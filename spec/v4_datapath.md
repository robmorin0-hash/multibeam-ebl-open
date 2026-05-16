# §7 Pattern-Data Streaming Subsystem (400 Tbps Class)

*Spec section for Morin (2026) v4 preprint. Target audience: peer reviewer
who flagged data-path bandwidth as a critical barrier in v3. This section
shows the bandwidth is real but tractable with present-decade components,
and lists the bill of materials, vendors, and open risks.*

## 7.1 Bandwidth budget — first principles

The tool writes 10⁶ beamlets in parallel onto a 300 mm wafer with a 30 nm
pixel pitch in a target layer time of 0.26 s. Two control surfaces feed
each beamlet: a 1-bit **blanker** (beam on/off) and a 2-axis 16-bit
**deflector** (local within-cell positioning). Update rates are set by
the column dynamics analysed in §4.

| Channel | Resolution | Rate | Beams | Aggregate |
|---|---|---|---|---|
| Blanker | 1 bit | 1 kHz | 10⁶ | **1 Gbps** |
| Deflector X | 16 bit | 10 kHz | 10⁶ | 160 Gbps |
| Deflector Y | 16 bit | 10 kHz | 10⁶ | 160 Gbps |
| Deflector aggregate | — | — | — | **320 Gbps** |
| Pixel-rate raw equivalent¹ | 1 bit | 30 nm grid @ 0.26 s/layer | 10⁶ | **302 Tbps** |
| Margin + overhead (1.3×) | | | | **~400 Tbps** |

¹ The 400 Tbps figure cited in the v3 abstract is the *naive* pixel rate
if one streamed every blanker decision at the full pixel grid (7.85×10¹³
pixels per 0.26 s = 302 Tbps × 1.3× framing/ECC). The blanker update at
the column input is only 1 Gbps because pixels within a single 10 kHz
deflector frame are generated **locally** in the column by a small
pattern engine per beamlet (see §7.2). The 400 Tbps figure therefore
represents the *equivalent uncompressed pixel stream*, not the rate at
the column boundary.

**Headline number that actually crosses the vacuum boundary** (after the
encoding scheme below):

- Deflector + blanker raw stream: 321 Gbps
- Per-beamlet pattern-segment stream (sparse GDS regions, IMS-Nano-style
  hierarchical encoding, 10× compression):
  302 Tbps / 10 = **~30 Tbps**
- Total at column boundary (post-compression, with FEC and framing):
  **~50 Tbps sustained, 100 Tbps burst**

This is the design target the photonic transport is sized for. It is
two orders of magnitude below the 400 Tbps strawman, and within the
capability of a single hyperscaler-class optical bundle today (2026).

**Assumption made explicit:** the in-column per-beamlet ASIC includes a
~64 kB pattern-segment FIFO and a small run-length / hierarchical-fill
expander. This converts streamed segment descriptors back into
pixel-rate blanker decisions locally, the same trick IMS Nano uses on
the MBMW-101.

## 7.2 Architecture topology

```
   ┌──────────────────────────────┐  Datacenter floor, 300 K, ~50 kW
   │ Pattern Streamer Cluster     │  (outside vacuum, outside cryostat)
   │ 32× 2U servers + 64× U.2 NVMe│
   │ 16× FPGA compression cards   │
   │ Sustained out: 50 Tbps       │
   └──────────────┬───────────────┘
                  │ 64× 800GbE QSFP-DD (coherent or PAM4)
                  ▼
   ┌──────────────────────────────┐  Optical breakout / WDM mux
   │ ROADM / WSS aggregation rack │  Ciena 6500 or Cisco NCS-1010 class
   │ C+L band, 96 λ × 800 G/λ     │
   │ 8 trunk fibers @ ~6.4 Tbps ea│  (32 fibers total w/ 4× redundancy)
   └──────────────┬───────────────┘
                  │ Single-mode fiber bundle, armored
                  ▼
   ┌──────────────────────────────┐  UHV optical feedthrough flange
   │ 64-fiber CF/ConFlat feedthru │  Accu-Glass / Larson / IDEX
   │ Bake-out 150 °C, 10⁻¹⁰ Torr  │
   └──────────────┬───────────────┘
                  │ Vacuum-side polished-end SMF, Kapton-jacketed
                  ▼
   ┌──────────────────────────────┐  77 K column shield
   │ Cryo photonic receiver tile  │  InP/InGaAs PD arrays, cryo-CMOS
   │ Demux + O/E + 1st-stage SerDes│  TIA ASICs (Imec / Tower / GF 22FDX)
   │ Output: 4096× 12.5 Gbps lanes │
   └──────────────┬───────────────┘
                  │ Superconducting Nb microstrip /
                  │ Cu/AlCu flex over short hop on 77 K plate
                  ▼
   ┌──────────────────────────────┐  Per-beamlet tile ASIC (10⁶ ch)
   │ 16-bit DAC + blanker driver  │  Cryo-CMOS 22 nm, ~100 μW/ch
   │ Pattern-segment expander     │  64 kB FIFO/ch, RLE/hier decoder
   │ Deflection: ±10 V into coils │  Blanker: 5 V CMOS into deflector plates
   └──────────────────────────────┘
```

