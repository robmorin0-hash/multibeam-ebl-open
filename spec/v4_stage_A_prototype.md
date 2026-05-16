# Stage A prototype — minimum buildable v4 validator

*Stage A is the first physical hardware that validates the v4 architecture
end-to-end at the smallest practical scale (1–4 beams). Goal: prove the
cryogenic HTS deflection + cryo-CMOS DAC + photonic data path + BSE
registration loop on a single column, in one or two years, at $200–500 k
hardware cost. If Stage A passes, the architecture is de-risked enough to
fund Stage B (16–64 beams, ~\$5 M).*

## Configuration

- **1 electron beam** (FEI/Thermo Fisher single-tip cold-field-emitter electron gun, off-the-shelf, $50 k)
- **1 HTS deflection coil pair** (YBCO 2G coated conductor, planar Helmholtz spiral, ~5 mm coil length, 20 μm gap geometry for direct v4 lineage). Patterned at SuperPower or in-house with off-the-shelf 4″ YBCO tape ($10 k materials + $30 k patterning at university clean room)
- **1 YBCO Meissner shield** adjacent to the coil, with a calibrated test beam to verify field exclusion (the second tip of a dual-emitter Wehnelt assembly serves as the "neighbor" beam for crosstalk measurement)
- **1 cryo-CMOS 16-bit current DAC** (Imec or Fraunhofer IPMS engineering sample, ~\$10 k) at 77 K
- **1 optical fibre photonic link** from external pattern source to a single photodiode at 77 K (off-the-shelf datacenter SFP+ + cryo InP photodiode, ~\$5 k)
- **1 etched fiducial wafer** with cross/grating/vernier marks ($1 k)
- **BSE detector** mounted in the chamber for registration loop closure (El-Mul $30 k)
- **UHV chamber** ($60 k off-the-shelf 8″ CF, Pfeiffer/Lesker)
- **Cryomech PT-90 cryocooler** (single unit, no redundancy, ~\$30 k)
- **Cryostat** ($25 k Janis or Montana Instruments off-the-shelf 77 K UHV chamber)
- **Stage**: simple X-Y piezo stage with ZMI-class interferometric metrology (\$50 k, Zygo + Heidenhain)
- **HVPS**: 50 kV electron-gun supply (Spellman, ~\$10 k)
- **Control system**: FPGA + workstation ($20 k)

**Total Stage A cost: \$320–\$450 k**, well under the $500 k Stage A budget in v4 §7.

## Tests it validates (in order)

1. **HTS coil deflection kinematics at 77 K** — verify Eq. 2 (v4 §3.1) within 1 % linearity over the deflection-coil range. Settling time < 10 μs. AC loss spectrum 1 kHz – 100 kHz. **Closes the §3.1 + §3.5 open items.**

2. **Meissner shield attenuation at 20 μm distance** — switch the primary coil, measure deflection of an adjacent test beam through the Meissner-shielded gap. Target: ≥ 80 dB attenuation (lower bound from defect-limited HTS shield literature). **Closes the §3.5 crosstalk question with empirical data.**

3. **Cryo-CMOS DAC end-to-end** — drive the coil from an optical-fibre-delivered 16-bit pattern via cryo-CMOS DAC at 77 K, characterise INL/DNL, switching power, settling. **Closes the §3.6 in-column DAC question.**

4. **BSE registration loop closure** — scan the deflected beam over the fiducial wafer, close a feedback loop using BSE signal to correct deflection. Target: closed-loop tracking accuracy < 2 nm over 1 mm field. **Closes the §3.9 registration question (in single-beam form).**

5. **Cryosorption pump-down** — expose HSQ-coated test wafer, measure outgassing burst on a residual gas analyser, verify cryosorption captures > 50 % on first impact at 77 K. **Closes the §3.12 cryosorption claim.**

6. **Wafer chuck thermal transient** — apply a 250 mW (scaled-down) beam-deposition equivalent (laser if no second beam available) and verify chuck holds ±50 mK at the smaller area. **Validates the §3.10 thermal architecture at scaled flux.**

## Tests it does NOT validate

- **Cross-beam Coulomb at 10⁶ density** — Phase 1 sim is the validator; Stage A only has 1–2 beams.
- **Loeffler-Jansen at 10⁶ density** — same; Phase 2 sim (GPT/OPAL) is the validator.
- **Pattern-data path at 50 Tbps** — Stage A demos a single fibre channel; full aggregate scale only matters in Stage B+.
- **Tool-throughput / wafers-per-hour** — single-beam writes are not throughput-relevant; Stage C/D validates.

