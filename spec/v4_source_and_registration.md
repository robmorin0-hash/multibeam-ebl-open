# v4 Subsystem Specification — Electron Source Array and Fiducial Registration

**Companion document to Morin (2026) v3 preprint.** Addresses peer-review items (A) source uniformity at $N = 10^6$ field emitters with 10–30% raw tip-to-tip current variation, and (B) sub-μm mechanical/thermal drift across the 20 mm column array versus the 6 nm placement budget. Both items are added as architectural subsystems; nothing here changes the §3 column geometry or the multi-rate steering principle.

Target operating point (carried from v3): $N = 10^6$ beams, 20 μm pitch, 5 nA/beam, 50 kV acceleration, column at 77 K, 6 nm RMS placement budget, deflection-loop rate ≥ 10 kHz.

---

## Part A: Source array and per-beam current control

### A.1 Source technology selection

Three candidate source families exist; the relevant figures of merit are reduced brightness $B_r$ (A·m⁻²·sr⁻¹·V⁻¹), energy spread $\Delta E$, lifetime, tip pitch achievable in a 2D array, and existing array-scale demonstrations.

| Source | $B_r$ (A·m⁻²·sr⁻¹·V⁻¹) | $\Delta E$ (eV) | Pitch | Variation | Array status |
|---|---:|---:|---|---|---|
| Schottky ZrO/W (TFE) | $\sim 10^7{-}10^8$ | 0.6–0.9 | 1–5 mm/tip | 2–5% | Commercial, ≤ few tips |
| Cold FE (W single-tip) | $\sim 10^9$ | 0.3 | mm | 10–20% | Lab |
| CNT / ZrC cold FE array | $\sim 10^8{-}10^9$ | 0.3–0.5 | **10–50 μm** | 10–30% | Lab arrays, ~10⁴ tips |
| Photo-cathode (NEA GaAs, etc.) | $\sim 10^7$ | 0.1 | μm pixel | optical-defined | R&D |

A 20 μm-pitch 10⁶ tip array is not achievable with bulk Schottky guns — each Schottky module is ~5–10 mm wide, which forces a 10⁶-source array to a column footprint of order 50 m, three orders of magnitude beyond v3 geometry. The architecture therefore commits to a **MEMS-fabricated cold-field-emitter (CFE) array** at the 20 μm pitch dictated by the column lattice, with each emitter accompanied by an integrated gate and extractor electrode (Spindt-style or CNT-on-Si).

The 10–30% raw tip variation cited by peer review is the documented spread for CNT and Spindt arrays in the literature [Spindt 1991; Teo 2005; Chen 2014]. The architectural answer is **not** to suppress the variation at fabrication time — that path has been chased for thirty years without crossing the few-percent threshold — but to **accept the variation and close a per-tip current loop** that flattens it electronically. This is the same move the architecture makes for cross-beam Coulomb (§3.4): use cheap massively-parallel electronics to relax a hard physics requirement.

Vendor / fab candidates for the source array proper:
- **NanoScience Corporation** (NSC) — CNT field-emitter array IP, has produced 10³–10⁴ tip arrays.
- **Hamamatsu Photonics** — Spindt-tip arrays, sub-μm-tip ZrC emitters in catalog for X-ray and FE display use.
- **CEA-Leti** (foundry service) — MEMS Spindt processes available as MPW.
- **imec** — gate-stack and HfO₂-dielectric fab for high-voltage extractor structures.
- **NSC + foundry combination**: NSC tip IP transferred onto a CMOS or MEMS substrate at Leti/imec is the credible path; no single vendor currently sells a 10⁶-tip 20 μm-pitch array as a product.

The 77 K column operation is favourable for cold field emission: emitter work-function fluctuation and tip-poisoning by residual H₂O/CO are both strongly suppressed below 100 K, and the literature shows 5–10× lifetime improvement for cryo-operated CFE tips [de Jonge 2002].

### A.2 Per-beam current measurement