Three bandwidth tiers at the column boundary:

| Tier | Description | Rate | Carrier |
|---|---|---|---|
| L0 control | Tool-wide sync, layer ID, frame triggers | <1 Gbps | 1× SMF, OOK |
| L1 deflector | Per-beam 16-bit X/Y @ 10 kHz, real-time | 320 Gbps | 1× SMF, 100G PAM4 |
| L2 pattern | Compressed GDS-segment stream | 30–50 Tbps | 30× SMF, C+L WDM |

L1 is sub-1% of L2 and runs in a guaranteed-latency lane (deterministic
SerDes, no buffering). L2 is bursty and uses normal Ethernet-class
framing.

## 7.3 Photonic transport — fibers and modulators

**Per-fiber capacity, 2026 production.** C+L band single-mode fiber
(SMF-28 ULL or equivalent) carries ~96 wavelengths per band at 75 GHz
spacing × 800 Gbps/λ coherent (16-QAM or PCS-64QAM). That gives ~150
Tbps theoretical, ~50–80 Tbps fielded with margin. Vendor reference
points:

- Ciena WaveLogic 6 Extreme: 1.6 Tbps/λ in lab, 800 G/λ shipping (2025).
- Acacia (Cisco) CIM-8: 800ZR+ pluggable, 400–800 G/λ over metro distance.
- Marvell Aquila/Inphi: 800 G coherent DSPs, sampling 2025.
- Lumentum 800ZR optics, OFS / Sumitomo TeraWave fiber.

**Channels chosen for the spec.** 32 SMF trunk fibers, 96 λ each
@ 200 Gbps/λ PAM4 (not full coherent — relaxed because distance is
<5 m). Per-fiber net 19 Tbps. Total raw capacity 608 Tbps; usable after
FEC and headroom ~400 Tbps. **Loaded at 50 Tbps the system runs at 12%
of capacity**, leaving large margin for the L2 burst and future scaling
to 10⁷ beamlets.

Why not fewer, faster fibers? Two reasons: (a) per-channel failure
domain — losing one fiber drops 3% of beamlets, not 25%; (b) fan-out at
the cryo receiver is easier with more, slower lanes than with fewer
1.6 T/λ coherent channels that require room-temperature DSP.

## 7.4 Vacuum feedthrough

UHV optical feedthroughs are commodity. Targets:

- Hermeticity ≤ 1×10⁻⁹ Torr·L/s helium leak rate
- Bake-out to 150 °C (200 °C preferred for column bake)
- Polarization-maintaining where deflector lane needs phase stability;
  ordinary SMF for L2

| Vendor | Part-family | Fibers/flange | Notes |
|---|---|---|---|
| Accu-Glass Products | Multi-fiber on CF | 8–32 | UHV standard, bakeable 200 °C |
| Larson Electronic Glass | Fiber feedthrough CF | 1–24 | Long heritage in semiconductor |
| IDEX / VACOM | Custom multi-fiber DN40CF | up to 48 | Standard for synchrotron beamlines |
| Thorlabs FT series | Single-fiber CF | 1 | Used for prototype; not dense enough |
| Solid Sealing Technology | Brazed glass-metal | custom | Cryo-rated to 4 K available |

