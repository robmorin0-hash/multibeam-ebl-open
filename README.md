# Multi-Beam Direct-Write Electron Lithography — Open Architecture v5

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20247262.svg)](https://doi.org/10.5281/zenodo.20247262)
[![License: CC BY 4.0](https://img.shields.io/badge/License%20(papers)-CC%20BY%204.0-lightgrey.svg)](https://creativecommons.org/licenses/by/4.0/)
[![License: MIT](https://img.shields.io/badge/License%20(code)-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**An open, mask-free, multi-vendor architecture for mature-node semiconductor manufacturing — published, simulated, and software-defined.**

Release: **v5 (May 16, 2026)** — final integrated open-source release with full software stack (GDS-II pattern compiler, real-time control firmware, tool operating system) layered on top of the v4.1 hardware engineering.

Author: Robert Gerald Morin (NÎKI Nation Builders, Edmonton AB, Canada)
ORCID: [0009-0008-8373-1496](https://orcid.org/0009-0008-8373-1496)
Correspondence: robmorin0@gmail.com
License: papers under CC BY 4.0 · code under MIT (see `LICENSE.papers`, `LICENSE.code`)

## How to cite

> Morin, R. G. (2026). *Multi-Beam Direct-Write Electron Lithography via Multi-Rate Electromagnetic Steering — v5 Open Architecture Release.* Zenodo. https://doi.org/10.5281/zenodo.20247262

BibTeX:
```bibtex
@software{morin_2026_multibeam_ebl,
  author       = {Morin, Robert Gerald},
  title        = {{Multi-Beam Direct-Write Electron Lithography
                   via Multi-Rate Electromagnetic Steering —
                   v5 Open Architecture Release}},
  month        = may,
  year         = 2026,
  publisher    = {Zenodo},
  version      = {v5.0},
  doi          = {10.5281/zenodo.20247262},
  url          = {https://doi.org/10.5281/zenodo.20247262}
}
```

---

## What this is

A complete open-source design package for a multi-beam direct-write electron-beam lithography (EBL) machine. It targets **mature-node semiconductor manufacturing (50–180 nm range)** at roughly **10× lower capital cost than EUV** (~$37 M per tool vs $200–400 M), with **no single-vendor architectural dependency**.

The architecture is released under CC BY 4.0 (papers) + MIT (code). The author makes no patent claim on anything in this package. By publication, the entire design enters the public domain as prior art and may not be enclosed by subsequent IP filings by any party.

If you want to build this machine — or fork the architecture, or extract subsystems for adjacent applications — this package gives you everything needed up to the Stage A prototype build.

## What's in the box

### `paper/` — the published preprint
- `Morin_2026_Multi-Beam_EBL_v5.pdf` — the integrated preprint (latest version)
- `Morin_2026_Multi-Beam_EBL_v5.tex/md` — LaTeX and Markdown sources
- `figures/` — all 10+ figures (cross-beam Coulomb, Loeffler–Jansen, cryo thermal, Meissner shield, node-scale curve, wafer FEA, system block diagram, photonic data path)

### `sim/` — verification simulations
All quantitative claims in the paper are simulated and the code is included. Anyone can run these to reproduce the published numbers, or modify them for their own architecture variants.

- `phase1/` — Cross-beam Coulomb perturbation (Phase 1 line-charge sim)
- `phase2/` — Loeffler–Jansen intra-beam blur (Jansen analytical + N-body MC)
- `phase3/` — Cryo column thermal network, Meissner shield attenuation, wafer chuck FEA, node-scale curve
- `data/` — CSV outputs, run logs

Run any sim with:
```bash
cd sim/phase1
python3 phase1_analytic.py
```

### `spec/` — subsystem engineering specifications
12 buildable engineering specifications, each with:
- Component selection + vendor candidates (≥3 vendors / ≥2 jurisdictions per subsystem)
- Cost estimates
- Open engineering questions

- Hardware: `v4_cryocolumn.md`, `v4_datapath.md`, `v4_blanker.md`, `v4_wafer_thermal.md`, `v4_resist_outgassing.md`, `v4_source_and_registration.md`, `v4_cold_warm_interface.md`, `v4_loeffler_jansen.md`
- Software: `v5_software_compiler.md`, `v5_software_firmware.md`, `v5_software_operating_system.md`
- Integration: `v4_INTEGRATION.md`, `v4_phase3_findings.md`
- Prototype path: `v4_stage_A_prototype.md`

### `xray_fork/` — architectural variant for X-ray lithography
A sketch of how the same architectural principles apply to X-ray lithography (using an electron-beam-pumped X-ray converter array). Coarser node range (130–250 nm) than the EBL primary, but useful for thick-resist and photon-sensitive substrate applications.

### `software/` — runnable code

Reference implementations and code skeletons for the v5 software stack. **These are starting points**, not production-ready code — but they're enough that a competent team can build out from them.

## How to use this package

### If you want to read the architecture
Start with `paper/Morin_2026_Multi-Beam_EBL_v5.pdf`. ~20 pages, includes all the key numbers and figures.

### If you want to build the architecture
1. Read the paper (architecture overview)
2. Read `spec/v4_INTEGRATION.md` (cross-subsystem dependencies)
3. Read each `spec/v4_*.md` (subsystem-by-subsystem detail)
4. Read `spec/v4_stage_A_prototype.md` (smallest physical validator at $600 k / 18 months)

### If you want to reproduce or extend the simulations
1. Set up Python environment: `python3 -m venv .venv && .venv/bin/pip install numpy scipy matplotlib`
2. `cd sim/phaseN; python3 phaseN_*.py`
3. CSV outputs in `sim/data/`, figures regenerated each run

### If you want to fork the architecture
The CC BY 4.0 license requires attribution but otherwise permits any use including commercial. The MIT license on code is similarly permissive. Two principles to keep:

1. **Attribution**: cite Morin (2026) when you use the architecture
2. **Open release**: if you improve it, please consider open-releasing the improvements so the architecture compounds in value across the community

## Project history

- **v1 (preprint)** — Original carbon-nanotube application (separate companion preprint)
- **v2** — Semiconductor refocus, initial 5 μm pitch
- **v3** — Quantitative cross-beam Coulomb analysis (Phase 1 sim), 5 μm → 20 μm pitch reframe
- **v4** — Engineering closure of 7 peer-review hurdles: cryogenic column, photonic data path, registration loop, etc.
- **v4.1** — Niki Phase 3 sim verification of all v4 numerical claims
- **v5** — Software stack added; final integrated open-source release

## Status

After v5 release:
- ✅ Architecture engineered subsystem-by-subsystem with vendor candidates
- ✅ All quantitative claims verified by independent simulation
- ✅ Software stack specified down to runnable code skeletons
- ✅ Stage A prototype is buildable now at $600 k / 18 months

Remaining work is normal engineering execution (process development, prototype build, integration test) — not paradigm risk.

## Contact

For questions, collaborations, or to share your fork:
- robmorin0@gmail.com
- File issues at the upstream repository (TBD)

---

*The architecture is open. The math is honest. The supply chain is multi-vendor. The patent landscape is clean. Build it.*