Four candidate measurement topologies, evaluated against the 10 kHz bandwidth, 10⁶-channel, in-column, 77 K constraints:

1. **Faraday cup array between source and condenser.** Direct, but mechanically blocks the beam. Discarded.
2. **Blanker pickup electrode (capacitive sense on blanker plate).** Indirect, requires beam to be blanked to sense — incompatible with continuous closed-loop. Discarded.
3. **Beam-induced current on a sense electrode (split anode or annular ring around each beam aperture).** A thin metallized annulus surrounding the bore of the per-beam aperture plate intercepts a known fraction (~1%) of the beam tail. The intercept current $I_s = \eta I_b$ is monotonic and approximately linear in $I_b$ for fixed beam profile. Calibrated against an end-of-column Faraday cup during commissioning. **Selected baseline.**
4. **Substrate-current monitoring at the wafer.** Used in single-beam SEM; impractical at 10⁶ channels because beam-to-substrate-current routing demultiplex is not solvable.

For option 3, with $\eta \approx 10^{-2}$ and $I_b = 5$ nA, the sense current is $I_s = 50$ pA. A 10 kHz bandwidth picoammeter input-referred current noise budget is

$$i_n \le \frac{0.01 \cdot I_s}{\sqrt{f_{BW}}} \cdot \sqrt{f_{BW}} = 0.5\,\text{pA RMS}$$

over 10 kHz, i.e., $i_n \le 5\,\text{fA}/\sqrt{\text{Hz}}$. This is achievable with a cryogenic JFET or HEMT transimpedance front-end (input-referred noise 1–3 fA/√Hz at 77 K, well known from astronomical IR readout and superconducting-detector electronics). At room temperature it would require femtoampere-class instrumentation that does not scale to 10⁶ channels; **cryo operation is what makes this measurement architecturally tractable.**

Sensor IC vendor candidates (per-channel integrated TIA + ADC):
- **Texas Instruments** — LMP7721 (3 fA input bias) for the TIA stage; cryo characterization required.
- **Analog Devices** — ADA4530-1 (electrometer-grade), ADAS1000 family for low-current array readout.
- **Caeleste** (Mechelen, Belgium) — custom cryo-CMOS readout ASICs for astronomy; commercial track record at 10⁴–10⁵ channel arrays.
- **Teledyne / e2v** — cryo SIDECAR-class ASICs (originally for HgCdTe IR FPAs); 32–64 channel multiplexed front-ends at < 4 K.

The architectural choice is a **per-die readout ASIC** at the bottom of the source-array chip: 1024-channel cryo-CMOS ASIC with on-chip TIA, 14-bit ΣΔ ADC, and digital readout at 10 kSps/channel. 10⁶ channels = 10³ ASICs. Total digital bandwidth out of the column: $10^6 \cdot 10\,\text{kSps} \cdot 14\,\text{b} = 140\,\text{Gbit/s}$ — comparable to a single 200G Ethernet link, routable on standard datacenter optics.

### A.3 Closed-loop current control

Each emitter has an individually-addressable extractor electrode driven by a per-tip DAC. The control variable is extractor voltage $V_e$ relative to the emitter, in the range 50–200 V. The Fowler–Nordheim emission law gives

$$I = a V_e^2 \exp\!\left(-\frac{b \phi^{3/2}}{V_e}\right)$$

so emission current depends exponentially on $V_e$. Differentiating, a 1% current change requires $\delta V_e / V_e \sim 0.005$, i.e., ~1 V control resolution out of 200 V full scale. A 12-bit DAC delivers 50 mV resolution — 20× margin.

Loop architecture: digital PI controller per tip, in firmware on the readout-ASIC's neighboring FPGA. DAC update rate 1 kHz is sufficient because the cathode tip thermal time constant is the limiting dynamics (see §A.4).