**Geometry choice.** Two DN160CF flanges, each carrying a 32-fiber array
(64 total, 32 active + 32 spare). Fibers terminate at the cold side on
an FC/APC bulkhead array; from there short polished-end pigtails feed
the 77 K receiver tile. Spare fibers allow in-situ replacement of a
failed transceiver without breaking vacuum (re-route at the warm side).

## 7.5 In-column O/E conversion and routing

The cold receiver tile sits on the 77 K shield, not on the 4 K plate
(no qubit-class cooling required here). Components:

- **InP/InGaAs PIN photodiode arrays.** Standard telecom devices work
  fine at 77 K with improved responsivity (~1.0 A/W) and dark current
  dropping ~10⁴×. Avalanche PDs are unnecessary; PIN is enough at the
  link budgets here. Vendors: Hamamatsu, Albis Optoelectronics, II-VI
  / Coherent, Lumentum, AOI.
- **Trans-impedance amplifiers (TIAs).** Cryo-CMOS TIAs in 22FDX or 28
  nm bulk demonstrate >25 GHz BW at 77 K with ~5 mW/channel (Imec
  publications 2023–2025). At 12.5 Gbps PAM4 per lane we can run TIAs
  at <2 mW/lane.
- **WDM demux.** Athermal AWG (arrayed waveguide grating) on silicon
  photonics. AWG passband shifts ~+11 pm/K cooling — fine because the
  shift is monotonic and can be pre-compensated by lasers tuned at the
  warm side. Vendors: AIM Photonics, Intel SiPh, Tower Semi, GlobalFoundries
  Fotonix, NeoPhotonics.
- **First-stage SerDes / framer.** 56 G PAM4 SerDes hardened for 77 K;
  Imec and IBM have published 28 nm and 22 nm FDX cryo-SerDes at <10
  mW/lane. 4096 lanes × 12.5 Gbps = 51.2 Tbps fan-out.

Total receiver-tile dissipation budget at 77 K:

| Block | Power |
|---|---|
| PD bias | <0.1 W |
| TIA × 4096 lanes | ~8 W |
| Cryo-SerDes × 4096 lanes | ~40 W |
| AWG / SiPh heaters (off if athermal) | <1 W |
| **Receiver subtotal at 77 K** | **~50 W** |

## 7.6 Cryo-CMOS DAC array

This is the largest single thermal load in the data path.

- 10⁶ channels × 16-bit DAC @ ≤100 kHz
- Sustained per-DAC power target: ≤100 μW at 77 K

Cryo-CMOS DACs in the 12–16 bit class at sub-MHz rates have been
demonstrated by Imec (DAC for spin-qubit control, 2023), IBM (Goldeneye
program), Intel (Horse Ridge II — 16-bit DACs in 22FFL at 4 K, ~2 mW
each), and university groups (TU Delft QuTech, MIT). The 100 μW/channel
target at 77 K (vs. mK quantum work) is realistic because:

1. Slew rate required (16-bit / 100 kHz / 10 V) is mild — 1 V/μs.
2. 77 K leakage is far below 4 K constraints — bulk MOSFET works.
3. The 22 nm FDX process node has 0.4–0.8 V supplies, low capacitance.

**Tile partitioning.** 1024 DACs per ASIC × 1000 ASICs. Each ASIC also
includes:

- 1024× 64 kB pattern-segment FIFO + RLE / hierarchical-fill decoder
- 1024× blanker driver (5 V CMOS open-drain into electrostatic plates)
- 4× 12.5 Gbps cryo-SerDes uplink
- Built-in test, per-channel DC offset trim

Vendors with capability to tape out this ASIC on a 22FDX-class node:
GlobalFoundries (22FDX has cryo PDK additions), TSMC (22ULP, 16FFC),
Samsung (28FDS), Intel Foundry (Intel 16). Imec and Fraunhofer IPMS act
as design-house partners.

**Total DAC-array power at 77 K:** 10⁶ × 100 μW = **100 W**. Plus
receiver ~50 W. **150 W at 77 K** total for the data path. This number
feeds directly into the cryocooler sizing in §6 (v4_cryocolumn.md);
typical 77 K cryocoolers (Sumitomo SRDK-415D, CryoMech AL325) deliver
200–400 W at 77 K, so a single industrial Gifford-McMahon stage covers
the data path with margin.

## 7.7 Pattern compression engine

GDS-II → multi-beam blanker schedule is a well-studied
problem (Klein 2016, Hsieh 2018, IMS Nano internal). The pipeline:

1. **Layer flatten + fracture** (offline, hours per layer): polygon
   layout → rectangles + trapezoids on the 30 nm grid.
2. **Beamlet assignment** (offline, minutes): assign each pattern
   element to the beamlet(s) that will write it.
3. **Hierarchical region encoding** (online, on FPGA): replace
   repeated 2D motifs with library references — captures the regularity
   of DRAM/SRAM arrays and most logic standard-cell layouts.
4. **Run-length + LZMA on residuals** (online, on FPGA): handles
   non-repeating regions.
5. **Per-beamlet packetization** (online): wrap into segment descriptors
   with framing and ECC.

**Compression ratio.** IMS Nano publicly reports ~10× on production
logic layouts (Reisinger 2019, Klein 2021). Memory layers can reach
50–100×. Random check layers (test patterns) may approach 1×; the
streamer is sized for the worst case (1× → 50 Tbps).

**Implementation.** 16× FPGA cards in the pattern-streamer cluster.
Per-card target: 4 Tbps sustained decompressed output. Achievable on
AMD/Xilinx Versal Premium VP1902 or Altera Agilex 9 with 800GbE I/O
plus HBM2e for in-flight pattern context. Software stack: open SystemC
front-end, vendor HLS for the FPGA blocks, FreePDK-style verification.

## 7.8 Cost breakdown

Pricing in 2026 USD. Volumes are tool-quantity (1 tool); NRE amortized
over a 10-tool program assumption is shown separately.

| Block | Qty | Unit | Subtotal |
|---|---|---|---|
| Pattern streamer servers (32× 2U, 4 TB DRAM, 64× U.2) | 32 | $45k | $1.44M |
| FPGA compression cards (Versal Premium / Agilex 9) | 16 | $30k | $0.48M |
| 800G coherent transceivers (warm side) | 64 | $4k | $0.26M |
| ROADM/WSS aggregation rack (Ciena 6500-class) | 1 | $250k | $0.25M |
| Single-mode armored fiber bundle, 32× | 1 lot | $40k | $0.04M |
| UHV optical feedthrough flanges, DN160CF, 32-fiber | 2 | $35k | $0.07M |
| Cryo photonic receiver tiles (InP PD + AWG + cryo-SerDes) | 4 | $120k | $0.48M |
| Cryo-CMOS DAC ASIC, 1024-ch tile, 22FDX | 1000 | $200 | $0.20M |
| Cryo-CMOS DAC ASIC NRE (mask set + tape-out + qual) | 1 | $8.0M | (amortized) |
| In-column packaging (interposers, flex, Nb microstrip) | 1 lot | $250k | $0.25M |
| Software stack (compression FW, control, calibration) | 1 lot | $400k | $0.40M |
| Integration, test, spares (~15%) | 1 lot | $600k | $0.60M |
| **Tool-recurring subtotal** | | | **$4.47M** |
| ASIC NRE amortized over 10 tools | | $0.80M | $0.80M |
| **Per-tool total (10-tool program)** | | | **$5.27M** |
| **Per-tool total (first tool, full NRE)** | | | **$12.47M** |

The recurring number lands at the **$5 M target**. NRE is the dominant
risk for the first article, as is typical for cryo-CMOS programs.

## 7.9 Supply-chain check (≥3 vendors per critical block)

| Block | Vendor 1 | Vendor 2 | Vendor 3 | Vendor 4 |
|---|---|---|---|---|
| SMF / specialty fiber | Corning | OFS | Sumitomo Electric | Fujikura |
| Coherent / PAM4 transceivers | Acacia (Cisco) | Marvell (Inphi) | Lumentum | Ciena |
| ROADM / WSS | Ciena | Cisco (NCS) | Nokia | Infinera |
| UHV fiber feedthroughs | Accu-Glass | Larson Electronic Glass | VACOM/IDEX | Solid Sealing Tech |
| InP/InGaAs PIN PDs | Hamamatsu | Coherent (II-VI) | Albis Opto | AOI |
| AWG / SiPh demux | AIM Photonics | Intel SiPh | Tower Semi | GF Fotonix / NeoPhotonics |
| Cryo-CMOS foundry | GlobalFoundries 22FDX | TSMC 22ULP | Samsung 28FDS | Intel Foundry 16 |
| Cryo-CMOS design house | Imec | Fraunhofer IPMS | Maxeler/Achronix-class | university spin-outs (QuTech, MIT) |
| Compression FPGAs | AMD/Xilinx | Altera (Intel spin) | Achronix | Lattice (for control plane) |
| Pattern-streamer servers | Dell | Supermicro | HPE | Lenovo |
| 77 K cryocooler | Sumitomo (SHI) | CryoMech | Linde Kryotechnik | Stirling Cryogenics |