## Schedule estimate

- **Months 0–3**: parts procurement, chamber bake-out, Pugh-matrix vendor selection.
- **Months 3–9**: HTS coil fabrication and 77 K characterisation, cryo-CMOS DAC bring-up.
- **Months 9–15**: integrated test campaign 1–6 above. One test per ~month with parallelism.
- **Months 15–18**: Stage A report, Stage B funding decision, scale-up engineering for Stage B.

Total: **~18 months Stage A from authorisation**.

## Decision gates

After Stage A:

- **GO to Stage B** if all 6 tests pass within design margins. The v4 architecture is empirically validated at the single-beam level; scale-up has known engineering challenges but no unanswered physics.
- **REVISE v4 + repeat Stage A** if any test fails materially (e.g., Meissner shield attenuation < 30 dB, indicating defect-density problem; or DAC INL > 4 LSB indicating cryo-CMOS process issue). Each revision-and-repeat adds ~6 months.
- **PIVOT to alternative architecture** if a test reveals a fundamental physics problem (no current evidence for this, but listed for completeness).

## Bill of materials (BOM) — Stage A

| Item | Vendor | Unit cost | Quantity | Subtotal |
|---|---|---:|---:|---:|
| Electron gun + Wehnelt assembly | FEI/Thermo Fisher | \$50 k | 1 | \$50 k |
| YBCO 2G tape (4″) | SuperPower | \$10 k | 1 | \$10 k |
| Coil + shield patterning service | Univ. clean room or AMSC | \$30 k | 1 | \$30 k |
| Cryo-CMOS 16-bit DAC (eng sample) | Imec or Fraunhofer IPMS | \$10 k | 1 | \$10 k |
| Cryo InP photodiode | Hamamatsu | \$5 k | 1 | \$5 k |
| SFP+ datacenter optical TX | Cisco / Marvell | \$2 k | 1 | \$2 k |
| Single-mode fibre + UHV feedthrough | Corning + Accu-Glass | \$3 k | 1 | \$3 k |
| BSE detector | El-Mul | \$30 k | 1 | \$30 k |
| UHV chamber (8″ CF) | Pfeiffer / Lesker | \$60 k | 1 | \$60 k |
| Cryomech PT-90 cryocooler | Cryomech | \$30 k | 1 | \$30 k |
| 77 K cryostat | Janis or Montana Instr. | \$25 k | 1 | \$25 k |
| X-Y piezo stage | PI / Heidenhain | \$30 k | 1 | \$30 k |
| ZMI interferometer | Zygo | \$25 k | 1 | \$25 k |
| 50 kV HVPS | Spellman | \$10 k | 1 | \$10 k |
| FPGA + workstation | Xilinx + commodity | \$20 k | 1 | \$20 k |
| Etched fiducial wafer (custom) | Univ. clean room | \$1 k | 5 | \$5 k |
| HSQ resist (test exposures) | DuPont / Allresist | \$0.5 k | 2 | \$1 k |
| Vacuum infrastructure (pumps, valves) | Pfeiffer / Lesker | \$30 k | 1 | \$30 k |
| Integration labor (engineer × months) | — | \$15 k/mo | 18 | \$270 k |
| **Stage A total** | | | | **\$616 k** |

(Labor was not included in the upper-estimate \$450 k figure earlier — the hardware-only number is ~\$346 k. Realistic full-project Stage A is \$600–700 k including labor.)

## Stage A → B handoff

Stage A's deliverables to Stage B:

- Characterised HTS coil with known $J_c$, AC-loss spectrum, switching transfer function
- Characterised cryo-CMOS DAC with INL/DNL, power, lifetime
- BSE registration loop architecture (tested at single-beam, scales to 10³-of-10⁶ probe design at Stage B)
- Cryostat + cryocooler integration that scales to the 20 mm × 20 mm column footprint at Stage B
- Vendor relationships and supply-chain qualifications for all critical components
- Process recipes for YBCO 20 μm patterning (the long pole)

## Path forward

Stage A is a buildable, in-budget validation project. It de-risks the v4 architecture from "all subsystem specs check out on paper" to "demonstrated at single-beam scale". The remaining 24–36 month path to Stage D production tool is the normal engineering scale-up cycle for a precision-instrument program.

**The architecture is ready to begin Stage A construction now.** The bottleneck is funding ($600–700 k for hardware + 18 months of skilled engineering time), not architecture.