Per-tip extractor electrode array is fabricated alongside the emitter using standard Spindt MEMS process: poly-Si gate, SiO₂ insulator, Mo or W extractor metallization. Existing CMOS-driver-on-emitter chips have been demonstrated at 10³–10⁴ tip count [Yokoyama 2009; CEA-Leti 2014]; scaling to 10⁶ is a fabrication challenge, not a physics challenge.

**Electronics cost estimate.** Per channel: 1× 12-bit DAC (~$0.05 in volume, integrated on driver ASIC), 1× HV level-shifter to 200 V (~$0.20), share of readout-ASIC + FPGA (~$0.30), share of digital backplane (~$0.10). Total ~$0.65/channel × 10⁶ = **\$650 k**. This is small relative to the ~\$50 M deflection-electronics line item from v3 §2.2, and confirms the architectural premise that "per-beam everything" is now economic.

### A.4 Bandwidth and stability analysis

The dominant cathode tip dynamics are thermal: tip temperature couples to emission current through Fowler–Nordheim $\phi^{3/2}$ dependence. Tip thermal time constant for a typical Spindt cone (apex radius 20 nm, base radius 1 μm, height 2 μm, on Si substrate) is

$$\tau_{th} \approx \frac{C_{tip}}{G_{base}} \approx \frac{(\rho c_p V_{tip})}{k A_{base}/L_{tip}} \sim 1{-}10\,\mu\text{s}$$

i.e., a cathode thermal corner frequency of $\sim 100\,\text{kHz}$. The current-emission electronic response itself (FN tunneling) is sub-ns and not the loop-limiting element.

Loop design: crossover frequency $f_c = 1\,\text{kHz}$, well below the 100 kHz thermal pole — phase margin $\arctan(100/1) \approx 89°$, comfortable. The DAC update rate at 1 kHz adds 0.5-sample delay = 0.5 ms = $-180° \cdot 1\,\text{kHz}/2 = -90°$ at the Nyquist limit, but at the 1 kHz crossover the digital-delay phase contribution is only $-18°$, leaving phase margin > 70°.

This is comfortably **slower than the 10 kHz deflection-loop bandwidth requirement**, which it should be — the current loop only needs to track slow emission drift (thermal cycling, gas adsorption, work-function evolution over minutes to hours), not the per-pixel beam steering that happens on the deflection loop. A fast-tip-current event (gas spike, arc, emission failure) is handled out-of-loop by a fault-detect that blanks the affected beam in < 100 μs and signals the controller.

---

## Part B: Fiducial registration system

### B.5 Fiducial mark design

Etched fiducial marks are placed on every die (typical die: 1 cm²), at the four corners and the centre. Mark inventory per die: 5 marks × 4 mark types = 20 features. Mark types:

| Mark | Function | Resolution |
|---|---|---|
| Cross (5 μm arms, 100 nm width) | Coarse find — millisecond acquisition | ~100 nm |
| 200 nm line grating | Fine $x,y$ — Moiré-style detection | 5–10 nm |
| Vernier pair | Rotation / scale | 20–30 nm |
| Periodic dot lattice | Higher-order distortion | 10 nm |

Marks are etched into the wafer using a low-volume single-beam EBL pass on each wafer-lot's first wafer (or by laser-direct-write in 5 μm-cross size), well before the high-throughput direct-write step. They are tungsten-filled or Au-filled to give strong **backscattered-electron (BSE) contrast** against Si substrate.

The architecture chooses **in-column BSE detection** as primary. A small set (~$10^3$ of the $10^6$) of the array's beams are used as **registration probes**: at intervals during exposure, these probes are momentarily diverted from pattern-writing duty to scan known fiducial locations, and the BSE detector signal is correlated against the expected mark to estimate sub-beam-position error. The cost (1000 beams × few μs per probe × few times per second) is < 0.1% throughput overhead.

Optical interferometric registration (separate visible/IR beam path through the column) is the **secondary backup** path used for slow (Hz) drift tracking and absolute-frame anchoring. Vendors: Zygo, Heidenhain, Renishaw. For the architectural baseline we assume a Zygo ZMI-class differential interferometer on the stage, giving ~0.1 nm/Hz of stage-position knowledge.

