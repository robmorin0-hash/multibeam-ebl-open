# How to build a Morin v5 multi-beam EBL tool

This is a quick-start for someone who wants to take this architecture from documents to a working machine. Reading time: 10 minutes. Implementation time: 18 months (Stage A) to 5 years (Stage D production).

---

## Phase 0 — Read

In this order, ~6 hours total:

1. `paper/Morin_2026_Multi-Beam_EBL_v5.pdf` — main architecture (20 pages)
2. `spec/v4_INTEGRATION.md` — cross-subsystem dependencies (5 min)
3. Skim each `spec/v4_*.md` — subsystem-by-subsystem (1–2 hr)
4. `spec/v4_stage_A_prototype.md` — what to build first (15 min)

---

## Phase 1 — Reproduce the simulations (1–2 days)

Verify the architecture's quantitative claims yourself before committing capital.

```bash
# Set up environment
python3 -m venv .venv
.venv/bin/pip install numpy scipy matplotlib

# Cross-beam Coulomb (Phase 1)
cd sim/phase1
.venv/bin/python phase1_analytic.py         # validation gate
.venv/bin/python phase1_stochastic.py       # full sweep

# Loeffler-Jansen (Phase 2)
cd ../phase2
.venv/bin/python phase2_jansen_v2.py        # Jansen formula + IMS calibration

# Cryo thermal, Meissner, wafer FEA, node-scale (Phase 3)
cd ../phase3
.venv/bin/python phase3_cryo_thermal.py
.venv/bin/python phase3_meissner.py
.venv/bin/python phase3_wafer_fea.py
.venv/bin/python phase3_node_scale.py
.venv/bin/python phase3_diagrams.py
```

Output: figures and CSV data in `sim/data/`. Confirm the published numbers reproduce within your environment.

If you want to explore parameter sensitivity, modify the operating point at the top of each script (per-beam current, drift distance, pitch) and re-run.

---

## Phase 2 — Stage A prototype (18 months, $600 k)

Read `spec/v4_stage_A_prototype.md` for the full BOM and test plan. Highlights:

**Hardware** (off-the-shelf except YBCO coil):
- FEI/Thermo Fisher 50 kV cold-field-emitter electron gun
- Single YBCO Helmholtz coil pair on silicon substrate (patterned at SuperPower or university clean room)
- Single YBCO Meissner shield
- Single cryo-CMOS 16-bit DAC engineering sample (Imec or Fraunhofer IPMS)
- Cryomech PT-90 cryocooler in a 77 K cryostat (Janis or Montana Instruments)
- Standard 8" CF UHV chamber
- BSE detector + ZMI interferometer + X-Y piezo stage
- 50 kV Spellman HVPS
- FPGA + workstation

**Months 0-3**: procure, bake out, vendor qualify
**Months 3-9**: fabricate HTS coil, bring up cryo-CMOS DAC
**Months 9-15**: six-point test campaign (HTS kinematics, Meissner attenuation, DAC pipeline, registration loop, cryosorption, thermal sink)
**Months 15-18**: Stage A report → GO/REVISE/PIVOT decision

If you pass Stage A, you've de-risked the architecture's novel subsystems at single-beam scale.

---

## Phase 3 — Stage B/C/D scale-up ($45-60 M total NRE, 36-60 months)

Stage B: 16-64 beams, $5 M
Stage C: 10³-10⁴ beams, $10-15 M
Stage D: 10⁵-10⁶ beams production tool, $30-40 M
First production article cost: same as Stage D.

The architectural decisions are made; remaining work is process development (YBCO 20 μm patterning recipe, cryo-CMOS DAC NRE tape-out, MEMS CNT 10⁶ tip array scale-up), prototype build, integration test. Standard precision-instrument program.

---

## Phase 4 — Software stack (concurrent with hardware)

See `software/` for spec + runnable code skeletons. Three subsystems:

1. **GDS-II pattern compiler** (`software/v5_software_compiler.md`) — converts standard chip-design files to per-beam blanker schedule with 10× compression. Long-pole development item.
2. **Real-time control firmware** (`software/v5_software_firmware.md`) — 3-tier control loop on 1000 cryo-CMOS tile ASICs. SystemVerilog + cocotb + Vivado.
3. **Calibration database + operator OS** (`software/v5_software_operating_system.md`) — PostgreSQL + Next.js + SECS/GEM. Standard datacenter stack.

Total software development effort: ~3-5 engineer-years at the Stage A → Stage D scale.

---

## Funding model

Capital sources to consider, in order of accessibility:

- **Sovereign / national semiconductor programs**: Canada SIF, EU Chips Act, India SemiconIndia, UK GTAR, Australia DSI, NZ MBIE — most have ~$500 M–$5 B budgets, of which $50-200 M for a multi-tool program is feasible
- **Strategic-materials defense contracts**: this architecture is export-control-clean by design
- **Custom-ASIC startups**: ~$5-10 M for a Stage A pilot, scaling with revenue
- **Open-source consortium model**: multiple parties build complementary subsystems, share IP

Capital requirements:
- Stage A: $600 k → research lab budget
- Stage A→D total: $45-60 M → mid-sized strategic program
- Production fab (10-20 tools): $300-600 M → small national-fab budget vs $5-15 B for EUV

---

## Fork philosophy

If you modify this architecture, two strong recommendations:

1. **Keep the supply chain plural.** The whole point is that no single vendor can hold this architecture hostage. If your fork introduces a single-vendor critical path, you've lost the strategic value.
2. **Open-release your improvements.** This is a positive-sum game. A fork that improves YBCO patterning yield benefits every implementer; a fork that improves the cryo-CMOS DAC NRE cost benefits every implementer. The architecture compounds value when forks share back.

The license permits closed forks (CC BY 4.0 only requires attribution, not share-alike), but the architecture is most valuable as a public commons.

---

## Where to ask questions

- Email the author: robmorin0@gmail.com
- File issues at the upstream repository (TBD)
- Tag your fork @niki-nation-builders on whichever platform you publish on so we can index it