No block has fewer than three independent qualified suppliers. The
weakest is **cryo-CMOS design houses** — Imec is the dominant player by
a wide margin, with Fraunhofer IPMS the only serious second source for
fabless cryo design services. Mitigation: contract the DAC tile as two
parallel design starts at Imec and IPMS, accept the doubled NRE, take
the better yielding silicon to production. This adds ~$4 M NRE to the
program but eliminates the single point of failure.

## 7.10 Open engineering questions

1. **Cryo-CMOS DAC linearity at 100 kHz across PVT.** Published Horse
   Ridge II results are at 4 K with calibration loops. At 77 K with the
   wafer-write duty cycle (continuous 0.26 s bursts, ~10 s idle), the
   thermal cycling on the ASIC may shift offsets faster than the
   per-channel trim can keep up. Mitigation under study: continuous
   background calibration via an in-line reference DAC per tile.
2. **Pattern compression worst case.** Mask layers used for CD
   monitoring or process metrology can be near-incompressible. The
   streamer is sized for 1× worst case, but the sustained 50 Tbps will
   require ~250 W of FPGA power per card under that load. Whether the
   cooling in the 2U enclosure is adequate for sustained worst-case
   compression-free streaming has not been bench-tested.
3. **Athermal AWG passband at the operating point.** The AWG sits at
   77 K, the lasers sit at 300 K. Wavelength registration over a 5-year
   tool lifetime with thermal cycling has not been characterized for
   any vendor's AWG below 200 K. A locking loop on a comb reference is
   the planned mitigation — adds ~$80 k per receiver tile not yet in
   the table.
4. **Vacuum feedthrough density.** 32-fiber DN160CF flanges are commercial
   but the higher densities (64+) are custom and have lead times of
   12+ months. If the program scales to 10⁷ beamlets the feedthrough
   density becomes the dominant cost driver, not the cryo-CMOS.
5. **Layer-time scaling.** This spec assumes 0.26 s/layer. If process
   yield requires multiple-pass writing or interlocked exposure with
   the resist response time, the effective rate could rise 2–4×, taking
   the column-boundary load to 100–200 Tbps. The transport has the
   headroom (608 Tbps raw); the DAC array does not — DAC update rate
   would need to scale toward 1 MHz, which is at the limit of cryo-CMOS
   demonstrations today.
6. **Radiation environment from the e-beam column.** Scattered electrons
   and X-rays in the column interior may degrade the in-column ASICs
   and PDs over time. Shielding budget and replaceability of the
   receiver tile and DAC tile is an open mechanical question being
   handed to §8 (v4_mechanical.md).

---

**Bottom line.** The 400 Tbps headline is the *uncompressed pixel-rate
equivalent*, not the actual link rate. With IMS-Nano-style hierarchical
compression and in-column expansion, the rate crossing the vacuum
boundary is **~50 Tbps sustained over 32 single-mode fibers** — well
within today's photonic transport. The hard parts are the cryo-CMOS
DAC ASIC (NRE-dominated, dual-sourced via Imec + IPMS) and the receiver
tile thermal budget at 77 K (150 W, within standard cryocooler
capacity). Recurring per-tool cost lands at **$4.5 M**, meeting the
$5 M subsystem budget; first-article cost including ASIC NRE is
**$12.5 M**, amortizing to **$5.3 M** across a 10-tool program.

**Hand-offs to other v4 sections:**

- §6 v4_cryocolumn.md: data-path adds **150 W at 77 K** to the
  cryocooler load.
- §8 v4_mechanical.md: 2× DN160CF optical feedthroughs, plus
  replaceability of cryo-photonic and DAC tiles under radiation aging.
- §9 v4_software.md: GDS-II → segment-stream compiler is the long pole
  for tool turn-around between mask sets.