### B.6 Registration measurement frequency

A three-tier hierarchy mirroring the multi-rate control philosophy of §2.3:

| Tier | Rate | Scope | Mechanism |
|---|---|---|---|
| Fast trim | 10 kHz | Per-beam, within-field | Probe beams sample fiducial during scan; per-beam DAC offset updated |
| Mid loop | 100 Hz | Per-column subarray (~10⁴ beams) | Full fiducial-corner re-acquisition between scan-fields |
| Slow loop | 1 Hz | Whole column | Stage interferometer + thermal-sensor fusion |

The fast trim handles ~10 nm intra-field drift that accumulates during a single 100 ms field exposure. The mid loop handles the ~100 nm field-to-field thermal step. The slow loop handles the hours-long differential expansion of the 20 mm × 100 mm column.

The peer-review question "per-beam vs per-column registration?" — the answer is **both at different rates**. Per-beam at 10 kHz, per-column-subarray at 100 Hz. The per-beam loop is what makes the architecture meet 6 nm; per-column-subarray alone would couple subarrays and reintroduce the cross-beam dependency v3 §2 was designed to eliminate.

### B.7 Feedback to deflection coils

Each beam already has a 16-bit $x$ and $y$ deflection-current DAC from v3 §2.2. The registration loop adds a **DAC trim register** (12-bit, $\pm 500$ nm range at the wafer plane) summed into the deflection setpoint:

$$I_{\text{deflect},x}(t) = I_{\text{pattern},x}(t) + I_{\text{trim},x}(t)$$

where $I_{\text{pattern}}$ comes from the pattern-generator pipeline at MHz rate and $I_{\text{trim}}$ comes from the registration controller at kHz rate. The trim DAC is physically a second DAC summed in the analog stage of the coil-driver IC, not a re-quantization of the pattern DAC — this preserves the 16-bit pattern resolution.

Loop topology: BSE signal → digital correlator (FPGA, per readout-ASIC) → per-beam position-error estimate → digital PI controller → trim DAC. The correlator is the only non-trivial part: 1D Moiré correlation against a stored reference takes ~100 multiply-accumulate operations per beam per scan, comfortably 100 MOPS for the full 10⁶-channel array running at 100 Hz.

### B.8 Long-term thermal compensation

Differential thermal expansion of the 20 mm column over hours is the slow drift the architecture must track. Coefficient of thermal expansion for Invar ($\alpha \sim 1.2 \times 10^{-6}$/K) over 20 mm at 0.01 K stability still gives 0.24 nm — sub-budget at the column level. The dominant residual drift is in the wafer chuck and stage, where $\alpha \cdot L = 2\,\mu\text{m}/\text{K}$ for typical SiC stages over a 200 mm wafer.

The slow registration loop (B.6 tier 3) directly observes this drift via fiducial re-acquisition between fields and feeds it back as a uniform-trim component on $I_{\text{trim}}$ across all beams in a column subarray. The thermal-time-constant of the column is ~1 hour, so the 1 Hz slow loop has 3600× bandwidth margin over the drift dynamics.

**Reset / recalibration cycle.** Every wafer lot (~1 hour), the column re-acquires absolute fiducials at all 20 die-corner marks for the loaded wafer, re-zeros the trim registers to the calibrated state, and persists the calibration vector for the rest of that lot.

### B.9 Components and vendors

