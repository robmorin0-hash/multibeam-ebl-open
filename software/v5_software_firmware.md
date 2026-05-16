# §9 Real-Time Control Firmware Architecture (10⁶-channel, hard real-time)

*Spec section for Morin (2026) v5 preprint. Audience: peer reviewer who
flagged the v4 hand-off note in `v4_datapath.md` §7 ("§9 v4_software.md:
GDS-II → segment-stream compiler is the long pole for tool turn-around")
and asked how the firmware actually closes a 10⁶-channel control loop
in microseconds across a cold-warm boundary. This document specifies
the firmware that runs the deflection, blanker, registration, and
stage-coupling loops on the 1000 cryo-CMOS tile ASICs and the warm-side
supervisory controller. It does not re-specify the photonic transport
(v4_datapath.md §7) or the registration sensor stack
(v4_source_and_registration.md §B), both of which are taken as given.*

The pattern compiler (GDS-II → L2 segment stream) is its own beast and
is specified separately in `v5_pattern_compiler.md`. This document
covers only the on-the-wire, on-the-tile, and warm-side control plane.

---

## 9.1 Three-tier control hierarchy — what the firmware actually has to do

Carrying the multi-rate steering principle from v3 §2.3 and the
registration tiering of `v4_source_and_registration.md` §B.6, the v5
firmware closes three nested loops plus a registration trim:

| Loop | Rate | Channels | Quantity per update | What it controls |
|---|---:|---:|---|---|
| Inner — Lorentz deflection | 10–100 kHz | 10⁶ | 16-bit X/Y current setpoint per beam | Per-beam within-cell positioning |
| Middle — blanker + dose | 1 kHz | 10⁶ | 1-bit on/off + 4-bit greyscale per beam | Pixel ON/OFF + dose modulation |
| Outer — wafer stage | 1–10 Hz | 1 (6-DOF) | x, y, z, θ, φ, ψ | Coarse wafer positioning |
| Registration trim (overlay) | 100 Hz nominal | 10⁶ | 12-bit ±500 nm trim per beam, summed into inner loop | Drift correction, fiducial tracking |

Plus the data-path control plane (L0/L1/L2) from v4 §7. The four data
tiers from v4 §7.2 map directly to firmware concerns: L0 sync (clock,
frame, alarms), L1 deflector stream (320 Gbps), L2 pattern stream
(50 Tbps), and the implicit L3/L4 control planes added below.

---

## 9.2 Architecture layering

Five firmware layers, named L0–L4 to align with the v4 §7.2 photonic
tiers:

```
┌─────────────────────────────────────────────────────────────┐
│ L4 — Supervisory (warm side, x86 + Linux + Vivado runtime)  │
│   Tool start/stop, recipe load, alarm handler, telemetry    │
│   Open-source: Tango / EPICS frameworks; baseline Tango     │
└────────────────────────┬────────────────────────────────────┘
                         │ 10 GbE, gRPC + protobuf
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ L3 — Per-tile control (cold side, RISC-V MCU on each tile)  │
│   Inner-loop FSM, registration trim, blanker scheduler,     │
│   per-coil PI controller, fault handler, BIST sequencer     │
│   Open-source: Zephyr RTOS on Ibex / VexRiscv RV32IMC       │
└────────────────────────┬────────────────────────────────────┘
                         │ on-die fabric, AXI4-Stream
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ L2 — Pattern dispatch (per-channel decode, blanker FIFO)    │
│   RLE / hierarchical decoder per channel, 64 kB FIFO        │
│   Stage-Y position lookup, blanker schedule generator       │
│   Open-source HDL: Amaranth or Chisel, exported SystemVerilog│
└────────────────────────┬────────────────────────────────────┘
                         │ 12.5 Gbps cryo-SerDes per lane × 4
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ L1 — MAC (packet parsing, FEC, framing)                     │
│   64b/66b framing, RS-FEC (528,514) per JESD204C, deskew    │
│   Lane bonding, in-band timestamp extraction                │
│   Open-source HDL: corundum project pattern (RS-FEC IP)     │
└────────────────────────┬────────────────────────────────────┘
                         │ photonic L1 link
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ L0 — PHY (photonic, fiber-coupled SerDes, clock recovery)   │
│   Per-tile PLL locked to femtosecond master, CDR, slip      │
│   Vendor: cryo-SerDes hard IP from Imec / IBM (22FDX)       │
└─────────────────────────────────────────────────────────────┘
```

L0–L1 are hard-IP/RTL on the cryo-CMOS tile, identical to commodity
JESD204C / 100G PAM4 receivers but redesigned for 77 K. L2 is the
per-channel pattern decoder — distinct firmware per channel but
parametric, generated from a single Chisel/Amaranth source. L3 is the
per-tile supervisor written in C against Zephyr RTOS on the per-tile
RV32IMC core (Ibex preferred for footprint, VexRiscv if pipelined
performance becomes binding). L4 is the warm-side host stack.

The vertical boundaries between L0/L1/L2 are clocked-by-PLL,
no-RTOS, deterministic logic. The L2/L3 boundary is the only place
the firmware crosses from RTL to C. That boundary is a single AXI4-Lite
status/control register block plus a small message FIFO; the inner-loop
data path does **not** traverse the RISC-V core, which is reserved for
slower (≤ 100 Hz) supervisory work and fault handling.

---

## 9.3 Per-coil inner-loop FSM

The inner-loop FSM is instantiated 1024× per tile, generated from a
single parametric Chisel module. Each instance closes a current PI
loop on one Lorentz deflection coil.

**State machine.** Five states:

```
IDLE → ARM → ACQ → ACT → SETTLE → ACQ … (loop)
                ↑
             FAULT → BLANK_PERMANENT (one-way)
```

- **IDLE**: pre-run, DAC at zero, blanker forced ON (beam off).
- **ARM**: armed for next 10 μs frame; setpoint latched from L2 FIFO.
- **ACQ**: read back per-coil current via cryo-CMOS sense electrode
  (the 50 pA sense-electrode signal from `v4_source_and_registration.md`
  §A.2, here reused as a coil-current monitor through the same
  per-channel TIA/ADC ASIC). 14-bit ΣΔ sample, decimated to 12-bit
  at 100 kSps.
- **ACT**: compute new DAC code = setpoint + trim + PI correction;
  write DAC.
- **SETTLE**: hold DAC stable for ≥ 5 μs of the 10 μs frame for the
  beam optics to respond. If the cryo-CMOS DAC slew (1 V/μs at
  10 V full scale) overruns the frame, the state machine asserts
  `slew_warning` to the L3 supervisor.

**PI loop coefficients.** Per channel, stored in a 24-bit fixed-point
register pair (Kp, Ki) loaded from L3 at calibration time. Default Kp
= 0.25, Ki = 0.05 per the v4 §A.4 stability analysis. The integrator
is bounded to ±10% of full-scale DAC code to prevent windup during
fault states.

**Registration trim summing.** A second 12-bit DAC code is delivered
from the registration loop (§9.5) at 100 Hz and held in a per-channel
trim register; it is summed into the deflection setpoint in the analog
output stage of the coil-driver ASIC, exactly as described in
`v4_source_and_registration.md` §B.7. The trim DAC has its own range
(±500 nm at the wafer plane); the firmware does not re-quantize the
pattern DAC.

**Fault detection.** If sense-electrode current deviates from the
DAC-implied target by > 5% for ≥ 3 consecutive frames, the FSM
transitions to FAULT, which:

1. Asserts blanker permanently for that channel,
2. Drives the deflection DAC to the **stop-aperture corner** code
   (deflects the beam to a known graphite beam dump in the column
   bore — same mechanism the source-array used for hot-spare swap in
   v4 §B.11),
3. Raises an L3 interrupt with channel ID + frame-counter timestamp.

Once latched, FAULT can only be cleared by an L4 supervisory write
after lot-end recalibration.

---

## 9.4 Per-tile blanker scheduler

1024 blankers per tile × 1000 tiles = 10⁶ blankers. Per-blanker
update rate is 1 kHz nominal from the v4 §7.1 budget; the firmware
supports up to 16 kHz for 4-bit greyscale dose modulation (effective
16 sub-pulses per 1 kHz frame).

**Per-blanker FIFO.** 64 kB per channel, identical to the
pattern-segment FIFO from `v4_datapath.md` §7.6. The FIFO is filled
from the L2 dispatch path (decoded RLE/hierarchical-fill segments)
and drained by the blanker scheduler at the stage-synchronized rate.

**Stage-Y position synchronization.** The wafer stage moves
continuously in Y at typical speeds of 1–10 mm/s during a layer write
(per v3 §3 column-scan geometry). The ZMI interferometer (Zygo ZMI
class, 0.1 nm/Hz) broadcasts the current Y position on a dedicated
fan-out at 1 MHz (32-bit position counter, sub-nm units). Each tile's
blanker scheduler consumes this counter as a sync source: a blanker
event scheduled at Y = Y₀ + N·Δy fires when the stage Y-counter
matches the scheduled position within ±0.5 Δy / 2. This is the same
position-trigger trick used in raster-scan EBL tools today (NuFlare,
Vistec) but operated on every blanker independently.

**Drift compensation.** The scheduler maintains a per-channel
fractional-position accumulator. When the registration loop (§9.5)
updates a trim offset, the accumulator is corrected so that blanker
events shift smoothly rather than jumping discontinuously — a 1st-order
fractional-delay filter implemented in 4 multiply-accumulate
operations per blanker per trim update.

**Skew compensation across the tile.** The 4 cryo-SerDes lanes feeding
each tile are deskewed at L1 to ≤ 100 ps RMS using inline lane-marker
patterns (JESD204C deterministic latency feature). Per-channel skew
within a tile is calibrated once at column commissioning and stored
in a 1024-entry skew LUT.

---

## 9.5 Registration loop fusion

Three sensor streams fuse into a per-coil trim DAC offset at 100 Hz:

1. **BSE probes.** 10³ of the 10⁶ beams act as registration probes
   (v4 §B.5). Each probe scans a fiducial mark at 10 kHz rate; the
   BSE detector array (custom El-Mul / Hamamatsu cryo SiPM stack,
   v4 §B.9) returns a 14-bit signal per probe per scan. The L2/L3
   correlator computes a 1D Moiré position estimate (≤ 100
   multiply-accumulate ops per beam per scan, comfortable 100 MOPS
   for the full array). Output: per-probe X/Y position error in
   nanometres at 10 kHz.

2. **ZMI interferometer.** Zygo ZMI-class differential interferometer
   on the stage at 1 kHz, 0.1 nm/Hz precision. Provides absolute
   stage-frame anchor.

3. **Thermal model.** Per-column-subarray TEC (thermoelectric cooler)
   measurement at 1 Hz, providing column temperature with 0.001 K
   resolution. A pre-computed thermal expansion matrix maps
   ΔT per subarray to ΔX/ΔY drift at the wafer plane (~2 μm/K
   stage, ~0.24 nm/K column — v4 §B.8). Output: drift contribution
   per subarray at 1 Hz.

**Kalman fusion.** A 6-state Kalman filter per column subarray
(~10⁴ beams per subarray, 100 subarrays total). States: {Δx,
Δy, Δθ, Δscale, Δskew, Δfocus}. Measurement update from the BSE
probe stream at 10 kHz; ZMI at 1 kHz; thermal at 1 Hz. Process
noise tuned at commissioning per subarray.

The fused state is propagated to per-coil trim DAC offsets at 100 Hz
(matching the registration mid-loop tier from v4 §B.6). Per-beam trim
= subarray-Kalman-state evaluated at that beam's (x, y) wafer
coordinate, written to the trim DAC register described in §9.3.

The Kalman fusion is implemented on the warm-side L4 supervisor —
not on the cold-side RISC-V — because (a) full-array state is small
(100 subarrays × 6 states × 8 bytes = 4.8 kB), (b) algorithm
complexity warrants an x86 floating-point environment, (c) the
100 Hz update rate is comfortably handled by gRPC over the
control-plane link. The cold-side RISC-V receives only the resulting
per-beam trim DAC vector (10⁶ × 12 bits = 1.5 MB at 100 Hz =
1.2 Gbps, fits inside the L1 deflector stream sideband).

---

## 9.6 Latency budget

Reproducing the v4 §7 spec rigor: every link in the inner loop has
a budgeted latency. The total must close inside the 10 μs inner-loop
period with margin.

| Stage | Budget | Source | Margin |
|---|---:|---|---|
| Photonic L0/L1 receive → cryo-CMOS register | < 100 ns | Imec/IBM cryo-SerDes pubs (Ranucci 2024) | 50× |
| L1 MAC parse + FEC + lane align | < 200 ns | corundum-class FPGA RTL benchmarks | 3× |
| L2 pattern decode + dispatch to per-coil FIFO | < 500 ns | Custom Amaranth RLE decoder (sim'd) | 4× |
| L3 inner-loop FSM compute (PI + trim sum) | < 200 ns | 4-cycle pipeline @ 200 MHz tile clock | 5× |
| DAC update (16-bit cryo-CMOS DAC slew) | < 5 μs | Horse Ridge II, IBM Goldeneye scaled to 77 K | 2× |
| **Total inner loop close time** | **< 6 μs** | | **0.6 of 10 μs frame** |

The 4 μs frame slack absorbs (a) BSE-probe correlator updates
(§9.5), (b) blanker scheduler drift correction (§9.4), (c) L3 RTOS
interrupt handling for fault events. The DAC slew is the dominant
budget item — 50% of the inner-loop frame — and is the single
firmware lever that drives the cryo-CMOS DAC architecture choice
(slew-rate-enhanced segmented architecture, see §9.10 open
question 1).

For the 100 kHz inner-loop variant (deflection rate scaling for
multi-pass writing, v4 §7.10 open question 5), the budget collapses
to 6 μs out of 10 μs — still feasible but with zero margin for
fault recovery within the frame. The architecture's answer at that
point is to lower the L2 decode latency by enlarging the per-channel
FIFO from 64 kB to 256 kB and pre-staging more frames; cost is
roughly 4× per-tile SRAM area, increasing the cryo-CMOS DAC ASIC
die area by ~12% and the per-tile power at 77 K by ~5 W.

---

## 9.7 Synchronization architecture

The whole tool runs from a single master clock at the warm-side
photonic source: a femtosecond-stable oscillator (Menlo Systems
FC-1500 or equivalent OFC) divided down to the system base rate.
This is identical in topology to JESD204C deterministic latency
and to the LCLS / European-XFEL accelerator timing system.

**Clock distribution.** The master clock is encoded onto a dedicated
L0 photonic lane (1 Gbps NRZ, separate from L1/L2 traffic per v4
§7.2 Tier L0) and broadcast to every tile. Per-tile PLLs lock to
this reference with sub-100 ps jitter — a standard cryo-CMOS PLL
result from Imec.

**Frame sync.** Embedded JESD204C-style multi-frame markers every
4096 samples define the deterministic-latency boundary for the L1
deflector stream. The L1 MAC at each tile aligns to the frame
boundary and exposes a global frame counter to L2/L3.

**Stage-position counter.** The ZMI interferometer counter is
continuously broadcast at 1 MHz on a second L0 lane (32-bit position
in sub-nm units, every microsecond). Every tile receives this counter
and feeds it to the blanker scheduler. This is the single source of
truth for stage-Y position; per-channel local time bases derive from
it plus the master clock.

**Wafer-level timestamp.** Each blanker event and each fault report
carries a 64-bit wafer-time stamp (master-clock count since the
wafer load event). This timestamp is the absolute coordinate for
all logging and post-hoc forensics.

---

## 9.8 Hot redundancy and failure recovery

The architecture's response to dead beams was set in v3 §3 and v4
§B.11: hot-spare beams allocated at column-design time, faulted
beams permanently blanked and deflected to stop apertures.

**Per-tile health monitor.** A 1 kHz background task on the per-tile
RISC-V scans: (a) DAC offset trim drift versus calibration baseline,
(b) sense-electrode current statistics per channel, (c) L1 lane BER
from the FEC error counter, (d) tile junction temperature.
Out-of-spec channels are flagged to L4.

**Auto-disable failed coils.** As in §9.3 FAULT state. The channel
is permanently parked at the stop-aperture DAC code. The blanker is
held ON (beam off). The L4 supervisor reallocates pattern data away
from the dead channel to a designated hot-spare beam from the
spare pool (allocated at compile time per v3 §3 hot-spare budget,
typically 1–5%).

**Tile-level failure.** If a tile loses L1 lock or its junction
temperature exceeds the 100 K cryo budget, the entire tile is
declared failed and 1024 beams are routed to the spare pool. The
tool can continue at degraded throughput (one tile = 0.1% of beams)
until the next maintenance window.

**Catastrophic faults.** Operator alarms (audible + GUI) fire on:
≥ 10 tiles failed, master clock loss, ZMI interferometer loss,
cryocooler over-temperature, vacuum loss, photonic-link bit-error
rate above threshold. Each alarm has an associated containment
action (drive all blankers ON, retract stage, vent recovery
sequence). All alarm timestamps are logged to a write-once SSD
for incident forensics — same pattern as semiconductor litho tools
today.

---

## 9.9 FPGA / ASIC implementation choice

The 1000 cryo-CMOS tiles run all of L1, L2, and the data-path
portion of L3. Each tile is fabricated on 22FDX (GlobalFoundries
FD-SOI 22 nm, v4 §7.6 vendor selection) and includes:

- 1024 deflection-coil DAC channels (per-channel 16-bit DAC, sense
  ADC, PI controller, blanker driver, trim DAC, FIFO)
- 1× hardened cryo-CMOS PLL locked to the L0 master clock
- 4× 12.5 Gbps cryo-SerDes uplinks (L0/L1 transport)
- 1× RV32IMC RISC-V core (Ibex from lowRISC, MIT-licensed)
- 64 kB instruction SRAM + 256 kB data SRAM for the RISC-V
- 1× AXI4-Lite control register block exposing all per-channel
  status and config registers to the RISC-V

**Source generation.** All synthesizable RTL for L1/L2 and the
per-channel inner-loop is generated from a single parametric
Chisel project (Chisel 6, MIT-licensed). Amaranth is the fallback if
the team prefers Python — equivalent capability, slightly less
mature for cryo-targeted PDK macros. Either way, the output is
plain SystemVerilog consumed by the foundry P&R toolchain (Cadence
Innovus or Synopsys ICC2 — proprietary, supplied under the foundry
MPW/full-mask contract).

**Verification.** Cocotb (Python-based, BSD-licensed) for unit and
block-level simulation; Verilator (LGPL) as the simulation engine.
Full-tile sim runs nightly in CI. UVM-style sequences are emitted
from cocotb test classes for the proprietary signoff sim
(VCS or Xcelium) at tape-out signoff.

**Per-tile cost.** $200 per tile in volume from v4 §7.8, NRE
$8 M dual-sourced through Imec and Fraunhofer IPMS per v4 §7.9
mitigation strategy. The firmware does not change these numbers —
the RISC-V core (~50 k gates) and SRAMs (~2 mm² per tile) are
budgeted inside the existing 1024-channel ASIC layout.

---

## 9.10 Software toolchain summary

| Concern | Tool | License | Notes |
|---|---|---|---|
| HDL source | Chisel 6 (Scala) | MIT | Primary; Amaranth as fallback |
| HDL emission | FIRRTL / SFC → SystemVerilog | Apache 2 | |
| Simulation | Verilator + cocotb | LGPL / BSD | Open, fast, CI-friendly |
| Linting | Verible | Apache 2 | Google-maintained |
| Formal | SymbiYosys | MIT | Open-source formal flow |
| FPGA build (validation) | Vivado 2024.x | Proprietary (free for AMD parts) | For pre-tape-out FPGA emulation on VCU128 |
| FPGA build (open path) | SymbiFlow / F4PGA | ISC | For Lattice ECP5 control-plane prototypes |
| ASIC P&R | Cadence Innovus or Synopsys ICC2 | Proprietary (foundry contract) | OpenROAD evaluated but 22FDX PDK not open |
| RISC-V toolchain | GCC + Newlib + LLVM | GPL / Apache 2 / BSD | Standard riscv-gnu-toolchain |
| Embedded RTOS | Zephyr 4.x | Apache 2 | Primary; FreeRTOS as fallback |
| Host control plane | Tango Controls | LGPL | EPICS as alternative |
| Network framing | gRPC + protobuf | Apache 2 / BSD | 10 GbE between L4 and edge |
| CI | GitHub Actions + cocotb-test | MIT | Reproducible Docker builds |

The choice of Zephyr over FreeRTOS is driven by: (a) better RISC-V
support upstream, (b) device-tree-driven configuration matching the
per-tile parametric build, (c) Apache-2 license aligns with the
Chisel front-end, (d) larger community for long-term maintenance.
FreeRTOS remains the fallback if a critical Zephyr regression hits
the cryo-MCU port — the inner-loop FSM does not depend on the RTOS
because the FSM lives in RTL, not C.

Vivado is preferred for FPGA validation builds because the
pre-tape-out emulation platform is a VCU128 (Versal Premium) which
SymbiFlow does not target. SymbiFlow / F4PGA is the open path for
the Lattice ECP5-based control-plane prototypes (warm-side L4 edge
nodes), where being able to ship a fully open bitstream matters for
the open-source release goals of §9.13.

---

## 9.11 Buildable code skeletons

**Per-coil inner-loop testbench (cocotb, Python, ~45 lines).**

```python
# tests/test_inner_loop_pi.py — cocotb testbench for InnerLoopFSM
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer
import random

@cocotb.test()
async def test_pi_settling(dut):
    """Apply step setpoint, verify PI loop settles within 5 frames."""
    cocotb.start_soon(Clock(dut.clk, 5, units="ns").start())  # 200 MHz
    dut.rst.value = 1
    await Timer(100, units="ns")
    dut.rst.value = 0
    dut.kp.value = 0x400000  # 0.25 in Q24
    dut.ki.value = 0x0CCCCC  # 0.05 in Q24
    dut.trim_dac.value = 0
    setpoint = 0x4000  # mid-scale 16-bit target
    dut.setpoint.value = setpoint
    # plant model: 1st-order, tau = 2 μs, fed back via sense_adc
    sense = 0
    for frame in range(8):
        await RisingEdge(dut.frame_strobe)  # 100 kHz frame tick
        dac = int(dut.dac_out.value)
        sense += (dac - sense) >> 2  # crude lag
        dut.sense_adc.value = sense
        cocotb.log.info(f"frame={frame} dac=0x{dac:04x} sense=0x{sense:04x}")
    assert abs(sense - setpoint) < (setpoint >> 6), \
        f"PI loop failed to settle within 5/64 of setpoint: {sense} vs {setpoint}"

@cocotb.test()
async def test_fault_latches(dut):
    """Inject sense/DAC mismatch for 3 frames, verify FAULT + blanker latch."""
    cocotb.start_soon(Clock(dut.clk, 5, units="ns").start())
    dut.rst.value = 1
    await Timer(100, units="ns")
    dut.rst.value = 0
    dut.setpoint.value = 0x8000
    dut.sense_adc.value = 0x0000  # huge mismatch
    for _ in range(5):
        await RisingEdge(dut.frame_strobe)
    assert dut.fault_latched.value == 1
    assert dut.blanker_out.value == 1  # beam off
    assert int(dut.dac_out.value) == 0xFFFF  # stop-aperture corner code
```

**Inner-loop FSM skeleton (SystemVerilog, ~45 lines).**

```systemverilog
// rtl/inner_loop_fsm.sv — per-coil inner-loop FSM, generated from Chisel
// 200 MHz tile clock, 100 kHz frame strobe, 16-bit DAC out
module inner_loop_fsm #(
    parameter int DAC_W   = 16,
    parameter int SENSE_W = 14,
    parameter int TRIM_W  = 12
) (
    input  logic                 clk, rst, frame_strobe,
    input  logic [DAC_W-1:0]     setpoint,
    input  logic signed [TRIM_W-1:0] trim_dac,
    input  logic [SENSE_W-1:0]   sense_adc,
    input  logic signed [23:0]   kp, ki,           // Q24 fixed-point
    output logic [DAC_W-1:0]     dac_out,
    output logic                 blanker_out,
    output logic                 fault_latched,
    output logic                 slew_warning
);
    typedef enum logic [2:0] {IDLE, ARM, ACQ, ACT, SETTLE, FAULT} state_t;
    state_t state, next_state;
    logic signed [DAC_W:0] err;
    logic signed [31:0]    integ;
    logic [3:0]            fault_cnt;

    always_ff @(posedge clk or posedge rst) begin
        if (rst) begin
            state <= IDLE; integ <= 0; fault_cnt <= 0;
            dac_out <= 0; blanker_out <= 1; fault_latched <= 0;
        end else begin
            state <= next_state;
            if (state == ACT) begin
                err     <= $signed({1'b0, setpoint}) - $signed({1'b0, sense_adc, 2'b00});
                integ   <= integ + ((ki * err) >>> 24);
                dac_out <= setpoint + ((kp * err) >>> 24) + integ[15:0] + trim_dac;
            end
            if (state == ACQ && (err > (setpoint >> 4))) fault_cnt <= fault_cnt + 1;
            else if (state == ACQ)                       fault_cnt <= 0;
            if (fault_cnt >= 3) begin
                fault_latched <= 1; blanker_out <= 1; dac_out <= '1; // stop aperture
            end
        end
    end

    always_comb begin
        unique case (state)
            IDLE:    next_state = frame_strobe ? ARM    : IDLE;
            ARM:     next_state = ACQ;
            ACQ:     next_state = ACT;
            ACT:     next_state = SETTLE;
            SETTLE:  next_state = frame_strobe ? ARM    : SETTLE;
            FAULT:   next_state = FAULT;
            default: next_state = IDLE;
        endcase
        if (fault_latched) next_state = FAULT;
    end

    assign slew_warning = (state == SETTLE) && (|err[DAC_W:8]);
endmodule
```

The Chisel source for this module is ~120 lines and parametrically
generates the 1024-instance array per tile. Cocotb tests run against
the SystemVerilog emission in Verilator; signoff sim runs in VCS
under the foundry contract.

---

## 9.12 Open-source release

**Repository.** `multibeam-ebl-firmware/` published at
github.com/morin-ebl/firmware on the v5 publication date.

```
multibeam-ebl-firmware/
├── README.md
├── LICENSE-MIT                     # code
├── LICENSE-LGPL                    # for any LGPL-derived components
├── docs/
│   └── v5_software_firmware.md     # this document
├── hw/
│   ├── chisel/                     # parametric Chisel sources
│   ├── amaranth/                   # Amaranth fallback prototypes
│   └── sv/                         # emitted SystemVerilog (artifact)
├── sw/
│   ├── tile_mcu/                   # Zephyr application for RV32IMC
│   ├── host/                       # warm-side Tango device server
│   └── kalman/                     # registration fusion (Python + C)
├── tests/
│   ├── cocotb/                     # block-level testbenches
│   └── system/                     # full-tile co-sim
├── ci/
│   ├── github-actions/             # cocotb sim, lint, formal
│   └── docker/                     # reproducible build image
├── nix/                            # Nix flake for fully-pinned builds
└── tools/                          # vendor wrappers (Vivado, Innovus)
```

**License split.** MIT for original code (HDL, Zephyr app, host
stack, tests). LGPL only where derived from LGPL upstreams
(Tango Controls device server, Verilator-derived utilities). All
vendor IP (Cadence, Synopsys, Xilinx) stays out of the public repo;
the foundry-PDK wrapper layer is stubbed with open BSD-licensed
behavioral models for CI sim, and the proprietary cells are
loaded from a separately-licensed `proprietary/` submodule that
ships only to consortium members.

**CI.** GitHub Actions matrix: (Verilator + cocotb), (Verible
lint), (SymbiYosys formal property checks). Nightly cron runs
full-tile co-sim against a Linux-host pattern-stream replay. PR
CI runs only block-level tests for sub-5-minute turnaround.

**Reproducible builds.** Nix flake pins every tool version including
Verilator, Chisel, cocotb, riscv-gnu-toolchain. Docker image is
generated from the same Nix expression for users who do not want
to install Nix. Vivado and the proprietary EDA tools are referenced
by exact version in the lock file but are not redistributed — users
supply their own licensed install.

---

## 9.13 Open engineering questions for v5.1+

1. **Cryo-CMOS DAC slew at 100 kHz across PVT.** v4 §7.10 question 1
   covers calibration drift. The firmware-side question is whether
   the segmented DAC architecture chosen for slew (top 6 MSB binary
   + bottom 10 LSB ladder) holds linearity across the 5 μs slew
   budget at 77 K. Bench data from Imec's 2025 cryo-DAC tape-out is
   needed to close this. If linearity degrades > 1 LSB during slew,
   the firmware mitigation is to pre-distort the DAC code in L2 —
   doable but adds ~50 ns to the L2 decode latency budget.

2. **Redundancy strategy at 10⁶-coil scale.** The hot-spare allocation
   is set at compile time (§9.8), but the optimal spare fraction
   versus tool throughput is open. 1% spare = 10⁴ unused beams =
   ~1% throughput hit but tolerates 1% beam failure; 5% spare
   tolerates 5% failure at 5% throughput cost. The right number
   depends on the steady-state per-tip failure rate (v4 §B.11
   question 1) which has no published data at 10⁶-tip array scale.

3. **RTOS selection — Zephyr vs FreeRTOS.** Settled at Zephyr above
   on five rationales, but the cryo-MCU port has not been
   bench-validated. Open question: does Zephyr's tickless idle
   work correctly when the RV32IMC core's clock tree is gated by
   the cryo-CMOS PLL during low-activity windows? FreeRTOS's
   simpler scheduler may be more robust to PLL gating artifacts.
   A 1-month bench characterization on a VCU128 emulator with
   cryo-trimmed clock margins is the proposed test.

4. **Kalman filter divergence under sensor dropout.** If the ZMI
   interferometer drops out (mechanical bump, fiber breakage), the
   100 Hz Kalman update reverts to BSE-only mode. Open: does the
   filter remain stable, or does it drift? Standard accelerator-physics
   answer is "use a particle filter with re-initialization on
   sensor return" — open whether the 100 Hz / 100 subarray
   computational budget can sustain that complexity on the warm-side
   x86 supervisor.

5. **Pre-tape-out emulation fidelity.** The VCU128 Versal Premium
   emulator can fit ~1 tile (1024 channels). Open: do the inner-loop
   timing characteristics measured on warm-silicon Versal at room
   temperature predict the cryo-CMOS 22FDX behavior at 77 K? Imec
   has cryo-validated process models but the FPGA emulator does
   not run on cryo silicon. Mitigation: bench the first MPW tile
   at 77 K against the emulator predictions; iterate the model.

6. **Stage-position counter dropout handling.** The ZMI counter
   broadcast at 1 MHz is single-fiber, single-source. If the L0
   sync lane drops, every tile loses stage-Y sync within one frame.
   Open: should the firmware ride out short dropouts on a per-tile
   local oscillator (10 ns Allan-variance over 1 ms) or
   immediately blank all beams? Operationally, blanking is safer;
   but the cost of frequent re-acquisition during marginal-link
   conditions has not been characterized.

7. **L4 supervisor latency budget under fault storm.** A correlated
   fault (e.g., cryocooler glitch) can fire 10⁴ FAULT interrupts
   simultaneously. The warm-side x86 + Tango stack must process
   the storm without dropping any. Open: is gRPC + protobuf the
   right framing under that load, or should the high-rate fault
   channel use a dedicated low-overhead binary protocol (e.g., raw
   AF_XDP socket)?

8. **Reproducibility of foundry P&R.** Vivado, Innovus, and ICC2
   are proprietary and version-locked to the foundry MPW contract.
   Open: is there a path to a fully-open ASIC flow (OpenROAD + the
   open SKY130/GF180 PDKs) for a derivative chip at a coarser
   node — e.g., the warm-side L4 edge-node FPGA replacement —
   to allow fully open-source bitstreams in the v5.1 release?

---

**Bottom line.** The 10⁶-channel hard real-time control loop closes
in 6 μs out of a 10 μs frame using a layered L0–L4 firmware stack
in which the deterministic data path (L0–L2) lives in RTL on the
cryo-CMOS tile ASICs and the supervisory work (L3 fault handling,
L4 Kalman fusion + recipe + alarms) lives in software on a per-tile
RISC-V and a warm-side x86 host. The per-tile cryo-CMOS ASIC adds
a small RV32IMC + 320 kB SRAM to the existing 1024-channel DAC tile
without changing the area, NRE, or power numbers from `v4_datapath.md`
§7.6. The firmware toolchain is open-source-first (Chisel + Amaranth
+ cocotb + Zephyr + Tango + Nix) with proprietary tools (Vivado,
Innovus, ICC2) confined to vendor-supplied environments and isolated
behind stable interface contracts. The full firmware source is
released under MIT + LGPL at v5 publication, with reproducible
builds via Nix flake and CI-validated cocotb regressions on every
PR.

**Hand-offs to other v5 sections:**

- §7 `v4_datapath.md` (carried forward): firmware does **not** change
  the 150 W cryo budget, the ASIC area, or the photonic transport
  sizing. The RISC-V + SRAM additions fit inside the existing tile
  budget.
- §8 `v5_pattern_compiler.md` (separate document, in progress):
  L2 segment-stream encoding and L4 recipe format are owned by the
  compiler doc; this firmware spec consumes them but does not
  define them.
- §10 `v5_qualification.md` (planned): the firmware regression suite
  (cocotb + Verilator + nightly co-sim) is the qualification
  baseline for any ASIC respin.