| Subsystem | Vendor(s) | Notes |
|---|---|---|
| BSE detector array (in-column) | El-Mul, FEI/Thermo Fisher, JEOL, OEM scintillator + SiPM | Need 10³ channel × kHz, cryo-compatible — likely custom |
| SiPM cryogenic array | Hamamatsu (S13361 series), SensL/onsemi | Operate 77 K (slight DCR reduction at LN₂) |
| Stage interferometer | Zygo ZMI-2000, Heidenhain LIP, Renishaw RLE | 0.1 nm resolution, multi-axis differential |
| Per-tip current TIA / ADC ASIC | Caeleste, Teledyne, in-house at imec/Leti | Cryo-CMOS, 1024 ch each, 14-bit |
| Extractor-voltage DAC + level-shift | Analog Devices AD568x family, TI DAC81xx | Integrated into driver ASIC |
| Source array MEMS fab | CEA-Leti, imec, Lawrence Semiconductor | MPW path realistic; product path requires partner |
| BPM (beam-position monitor) read-out | Adapted from accelerator physics — Instrumentation Technologies (Slovenia) Libera Spark line | Sub-μm BPM precision at GHz; adaptable to keV regime |

Source-array MEMS is the highest-risk vendor line — no current commercial offering at 10⁶ tip × 20 μm pitch. The architecture's response is the same as for deflection electronics: **the spec is a fab spec, not a product spec.** The wafer-level process exists in pieces (Spindt tip, CNT growth, integrated gate); the integration is non-trivial but does not require new physics.

### B.10 Cost addition

| Line item | Unit cost | Quantity | Subtotal |
|---|---:|---:|---:|
| Source-array wafer (MEMS, 10⁶ tip) | \$2 M NRE + \$500 k/array | 1 array + 2 spares | \$3.5 M |
| Per-tip current loop electronics (§A.3) | \$0.65/ch | 10⁶ | \$650 k |
| Cryo-CMOS readout ASIC (1024 ch) | \$3 k/ASIC | 10³ | \$3 M |
| BSE detector + SiPM array (1024 ch) | \$2 k/ch averaged | 10³ | \$2 M |
| Stage interferometer (3-axis) | — | 1 system | \$300 k |
| Registration FPGA / correlator | \$5 k each | 100 | \$500 k |
| Fiducial-mark wafer-prep (per-lot SBEBL pass) | — | service | \$50 k/year |
| Engineering integration | — | — | \$5 M |
| **Subsystem total** | | | **~\$15 M** |

This sits inside the v3 §6 capital envelope of \$10–30 M per tool. The line items most sensitive to volume are the source-array NRE and the readout-ASIC tape-out; both amortize favourably at fleet scale.

### B.11 Open questions

1. **Per-tip emission lifetime at 77 K.** Cryo-operated CNT/Spindt arrays show 5–10× lifetime improvement in single-tip studies; a 10⁶-tip array's *failure-rate distribution* (not mean lifetime) determines hot-spare-tip count required. No published data at this array scale. Phase-2 experimental task.

2. **BSE cross-talk between adjacent probe beams.** At 20 μm pitch, BSE from beam $i$ scanning a fiducial may register at the detector pixel assigned to beam $j$. Modelling required (Monte Carlo of BSE emission cone at 50 kV in tungsten fiducial vs. Si substrate; geometric collection by detector geometry).

3. **Probe-beam scheduling vs. pattern throughput.** The 0.1% throughput overhead estimated in §B.5 assumes optimal scheduling. Real-world pattern-data layouts may force more frequent probing; needs simulation against actual GDSII test cases.

4. **Cryo readout-ASIC yield.** 10³ ASICs at 1024 ch each with cryo-CMOS process novelty — what's the realistic per-ASIC yield, and does the architecture survive 1–5% dead-channel rate at the system level? (Probably yes via redundant-beam allocation, but needs explicit budget.)

5. **Fiducial mark wear under repeated probe-beam exposure.** Tungsten fills should be stable, but cumulative dose at the same nanometre-scale location may erode mark edges over weeks. Mark refresh policy TBD.

6. **Interferometer / fiducial-BSE fusion algorithm.** Three-tier Kalman or particle-filter design open; well-studied in accelerator BPM literature but specific filter architecture for the registration use case needs design work.

These are the same character of open question as the v3 §8 list — engineering integration, not new physics. The architecture remains internally consistent and within the published capital envelope.
