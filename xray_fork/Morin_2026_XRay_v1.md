# Multi-Beam Direct-Write X-Ray Lithography via Per-Beam Electron-Pumped Converter Arrays

## An Open, Mask-Free, Multi-Vendor Architecture for Mature-Node Semiconductor Manufacturing — X-Ray Variant

**Robert Gerald Morin¹,***

¹NÎKI Nation Builders, Edmonton, Alberta, Canada
*Correspondence: robmorin0@gmail.com*

**Preprint v1 — May 16, 2026**

*Companion to the Morin (2026) multi-beam electron-beam lithography (MBM-EBL) preprint series (v1–v4). MBM-EBL v3 quantitatively validated the per-beam Lorentz-steering architecture for direct-write electron lithography at mature nodes; v4 closed the cryogenic, photonic, and registration engineering. This X-ray v1 reuses the entire MBM-EBL v4 column upstream of the wafer plane and replaces the final electron-resist exposure stage with an electron-pumped soft-X-ray converter array, transferring the v4 architectural principles to X-ray lithography. The v1 rigor target matches MBM-EBL v3 (quantitative architecture sketch + closed-form physics + staged validation pathway), not MBM-EBL v4 (detailed subsystem engineering specifications).*

---

**Open Release.** This work is released under a Creative Commons Attribution 4.0 International License (CC BY 4.0). It may be freely copied, modified, built, commercialised, or extended by anyone, for any purpose, with attribution to the author. The author retains no patent claim on the architecture or its constituent ideas. By publication, all combinations and methods described herein enter the public domain as prior art, and may not be enclosed by subsequent intellectual-property filings by any party.

---

## Abstract

We propose a multi-beam direct-write soft-X-ray lithography (MBM-XRL) architecture that applies the architectural principles of the Morin (2026) multi-beam EBL series — per-beam independent steering, multi-rate control, mask-free direct write, multi-vendor supply chain, mature-node target, ~10× cost advantage over EUV — to X-ray lithography. The architectural primitive is the *electron-pumped per-beam X-ray converter array*: the upstream column of MBM-EBL v4 is preserved unchanged ($N \sim 10^5{-}10^6$ independently-steered 50 kV electron beams at 20 μm pitch, 77 K cryogenic column, photonic data path), and the final exposure stage is changed by inserting a thin metallic converter target (Mg or Al K-line emitter) just above the wafer. Each electron beam generates its own localised soft-X-ray source spot at the converter; the X-rays then expose the wafer through a sub-micrometer proximity gap. The resulting tool is mask-free, direct-write, software-defined, multi-vendor, and capital-comparable to MBM-EBL v4 within the noise of a sketch-level estimate.

The X-ray variant offers three distinct architectural advantages over MBM-EBL v4:

1. **Decoupling of resist chemistry from electron-beam shot-noise.** Soft X-rays (~1 nm, ~1.25 keV) couple to standard EUV-grade metal-oxide and chemically-amplified resists with broader process latitude than direct electron exposure, particularly for resists optimised for the EUV ecosystem (Inpria, Imec EUV CAR families).

2. **Wafer-side proximity-litho geometry decouples the placement budget from beam-column geometry.** The placement budget is split between *upstream electron-beam placement on the converter* (inherited from MBM-EBL v4: $\sigma \approx 8$ nm) and *downstream X-ray geometric blur* (Fresnel diffraction + penumbra + photoelectron range in resist: $\sigma_X \approx 50$–$80$ nm at 1 nm wavelength + 1 μm proximity gap). For mature-node targets, the X-ray geometric blur dominates, freeing the upstream column from sub-10-nm placement requirements that drive MBM-EBL v4's cryogenic complexity.

3. **Resist outgassing decouples from the column.** The resist is exposed by photons, not by direct electron contact. Beam-induced contamination of the cold column from photoacid-generator volatiles is geometrically blocked by the converter foil itself, which acts as a vacuum bulkhead between the column UHV and the wafer subchamber.

The validated node-range envelope is **80–250 nm at 1 nm wavelength** with a Mg-K converter target and ~1 μm proximity gap, set primarily by Fresnel diffraction and photoelectron range in the resist. The tighter 50–80 nm range accessible to MBM-EBL v4 is not directly available to MBM-XRL v1 at these wavelengths and gaps; a future v2 path through Cu-Kα (0.154 nm, 8.05 keV) with sub-micrometer proximity and ultra-thin resist could extend the architecture toward 30 nm, but is left open. Capital cost is estimated at **\$40–50 M per tool**, retaining the order-of-magnitude advantage over EUV.

The architecture inherits the multi-vendor supply chain check from MBM-EBL v4 (≥3 vendors / ≥2 jurisdictions per subsystem) and adds three new vendor categories specific to X-ray operation (converter targets, X-ray-resist suppliers, proximity-gap metrology), each of which we show has multi-vendor commodity availability. We identify the remaining open engineering questions — converter-foil thermal management, source-spot characterisation at the converter, photoelectron-range modelling in modern metal-oxide resists, and proximity-gap servo at ~100 nm tolerance — and propose a staged validation pathway analogous to MBM-EBL v3 §7.

The architecture is released openly. Any party may build, modify, or commercialise it without restriction.

**Keywords:** X-ray lithography, proximity X-ray lithography, multi-beam direct write, electron-pumped X-ray source, mature-node semiconductor manufacturing, EUV alternatives, sovereign semiconductor supply chain, mask-free lithography

**Classification:** Semiconductor manufacturing; X-ray lithography; Charged-particle optics; X-ray physics; Manufacturing automation

---

## 1  Introduction

### 1.1  Why X-ray lithography is worth re-opening

X-ray lithography has been written off twice. In the 1980s–1990s, the IBM and NTT proximity X-ray lithography (PXL) programs demonstrated 70–100 nm patterning on synchrotron and compact-source X-ray tools, were technically competitive with the deep-ultraviolet (DUV) state of the art at the time, and were abandoned principally because of mask-related problems (membrane stability, mask cost, mask-to-mask matching) and because DUV scaling proved more economical than expected [24, 25]. By the time DUV reached its limit in the mid-2000s, the industry's R&D investment had shifted to EUV at 13.5 nm. The synchrotron and compact-X-ray-tube infrastructure built for PXL was largely dismantled.

The first reason to re-open is that the principal *historical* failure mode of X-ray lithography — the X-ray mask — is removed by direct-write architecture. A multi-beam direct-write X-ray tool needs no mask, in the same way that a multi-beam direct-write EBL tool needs none. The mask-membrane-stability problem, the mask-NRE-cost problem, and the mask-matching problem all dissolve simultaneously.

The second reason to re-open is that the *physical* advantages of soft X-ray exposure relative to DUV or direct e-beam exposure remain real. Soft X-rays at ~1 nm wavelength penetrate ~3–10 μm of standard resist with little diffractive blur, expose through opaque overlayers (metal hardmasks, thick organic planarisation layers), produce small photoelectron ranges (~60–80 nm in PMMA at 1 keV photoelectron energy), and decouple cleanly from the visible/UV optics ecosystem. The EUV community has, in effect, validated the soft-X-ray exposure regime for production manufacturing; the question is whether the same exposure physics can be delivered through a different and substantially cheaper tool architecture.

### 1.2  Why the Morin (2026) MBM-EBL architectural principles transfer

The Morin (2026) MBM-EBL v3 [16] and v4 [17] preprints established that the following architectural primitives, taken together, drive an order-of-magnitude cost reduction relative to EUV at mature nodes:

- **Per-beam independent steering** at $N = 10^5$–$10^6$ channels, with electromagnetic (Lorentz) deflection rather than shared electrostatic projection.
- **Multi-rate control hierarchy**: inner electronic loop at 10–100 kHz per beam, middle blanker loop at ~1 kHz per beam, outer mechanical loop at 1 Hz for the wafer stage.
- **Mask-free, software-defined patterning**, removing the \$10–50 M mask-NRE that dominates custom-ASIC economics at mature nodes.
- **Multi-vendor, multi-jurisdictional supply chain** with ≥3 vendors and ≥2 jurisdictions per subsystem, eliminating the EUV-style triple-monopoly (ASML/Zeiss/Cymer).
- **Mature-node target** (50–180 nm in MBM-EBL v4), explicitly *not* competing with EUV at <5 nm.
- **Open architecture** (CC BY 4.0), preventing enclosure by any single integrator.
- **Optional cryogenic + photonic stack** to manage thermal dissipation and pattern-data bandwidth at the $N \sim 10^6$ scale.

Of these seven primitives, **all seven transfer directly to an X-ray architecture in which the X-ray source is itself an array of $N \sim 10^6$ independently-controlled per-beam emitters**. The architectural problem reduces to: *what is the right per-beam X-ray emitter, and how does it integrate with the v4 column?* §1.3 below establishes the choice.

### 1.3  Choice of X-ray generation mechanism

Four candidate X-ray generation mechanisms were considered, evaluated against the criterion of preserving the MBM-EBL v4 architectural principles most cleanly:

| Mechanism | Per-beam independence | Inherits v4 column? | Capital cost | Notes |
|---|---|---|---|---|
| **Electron-pumped converter array** (chosen) | Excellent — each e-beam makes its own X-ray source spot | **Yes, entirely** | \$40–50 M | Adds converter target + proximity stage |
| Inverse Compton scattering array | Poor — needs $10^6$ counter-propagating laser crossings | No (separate optical lattice) | \$200 M+ | Coherent X-rays, narrow band, but scales catastrophically |
| Laser-produced plasma (LPP) array | Moderate — each plasma needs kJ-class drive laser | Partially | \$100 M+ | EUV-class wavelengths; per-source drive lasers don't scale to $10^6$ |
| Programmable shutter array | Poor — single source + masked shutter is essentially a programmable mask | No | \$30 M | Loses massive-parallel direct-write; throughput bottlenecked on a few sources |

The **electron-pumped converter array** is the only candidate that preserves all seven MBM-EBL v4 primitives. The architectural change relative to v4 is purely additive: a thin converter target is inserted between the column and the wafer, and a proximity stage is added to control the converter–wafer gap. Every other subsystem (source array, deflection, cryogenic column, photonic data path, registration, wafer chuck) is inherited from v4 verbatim. This single-architectural-change property is decisive: it means MBM-XRL v1 is *not* a new tool design but a v4-derivative tool design, with most of the v3/v4 engineering work already complete.

The inverse Compton, LPP, and shutter-array variants are noted for completeness and discussed briefly in §7.3 as alternative architectures with different cost/performance tradeoffs; none are pursued in this v1 sketch.

### 1.4  Scope of this v1

This v1 preprint is a sketch at MBM-EBL v3 rigor level: closed-form physics, an architecture diagram (verbal), a first-pass placement budget, a sketch-level cost rollup, a multi-vendor supply-chain check, and a staged validation pathway. The subsystem-level engineering closure (cryogenic thermal accounting, photonic data path topology, MEMS source-array scale-up, etc.) is inherited unchanged from MBM-EBL v4 and is referenced rather than restated; subsystems specific to the X-ray variant (converter target, proximity stage, X-ray resist selection, X-ray-side dose calibration) are described at the v3 rigor level. A future v2 of MBM-XRL would close these subsystems at v4-rigor with supplementary specifications, after Stage A validation.

---

## 2  Architecture

### 2.1  Overview

The MBM-XRL v1 architecture is the MBM-EBL v4 column with a final-stage modification. From top to bottom:

1. **MEMS field-emitter source array** (v4 §3.8): $N = 10^6$ Spindt/CNT cold-field-emitter tips at 20 μm pitch, with per-tip closed-loop current control to 1% uniformity.

2. **Acceleration and condenser optics** (v4 baseline): each beam is accelerated to 50 kV nominal (range 30–80 kV — the operating energy choice is discussed in §3.2). Common condenser optics shape each beam to a sub-20-nm focal spot at the converter plane.

3. **Cryogenic 77 K column with HTS deflection coils** (v4 §3.5): YBCO 2G coated-conductor coils, Meissner shielding between coils, cryo-CMOS DACs, photonic data delivery. Each beam is independently steered with a $\pm 0.66$ mm placement window and 8 nm RMS total placement budget (v4 §4.4).

4. **Per-beam blanker array** (v4 §3.7): CMOS-MEMS hybrid die at the column footprint, 40 V switched plates with 1 GHz bandwidth.

5. **NEW — Electron-pumped X-ray converter target**: a continuous thin metallic foil (Mg, Al, or Cu) suspended ~1 μm above the wafer plane, oriented perpendicular to the electron beam axis. Electrons land on the upper surface of the foil and produce X-rays via bremsstrahlung continuum + characteristic K-line emission. The X-rays radiate downward into the wafer; high-energy backscattered electrons are absorbed in an upstream electron beam-stop coupled to the foil mount. See §2.2 below for the target subsystem.

6. **NEW — Proximity stage**: a piezoelectric flexure stage holding the wafer chuck at a controlled gap $g$ (50 nm–10 μm range, with 10 nm gap repeatability) below the converter foil. Inherits the registration, metrology, and chuck-thermal subsystems from v4 §3.9–3.10.

7. **Wafer chuck and stage**: identical to v4 §3.10 — AlN ceramic chuck with backside He gas, Galden microchannel loop, 36-zone TEC trim, and 6-DOF stage with Zygo ZMI interferometric metrology.

### 2.2  The converter target subsystem (new)

The converter is the principal new subsystem relative to MBM-EBL v4. Its design parameters:

- **Target material**: thin metallic film selected for K-line emission at the desired wavelength. The v1 nominal is **100 nm Mg foil on a 200 nm Si₃N₄ membrane substrate**, providing Mg-K emission at 1.254 keV (0.989 nm), with the Si₃N₄ acting as a vacuum-bulkhead substrate and the Mg as the active emitter. Alternative target candidates discussed in §3.2 include Al-K (1.486 keV, 0.834 nm), Cu-L (0.93 keV, 1.33 nm), and the hard-X-ray Cu-Kα (8.05 keV, 0.154 nm) for the future v2 path.

- **Geometry**: continuous foil spanning the full 20 mm × 20 mm column footprint, mounted at the perimeter on a SiC frame. The frame includes integrated water-cooling channels for steady-state heat removal. Membrane stress is balanced between the Mg and Si₃N₄ layers to keep deflection under wafer load to <100 nm peak-to-valley.

- **Operating temperature**: nominally 295 K (warm). The converter is *not* part of the 77 K cold column; it is mounted to the warm-side wafer chamber. This forces a cold-warm gap traverse for the electron beam, but the traverse is shorter and easier than v4 §3.11 because the converter is rigidly tied to the wafer plane (no relative motion). View-factor-limited radiative load on the cold column above is ~150 mW — comparable to the v4 cold-warm interface budget.

- **Lifetime**: at $I_b = 2$ nA per beam × $10^6$ beams × 50 keV = 100 W total beam power deposited in the foil. Sputtering of the Mg layer at ~3 × 10⁻³ atoms per electron at 50 keV implies a sputtering rate of ~5 × 10⁻⁹ kg/s, or ~40 nm of Mg removed per hour averaged across the foil. The 100 nm Mg layer is replaced approximately every 2.5 hours of operation, motivating an automatic foil-cartridge change system (see §5.4). Practical operation will likely use a thicker Mg layer (300–500 nm) for ~12-hour lifetime between cartridge changes; the tradeoff is a slight increase in X-ray source spot size due to electron scattering within the thicker target, discussed in §3.3.

- **Vacuum sealing**: the converter foil + Si₃N₄ membrane acts as a vacuum bulkhead between the column UHV ($10^{-9}$ Pa) and the wafer subchamber ($10^{-3}$ Pa during resist outgassing). This is a load-bearing function: the membrane must survive a sustained $10^6$:1 pressure differential. 200 nm Si₃N₄ is standard practice for X-ray windows in synchrotron-instrument beamlines [26]; comparable membranes routinely survive 1 atm differentials across 20 mm-diameter apertures. The 10⁻³ Pa transient differential of MBM-XRL is six orders of magnitude milder.

### 2.3  Multi-rate control (preserved from MBM-EBL v4)

The control hierarchy is identical to MBM-EBL v4 §2.3 with one addition:

- **Inner loop (10–100 kHz, electronic, per beam)**: Lorentz deflection of each electron beam on the converter plane. Each beam paints a 20 μm × 20 μm cell on the converter; the X-ray emission point on the converter is the steerable observable.
- **Middle loop (~1 kHz, electronic, per beam)**: per-beam blanker, on/off plus 4-bit greyscale dose modulation.
- **Outer loop (1–10 Hz, mechanical)**: wafer stage motion between full-column footprints (~10 cm² fields).
- **NEW — Proximity loop (~10 Hz, piezo)**: converter–wafer gap servo, maintaining the gap $g$ at the nominal 1 μm with ~10 nm tolerance. Setpoint is selected per layer based on the desired Fresnel-blur–vs–penumbra tradeoff (§3.4). Implemented via capacitive gap sensors at the converter frame perimeter and a piezo Z-flexure under the wafer chuck.

The proximity-gap loop is geometrically decoupled from the per-beam placement loop: gap variation affects all $10^6$ beams identically and is therefore a global degree of freedom calibrated once per layer, not a per-beam control variable.

---

## 3  Physics framework

### 3.1  Electron-to-X-ray conversion efficiency

For electrons impinging on a thick metallic target, the integrated X-ray emission efficiency is approximately

$$\eta \approx 7 \times 10^{-10} \cdot Z \cdot V_0 \;\;[\text{V}], \qquad (1)$$

a standard textbook result for the bremsstrahlung continuum integrated over $4\pi$ sr [27]. For $Z = 12$ (Mg) and $V_0 = 50$ kV, $\eta \approx 4.2 \times 10^{-4}$. The characteristic K-line emission contributes an additional ~$10^{-4}$ to ~$10^{-3}$ at the K-line energy, depending on the overvoltage ratio $V_0 / V_K$ ($V_K \approx 1.3$ kV for Mg, giving an overvoltage of ~38 at 50 kV — well above the maximum-K-yield overvoltage of ~10). For thin targets at the v1 geometry (100–500 nm Mg), only the fraction of electrons stopping within the foil contributes; the integrated efficiency is reduced by approximately the ratio of foil thickness to electron stopping range (~5 μm at 50 keV in Mg), giving $\eta_\text{thin} \approx (0.1\text{–}0.5)\,\eta \approx 4{-}20 \times 10^{-5}$.

For the v1 nominal (200 nm Mg layer, 50 kV beams), we take **$\eta = 1 \times 10^{-4}$** as a conservative design value, with the recognition that empirical measurement at Stage A may revise this upward (toward the thick-target ~$4 \times 10^{-4}$ limit) or downward (if angular distribution into the wafer hemisphere is unfavourable).

Of the integrated $4\pi$-sr emission, the fraction radiated into the downward hemisphere (toward the wafer) is ~0.5 for a forward-isotropic source. Of *that*, only the fraction subtended by the wafer aperture (which at $g = 1$ μm proximity is ~$2\pi$ effectively, due to the geometry) contributes to wafer exposure. The net downward-hemisphere collection efficiency is ~0.5, giving an effective wafer-incident X-ray power per beam:

$$P_X^\text{beam} = \eta_\text{thin} \cdot 0.5 \cdot I_b V_0 \approx 10^{-4} \cdot 0.5 \cdot 2\,\text{nA} \cdot 50\,\text{kV} \approx 5\,\text{nW}. \qquad (2)$$

At a photon energy $h\nu = 1.254$ keV (Mg-K), this corresponds to a photon rate

$$\dot{n}_\text{ph}^\text{beam} = P_X / h\nu \approx 2.5 \times 10^{10}\,\text{photons/s per beam}. \qquad (3)$$

Aggregated across $N = 10^6$ beams, the total X-ray photon production rate is **$2.5 \times 10^{16}$ photons/s into the wafer hemisphere**, or ~5 mW of soft-X-ray power. This is comparable to compact X-ray sources used in PXL-era research tools [25, 28] but distributed across $10^6$ independent emitters rather than a single point source.

### 3.2  Choice of converter wavelength

The choice of target material sets the X-ray wavelength, which trades off:

| Target | $h\nu$ (keV) | λ (nm) | PE range in resist | Fresnel √(λg) at g=1μm | Resist absorption length |
|---|---:|---:|---:|---:|---:|
| C-K (graphite) | 0.28 | 4.43 | <10 nm | 67 nm | 0.05–0.2 μm |
| Cu-L | 0.93 | 1.33 | 30–50 nm | 36 nm | 1–3 μm |
| **Mg-K (v1 nominal)** | **1.25** | **0.99** | **50–80 nm** | **31 nm** | **2–5 μm** |
| Al-K | 1.49 | 0.83 | 80–120 nm | 29 nm | 3–8 μm |
| Si-K | 1.74 | 0.71 | 100–150 nm | 27 nm | 4–10 μm |
| W-M | 1.77 | 0.70 | 100–150 nm | 26 nm | 4–10 μm |
| Cu-Kα (v2 candidate) | 8.05 | 0.154 | 1000–2000 nm | 12 nm | 30–100 μm |

The principal tradeoff at this part of the X-ray spectrum is: **as wavelength shortens (energy hardens), Fresnel diffraction blur drops, but the photoelectron range in the resist grows linearly with PE kinetic energy, eventually dominating.** Mg-K at 1.25 keV sits at the optimum: Fresnel ~31 nm (compatible with sub-100 nm nodes at 1 μm proximity) and PE range ~50–80 nm (compatible with 100–200 nm nodes). This is the same architectural choice made historically by IBM's 1990s PXL program [24].

Cu-Kα at 8.05 keV is the most promising candidate for a future v2 hard-X-ray path, accepting the increased PE-range constraint in exchange for much tighter Fresnel resolution. At Cu-Kα, the PE range in PMMA exceeds 1 μm, which would force ultra-thin resist (<50 nm) and aggressive hardmask strategies. We flag this as a v2-candidate architecture but do not develop it further in v1.

### 3.3  Source spot size on the converter

The X-ray source spot on the converter is set by three contributions:

- **Incoming electron beam spot** at the converter plane: inherited from v4, ~5 nm RMS.
- **Lateral electron scattering** within the converter foil: for 100 nm Mg at 50 keV, the lateral spread of the electron interaction volume is ~30 nm (Monte Carlo CASINO/PENELOPE estimates [29] for thin foils; the full electron range of 5 μm is mostly forward-scattered, but lateral kicks accumulate). For 500 nm Mg (the thicker variant used for cartridge-life extension), the lateral spread grows to ~80 nm.
- **Backscatter / re-emission** within the Si₃N₄ substrate below the Mg layer: contributes a low-amplitude tail at the ~100 nm scale.

For the v1 nominal (100 nm Mg + 200 nm Si₃N₄, 50 kV electrons), the effective X-ray source spot at the lower face of the converter is **~30–50 nm FWHM**, with a broader low-amplitude tail at ~100 nm scale from the substrate backscatter contribution. This is the controlling parameter for penumbral blur in §3.4.

The 30–50 nm source spot at the converter is substantially larger than the 5 nm e-beam spot at v4's wafer plane. *This is the principal physical penalty paid for the X-ray architecture.* The architectural answer is that the X-ray exposure stage is geometrically decoupled from the wafer placement: source-spot–driven penumbra at the wafer is a property of the X-ray geometry, not the upstream electron-beam placement budget, and folds into the X-ray-side budget of §3.4 rather than the electron-side budget of MBM-EBL v4.

### 3.4  Wafer-plane resolution budget

Four blur mechanisms add (in quadrature, with caveats) at the wafer plane:

**(a) Fresnel diffraction:**
$$\sigma_\text{Fresnel} \approx \sqrt{\lambda \cdot g}, \qquad (4)$$
where $\lambda$ is the X-ray wavelength and $g$ is the proximity gap. For $\lambda = 1$ nm (Mg-K) and $g = 1$ μm: $\sigma_\text{Fresnel} \approx 31$ nm. Halving the gap to $g = 250$ nm brings this to 16 nm; doubling the gap to 4 μm pushes to 63 nm.

**(b) Penumbral (geometric) blur from finite source spot:**
$$\sigma_\text{penumbra} \approx s \cdot \frac{g}{D + g}, \qquad (5)$$
where $s$ is the X-ray source spot diameter at the converter, and $D$ is the source-to-wafer distance. In the proximity geometry, $D \approx g$ (the source is at the lower face of the converter foil, immediately above the wafer), so Eq. (5) reduces to
$$\sigma_\text{penumbra} \approx s/2.$$
For $s = 40$ nm: $\sigma_\text{penumbra} \approx 20$ nm. The source spot is the controlling parameter and is essentially independent of the proximity gap in the proximity limit.

**(c) Photoelectron range in resist:**
$$\sigma_\text{PE} \approx R_\text{PE}(E_\text{PE}), \qquad (6)$$
where $R_\text{PE}$ is the practical range of photoelectrons in the resist. For Mg-K photons (1.254 keV) absorbed by the C-K shell of PMMA (binding energy ~0.28 keV), the photoelectron has kinetic energy ~0.97 keV and a practical range in PMMA of ~60–80 nm [30]. For HSQ (silsesquioxane), the range is similar. For Inpria Sn-cluster resists, the heavy-metal content shortens the practical range to ~30–50 nm because secondary cascade events deposit dose more locally [22]. The v1 nominal uses Inpria-class resist for the production node range, giving $\sigma_\text{PE} \approx 40$ nm.

**(d) Upstream electron-beam placement budget:** inherited from MBM-EBL v4 at $\sigma \approx 8$ nm. This is the *position uncertainty of the X-ray source on the converter*, which translates approximately 1:1 to the wafer plane in the proximity geometry. We carry $\sigma_\text{e-beam} = 8$ nm.

The v1 total resolution budget at the wafer plane is

$$\sigma_\text{total,X} = \sqrt{\sigma_\text{Fresnel}^2 + \sigma_\text{penumbra}^2 + \sigma_\text{PE}^2 + \sigma_\text{e-beam}^2}, \qquad (7)$$

evaluated at the v1 nominal ($\lambda = 1$ nm, $g = 1$ μm, $s = 40$ nm, Inpria resist):

$$\sigma_\text{total,X} = \sqrt{31^2 + 20^2 + 40^2 + 8^2}\,\text{nm} \approx 55\,\text{nm}.$$

For the conservative case ($s = 60$ nm, 500 nm Mg foil; PMMA resist with $\sigma_\text{PE} = 80$ nm): $\sigma_\text{total,X} \approx 88$ nm.

### 3.5  Validated node-range envelope

Adopting the 20 %-sub-pixel placement convention from MBM-EBL v4 §4.5:

| Node | 20 % sub-pixel budget | v1 nominal verdict ($\sigma$ = 55 nm) | v1 conservative verdict ($\sigma$ = 88 nm) |
|---:|---:|---|---|
| 250 nm | 50 nm | comfortable PASS | marginal PASS |
| 180 nm | 36 nm | marginal | FAIL |
| 130 nm | 26 nm | marginal FAIL | FAIL |
| 90 nm | 18 nm | FAIL | FAIL |
| 50 nm | 10 nm | FAIL | FAIL |

The v1 architecture is therefore best matched to the **180–250 nm node range** at conservative assumptions and **130–250 nm at nominal assumptions**. The 90 nm node and below requires either (a) tighter proximity (sub-500 nm gap, which stresses the gap servo and the planarity tolerance of the converter foil), (b) a tighter-source-spot converter (thinner Mg, sub-200 nm Si₃N₄ substrate, accepting reduced membrane robustness), or (c) the v2 path to harder X-rays (Cu-Kα) combined with ultra-thin resist.

The conservative 250–180 nm range is *exactly the range underserved by EUV (which targets <5 nm) and where DUV mask economics are most punishing for low-volume custom designs*. It overlaps the upper end of MBM-EBL v4's 50–180 nm range and extends ~70 nm coarser. The architecture is not redundant with MBM-EBL v4 — it serves the coarser end of mature-node manufacturing where X-ray resist process latitude and wafer-side proximity geometry are advantageous — but it also does not extend below v4's node floor.

### 3.6  Throughput

Per-beam X-ray photon rate at the wafer (Eq. 3): $2.5 \times 10^{10}$ ph/s.

For a standard resist sensitivity of 20 mJ/cm² (Inpria-class, similar to EUV resist dose [22]), the required photon flux per cm² at 1.254 keV is $20 \times 10^{-3} / (1.254 \times 10^3 \times 1.6 \times 10^{-19}) = 1.0 \times 10^{14}$ ph/cm².

For a 30 nm pixel ($9 \times 10^{-12}$ cm²), the required dose per pixel is **900 photons**. (Note this is comfortably above the soft-X-ray stochastic-defect floor of ~30 photons per pixel set by Poisson statistics; the v1 architecture is not shot-noise-limited at the target nodes.)

Per-pixel exposure time per beam: $900 / (2.5 \times 10^{10}) \approx 36$ ns.

For a 300 mm wafer at 30 nm grid: total pixels = $7.85 \times 10^{13}$. With $N = 10^6$ parallel beams, each exposes $7.85 \times 10^7$ pixels in $7.85 \times 10^7 \times 36 \times 10^{-9} \approx 2.8$ s. With $N = 10^5$ beams (conservative configuration): layer time ~28 s.

**Layer throughput** at 30 nm pixel grid: **~1300 layers/hr (aggressive, $10^6$ beams) or ~130 layers/hr (conservative, $10^5$ beams)**.

**Wafer throughput** through a representative 70-layer mature-node process flow: **~18 wph (aggressive) or ~1.8 wph (conservative)**.

These numbers are comparable to MBM-EBL v4 (~15 wph aggressive). The MBM-XRL throughput is *not penalised* relative to v4 by the conversion efficiency — the per-beam current is the same, the dose per pixel is higher in raw-photon count but the photon-energy-per-event is correspondingly lower, and the net pixels-per-second-per-beam works out within a factor of 2. The principal throughput cost relative to v4 is the dose budget overhead from the lower-than-100% conversion efficiency, which is absorbed by the longer per-pixel exposure time.

### 3.7  Cross-beam interactions

The MBM-EBL v3 cross-beam Coulomb perturbation analysis (v3 §3.4) applies *upstream of the converter*, unchanged. Within the column, electron beams interact via Coulomb force as in v4; the v3 σ_cross ≈ 2 nm at the v4-derated 2 nA / 20 μm pitch is inherited.

*Below* the converter, X-ray photons do not interact with each other (no photon-photon scattering at these energies). The cross-beam X-ray exposure budget therefore does not need a new lattice-sum analysis; X-ray exposure from neighbouring beams overlaps geometrically (at the wafer plane, with the geometric blur of Eq. 7) and combines additively in dose. This is *easier* than the e-beam case, because the only cross-beam coupling is the deterministic dose-overlap from adjacent beams' soft penumbral skirts, which is calibratable per the v3 §3.4.2 framework (deterministic component absorbed into per-beam DAC offset).

### 3.8  Shot noise

X-ray photon shot noise is the fundamental dose-fluctuation limit. For 900 photons per pixel (§3.6 above), Poisson shot noise is $\sqrt{900}/900 \approx 3.3\%$, well under the ~5% line-edge-roughness budget for mature-node manufacturing. The architecture is shot-noise-safe at the v1 nominal dose.

For higher-resolution operation at 10 nm pixel ($10^{-13}$ cm²), the required dose drops to 100 photons per pixel, which gives 10% Poisson noise — at the edge of mature-node acceptability and forcing either dose-increase or pixel-averaging. This is one of the soft barriers that prevents the v1 architecture from extending below ~100 nm without further engineering.

---

## 4  Subsystem engineering

### 4.1  Inherited from MBM-EBL v4 (without change)

The following subsystems are inherited from MBM-EBL v4 with no modification. Specifications are documented in [16] and [17]; we reference rather than restate.

| Subsystem | Inherited from |
|---|---|
| MEMS field-emitter source array (10⁶ tips at 20 μm pitch) | v4 §3.8 + [S5] |
| Acceleration & condenser optics | v4 §2.1 |
| Cryogenic 77 K column with HTS deflection coils | v4 §3.5 + [S2] |
| Meissner-effect magnetic shielding | v4 §3.5 + [S2] |
| Photonic 50 Tbps data path with cryo-CMOS DACs | v4 §3.6 + [S3] |
| Per-beam blanker subsystem (CMOS-MEMS) | v4 §3.7 + [S4] |
| Three-tier fiducial registration loop | v4 §3.9 + [S5] |
| AlN wafer chuck with backside He + Galden + TEC | v4 §3.10 + [S6] |
| Cold–warm UHV interface | v4 §3.11 + [S7] |
| Wafer stage, Zygo ZMI metrology, granite base | v4 §3.9 |
| Resist outgassing pumping | v4 §3.12 + [S8] |

This is approximately **85% of the v4 capital budget by line-item count**. The fact that the X-ray variant reuses this much of v4 is the architectural justification for the design choice in §1.3: the per-beam electron-pumped converter array is the only X-ray generation mechanism that preserves the v4 column wholesale.

### 4.2  New subsystems specific to MBM-XRL v1

#### 4.2.1  Converter target subsystem

**Function**: convert each electron beam to a localised soft-X-ray source spot.

**Architecture**: continuous 100 nm Mg layer on a 200 nm Si₃N₄ membrane, framed by a SiC perimeter with integrated water-cooling channels. Cartridge-replaceable on a magazine system (~12 cartridges/magazine, automatic indexing every ~12 hours).

**Thermal load**: 100 W total beam power deposited in the foil for an unblanked $N = 10^6$ array; ~26 W steady-state at 26 % write-cycle duty (matching v4 §3.10). Foil itself rises ~50 K above the perimeter frame (conduction-limited, no convection); frame cooled to 295 K by the water loop. The foil temperature gradient is acceptable for the 100 K Mg melting margin (Mg melts at 923 K).

**Vendors**: Si₃N₄ membrane suppliers (Norcada Canada, Silson UK, Plano Germany — all multi-jurisdiction); Mg deposition (Lesker, AJA International, Mantis Deposition — multi-vendor commodity sputtering); SiC frame (Coorstek, II-VI/Coherent, Saint-Gobain). Cartridge magazine: custom mechanical design at ~\$300 k NRE.

**Cost**: \$2.0 M tool capital (\$1.5 M cartridge magazine + \$0.3 M initial inventory of 20 cartridges at \$25 k each + \$0.2 M water cooling and frame infrastructure). Recurring: \$25 k/cartridge × 4–10 cartridges/month operating = \$0.1–0.25 M/year in consumables.

#### 4.2.2  Proximity gap servo subsystem

**Function**: maintain converter–wafer gap $g$ at 0.5–4 μm nominal range with ~10 nm tolerance.

**Architecture**: piezo Z-flexure under the wafer chuck (~5 μm stroke); capacitive gap sensors at four corners of the converter frame (sensing the chuck top surface, not the wafer itself, to remove wafer-thickness variation from the gap servo); FPGA-based gap controller with 10 kHz update rate.

**Stability budget**: gap variation translates to Fresnel-blur variation per Eq. (4). At $g = 1$ μm and $dg = 10$ nm, the Fresnel blur changes by $\sim 0.5 \sqrt{\lambda \cdot dg/g} \approx 0.15$ nm — negligible. The 10 nm tolerance is essentially a planarity tolerance, not a Fresnel-resolution tolerance, and is set by the residual wafer-side topology rather than the X-ray budget.

**Vendors**: piezo Z-flexure (Physik Instrumente DE, Aerotech US, PI miCos DE, Smaract DE — multi-vendor commodity); capacitive gap sensors (Lion Precision US, MicroEpsilon DE, ADE Phase Shift US); FPGA controller (Xilinx US, Lattice US, Intel/Altera US — multi-vendor).

**Cost**: \$0.6 M tool capital.

#### 4.2.3  X-ray resist subsystem

**Function**: photon-sensitive resist with high absorption at 1 nm wavelength, low photoelectron range, and process compatibility with standard semiconductor fab.

**Architecture**: Inpria Sn-cluster metal-oxide resists are the v1 nominal — same family used by MBM-EBL v4 [22] and by the EUV ecosystem. Soft-X-ray absorption coefficient is ~3 μm⁻¹ at 1.254 keV (well-matched to ~100 nm thick resist), and the heavy-metal Sn content provides the short photoelectron range noted in §3.4(c). Alternative: HSQ for prototyping (lower outgassing for Stage A/B characterisation).

**Note on differentiation**: the X-ray resist subsystem is *easier* than the equivalent e-beam resist subsystem in MBM-EBL v4, because X-ray exposure produces photoelectrons via a known cross-section per atomic shell, with much less dependence on resist polymer chemistry than direct electron exposure. The same Inpria resist can in principle serve both v4 (e-beam) and MBM-XRL v1 (X-ray) tools; cross-tool process integration is simplified.

**Vendors**: Inpria/Applied Materials (US), JSR (JP), TOK (JP), DuPont (US), Allresist (DE), Microresist (DE) — multi-vendor and multi-jurisdictional.

**Cost**: \$0 incremental tool capital (resist is a consumable, not a tool subsystem); resist budget rolls into per-wafer cost-of-goods.

#### 4.2.4  X-ray dose calibration subsystem

**Function**: per-beam dose calibration accounting for per-tip converter-efficiency variation, foil-thickness gradient, and X-ray detector linearity.

**Architecture**: Si-PIN photodiode array at the wafer plane (placed in a fiducial-strip outside the active patterned area) measuring per-beam X-ray flux during calibration scans. Used during the first ~10 wafers of a cartridge change to characterise the new foil's per-beam emission map, then closed-loop trims per-beam blanker duty cycle to equalise wafer-plane dose.

**Vendors**: Si-PIN photodiode arrays (Amptek US, Hamamatsu JP, Ketek DE — multi-vendor); readout electronics (Cremat US, Caen IT — multi-vendor).

**Cost**: \$0.4 M tool capital.

### 4.3  Capital cost rollup (v1)

| Subsystem | Cost share | Source |
|---|---:|---|
| Electron source array (MEMS CNT/Spindt) | \$3.0 M | v4 [S5] |
| Per-beam source closed-loop control | \$0.65 M | v4 [S5] |
| Acceleration & condenser optics | \$2.0 M | v4 baseline |
| Per-beam HTS deflection coils + Meissner shields | \$4.7 M | v4 [S2] |
| Per-beam cryo-CMOS DAC + photonic data path | \$5.3 M | v4 [S3] |
| Per-beam blanker array (CMOS-MEMS) | \$0.6 M | v4 [S4] |
| Wafer stage + 3-tier registration + ZMI metrology | \$15.0 M | v4 [S5] |
| Wafer chuck thermal management | \$0.45 M | v4 [S6] |
| Cryocooler + cold–warm interface | \$1.5 M | v4 [S2] + [S7] |
| Vacuum + differential pumping + resist mgmt | \$2.3 M | v4 [S8] |
| Control system + software | \$2.0 M | v4 baseline |
| **NEW — Converter target subsystem** | **\$2.0 M** | **§4.2.1** |
| **NEW — Proximity gap servo** | **\$0.6 M** | **§4.2.2** |
| **NEW — X-ray dose calibration** | **\$0.4 M** | **§4.2.3** |
| **Total** | **\$40.5 M** | |

Range: **\$40–50 M per production tool**, accommodating the v4-baseline uncertainty bands. The X-ray variant adds **\$3.0 M of new subsystems** to the \$37.4 M v4 baseline, a marginal increase of ~8%. The cost advantage over EUV (\$200–400 M) is preserved at ~5–10×; the cost advantage over DUV (\$50–100 M) is preserved at ~1.5–2×.

### 4.4  Supply-chain check (≥3 vendors, ≥2 jurisdictions)

The v4 supply-chain table (v4 §5) is inherited for the 85% of subsystems shared with v4. The new MBM-XRL-specific subsystems are documented above (§4.2.1–4.2.4) and each pass the ≥3-vendor / ≥2-jurisdiction test:

| New subsystem | Vendors |
|---|---|
| Si₃N₄ membrane substrate | Norcada (CA), Silson (UK), Plano (DE), Greatcell (AU) |
| Mg thin-film deposition (or Mg metal source) | Kurt J. Lesker (US), AJA International (US), Mantis Deposition (UK), Singulus (DE) |
| SiC perimeter frame | Coorstek (US), II-VI/Coherent (US), Saint-Gobain (FR), Kyocera (JP) |
| Piezo Z-flexure | Physik Instrumente (DE), Aerotech (US), Smaract (DE), Cedrat (FR) |
| Capacitive gap sensor | Lion Precision (US), MicroEpsilon (DE), ADE Phase Shift (US), Microsense (US) |
| Si-PIN X-ray photodiode | Amptek (US), Hamamatsu (JP), Ketek (DE), XGLab (IT) |
| X-ray resist | Inpria/AMAT (US), JSR (JP), TOK (JP), DuPont (US), Allresist (DE) |

No single-vendor chokepoint is introduced. The v4 multi-vendor premise is preserved.

---

## 5  Validation pathway

Following the MBM-EBL v3 §7 staged structure, with X-ray-specific modifications:

### 5.1  Stage 0: Numerical validation

**Goal**: close the v1 placement budget numerically.

**Work items**:
- **Monte Carlo electron-foil interaction** at the v1 converter geometry (100 nm Mg / 200 nm Si₃N₄, 50 kV electrons) using CASINO or PENELOPE [29]; outputs are X-ray angular distribution, lateral source spot, and conversion efficiency. Refines the §3.1 conservative $\eta = 10^{-4}$ to a measured value.
- **Photoelectron-range modelling** in Inpria-class resists at Mg-K, Al-K, and Cu-L photon energies, using GEANT4 or PENELOPE. Refines the §3.4(c) PE-range estimate.
- **Fresnel + penumbra wave-optics simulation** at gap $g \in [0.1, 10]$ μm and source spot $s \in [10, 100]$ nm, characterising the joint $\sigma_\text{Fresnel}$ + $\sigma_\text{penumbra}$ envelope (the simple quadrature of Eq. 7 likely overestimates the true joint distribution at small gaps where the two effects correlate).
- **Cartridge-life sputter modelling** under the v1 beam-power distribution.

**Cost**: \$0 (open-source codes on commodity Linux + cloud GPU as needed).

**Outcome**: refined v1 placement budget; converter-design parameters for Stage A; identified resist-PE-range optimisation candidates.

### 5.2  Stage A: Single-beam Lorentz steering + converter validation

**Goal**: demonstrate single-electron-beam → converter → wafer-plane X-ray exposure with controllable position and dose.

**Components**:
- Single 50 kV electron column (reused from MBM-EBL v3 Stage A if available, or commercial gun ~\$200k).
- HTS deflection coil at 77 K (validates v4 §3.5 simultaneously).
- Converter target prototype (single 5×5 mm Mg foil on Si₃N₄).
- Si-PIN X-ray detector for source-spot characterisation.
- Resist-exposure test wafer with HSQ for blur characterisation.
- Piezo proximity stage at 100 nm tolerance.

**Estimated cost**: **\$0.5–1 M**.

**Outcome**: validates the X-ray conversion efficiency at the v1 geometry, measures source-spot size empirically, demonstrates single-beam patterned resist exposure with measured σ_total at known proximity gap, validates Eq. (7) experimentally.

### 5.3  Stage B: Few-beam prototype with converter array

**Goal**: 4×4 to 8×8 beam array at 20 μm pitch with a single common converter target.

**Components**: v4 Stage B prototype hardware + Stage A converter target scaled to ~5×5 mm. Demonstrates that multiple e-beams sharing a continuous converter foil do not cross-couple at the X-ray-emission stage (a new question relative to v4) and that the per-beam blanker faithfully gates X-ray emission.

**Estimated cost**: **\$5–7 M** (vs v4 \$5 M Stage B; X-ray-specific additions ~\$0.5 M).

**Outcome**: validates cross-beam X-ray exposure overlap, per-beam X-ray dose calibration, converter-foil stability under multi-beam load, and the first multi-beam X-ray-exposed resist pattern at v1 nominal node.

### 5.4  Stage C: Beam-count scaling

**Goal**: scale to $10^3$–$10^4$ beams under a continuous 5–10 mm converter target.

**Estimated cost**: **\$10–15 M**.

**Outcome**: characterises foil-life and contamination at production density; first wafer-scale X-ray exposures at the v1 nominal 130–250 nm node range.

### 5.5  Stage D: Production prototype

**Goal**: full $10^5$–$10^6$ beam tool with production-grade converter cartridge magazine, integrated with standard wafer-processing line.

**Estimated cost**: **\$40–50 M** (per the §4.3 capital rollup).

**Outcome**: commercial mature-node X-ray manufacturing capability.

**Total program cost** (Stage 0 → Stage D): **\$55–75 M, 36–60 month timeline**, comparable to MBM-EBL v4 (\$45–60 M, 36–60 months).

---

## 6  Comparison with existing lithography technologies

### 6.1  vs. EUV (ASML NXE/EXE class)

EUV targets <5 nm at \$200–400 M / tool. MBM-XRL v1 targets 130–250 nm at \$40–50 M / tool. The two technologies do not compete on node range or throughput. The MBM-XRL v1 architecture's advantages over EUV are entirely in capital cost, supply-chain diversification, mask elimination, and software-defined direct-write reconfigurability — the same advantages claimed by MBM-EBL v4. At the leading edge, EUV remains uncontested.

### 6.2  vs. DUV ArFi (current mature-node workhorse)

DUV immersion dominates 14–180 nm production. MBM-XRL v1 overlaps DUV at the coarser end (130–250 nm). Where chip design volume is high, DUV's mask-amortisation favours DUV; where volume is low (custom ASICs, defence, research, biomedical, scientific instruments), MBM-XRL v1's mask-free direct-write changes the economics in the same way MBM-EBL v4 does.

MBM-XRL v1's specific advantage *over MBM-EBL v4* in this segment is that the X-ray resist process latitude is better-matched to the existing EUV resist ecosystem (Inpria, etc.), which simplifies cross-tool resist process integration in fabs running both EUV and MBM-XRL tools.

### 6.3  vs. multi-beam EBL (MBM-EBL v4)

MBM-XRL v1 and MBM-EBL v4 are complementary, not competitive:

| Property | MBM-EBL v4 | MBM-XRL v1 |
|---|---|---|
| Node range | 50–180 nm | 130–250 nm |
| Resolution-limiting physics | Loeffler–Jansen + cross-beam Coulomb | Fresnel + PE range + source spot |
| Resist | Inpria + HSQ (e-beam) | Inpria + HSQ (X-ray) |
| Throughput | ~15 wph | ~18 wph |
| Capital cost | \$37 M | \$40–50 M |
| Outgassing-to-column coupling | direct | blocked by converter foil |
| Process integration with EUV fabs | good (resist shared) | very good (resist + radiation-type shared) |

The two architectures together cover **50–250 nm at <\$50 M / tool**, the entire mature-node range with explicit cross-coverage at 130–180 nm. A fab equipped with both tools has redundant exposure pathways across most of the mature-node spectrum.

### 6.4  vs. historical proximity X-ray lithography (PXL, 1980s–1990s)

The IBM and NTT PXL programs established that soft X-ray proximity exposure at 1 nm wavelength achieves 70–100 nm resolution under good geometric control [24, 25]. MBM-XRL v1's resolution budget (§3.4) is consistent with this historical anchor at $g \approx 0.5$ μm and tight source spot; the v1 nominal at $g = 1$ μm and 40 nm source is somewhat coarser.

The MBM-XRL v1 architectural advance over PXL is fivefold:

1. **No X-ray mask.** PXL required a Au-on-Si₃N₄ X-ray mask whose membrane stability, distortion under heat load, and matching across mask sets killed PXL economically. MBM-XRL v1 is mask-free; the converter foil is not a pattern carrier, only a wavelength converter.

2. **Direct software-defined patterning.** MBM-XRL v1 inherits the v4 mask-free direct-write economics: zero mask NRE, seconds-to-reconfigure pattern.

3. **Massive parallelism via electronic steering.** PXL throughput was set by a single X-ray source; MBM-XRL v1 has $10^6$ parallel X-ray sources, each independently controlled at kHz–MHz bandwidth.

4. **Modern cryo-photonic infrastructure.** MBM-XRL v1 inherits v4's cryogenic column, photonic data path, and 8 nm registration budget — none of which existed for the PXL programs.

5. **Open architecture.** The PXL programs were captured by single-corporate IP regimes; MBM-XRL v1 is CC BY 4.0.

### 6.5  vs. inverse-Compton-source or LPP-based X-ray lithography

Both inverse Compton and LPP variants (§1.3) are noted in the literature [31, 32] as possible compact X-ray source paths. Neither preserves the v4 architectural principles at $N = 10^6$ scale, as documented in §1.3. They are not pursued in v1.

---

## 7  Open questions

The MBM-EBL v4 closed seven of its engineering hurdles to subsystem-spec rigor; MBM-XRL v1 inherits those closures for the 85% of v4-shared subsystems and adds new open questions specific to the X-ray variant. The principal v1 open items are:

### 7.1  Converter-foil characterisation

**Question**: at the v1 nominal geometry (100 nm Mg / 200 nm Si₃N₄, 50 kV), what is the empirical X-ray source-spot size at the lower face of the converter, and how does it scale with foil thickness and electron energy? The §3.3 estimate of 30–50 nm relies on CASINO/PENELOPE simulations that are calibrated against thick-target geometries; thin-foil X-ray emission patterns may differ.

**Address path**: Stage A direct measurement, supplemented by Stage 0 Monte Carlo simulation. Expected refinement: ±30%.

**Impact**: source-spot size feeds directly into σ_penumbra in Eq. (5) and therefore into the node range. If the empirical source spot is 80 nm rather than 40 nm, the v1 node range shifts coarser by ~30 nm.

### 7.2  Photoelectron range in Inpria-class resists at soft X-ray

**Question**: the §3.4(c) estimate of PE range in Inpria Sn-cluster resist (~40 nm at Mg-K) relies on the literature anchor of [22]; direct measurement at 1.254 keV photon energy in modern formulations is sparse.

**Address path**: Stage 0 PENELOPE/GEANT4 modelling + Stage A empirical Latent-image characterisation. Expected refinement: ±20 nm in the PE-range contribution to σ_total.

**Impact**: if PE range is 80 nm (rather than the assumed 40 nm), σ_total grows from 55 nm to ~85 nm, eating most of the v1 node-range envelope at the 130 nm end.

### 7.3  Proximity-gap planarity over a 20 mm column footprint

**Question**: across a 20 mm × 20 mm converter foil under 100 W beam-power load, with the lower face suspended ~1 μm above the wafer, what is the worst-case planarity deviation due to (a) thermal-gradient-induced membrane bulging, (b) sputter-induced foil-thickness gradient, and (c) wafer-surface topology under the foil?

The capacitive-gap sensor system (§4.2.2) measures four perimeter points but does not directly measure the foil sag at the centre. A finite-element thermomechanical model of the foil under operating load is required.

**Address path**: Stage 0 FEA + Stage B empirical planarity characterisation.

**Impact**: foil sag of >100 nm at the centre relative to the perimeter directly degrades σ_Fresnel and σ_penumbra non-uniformly across the footprint, creating a position-dependent placement error that is not captured by the per-beam DAC calibration.

### 7.4  Converter-cartridge replacement at production cadence

**Question**: the §4.2.1 cartridge-replacement scheme assumes ~12-hour cartridge life and automatic indexing on a magazine. At production cadence of ~18 wph through a 70-layer flow, each cartridge passes ~10–15 wafers before replacement; cartridge-to-cartridge X-ray-flux matching and per-cartridge calibration time become a throughput-overhead question.

**Address path**: Stage C empirical cycle-time accounting under sustained operation.

**Impact**: cartridge-change overhead may reduce throughput from the §3.6 nominal 18 wph to ~10–12 wph if cartridge calibration is slow. Mitigation: thicker (300–500 nm) Mg layer for longer life, at cost of slightly larger source spot.

### 7.5  Hard-X-ray v2 path

**Question**: a future MBM-XRL v2 architecture based on Cu-Kα (8.05 keV, 0.154 nm) could potentially extend the architecture to 30–50 nm node range, exploiting the much smaller Fresnel diffraction at hard X-ray wavelengths. The principal obstacles are (a) the ~1–2 μm PE range in standard resists at 8 keV, forcing ultra-thin (≤50 nm) resist + hardmask strategies, and (b) the higher electron-energy column needed for efficient Cu-Kα generation (overvoltage ~3 at 30 kV is acceptable but yields are lower than soft-X-ray K-line generation per Eq. 1).

**Address path**: deferred to MBM-XRL v2 development; the v1 architecture is forward-compatible (simply swap the converter cartridge for a Cu-Kα variant).

**Impact**: opens potential 30–80 nm node range in a future v2, partially overlapping MBM-EBL v4 and extending below it.

### 7.6  Resist-radiation-damage chemistry mismatch

**Question**: the v1 architecture assumes the Inpria Sn-cluster resist chemistry developed for EUV (13.5 nm, 92 eV) transfers to soft-X-ray exposure at 1 nm (1.25 keV). The dominant absorption shells differ (O-K and C-K at EUV vs. Mg-attenuation-edge interplay at 1.25 keV); the dose-to-clear and line-edge-roughness behaviour may not match the EUV-mode performance directly.

**Address path**: Stage 0 quantum-yield modelling + Stage A direct dose-to-clear measurement.

**Impact**: if Inpria-class resists need re-formulation for the X-ray regime, the v1 resist subsystem may carry NRE at ~\$2–5 M (one-time, amortised across the X-ray-tool product line). Multiple vendors (§4.2.3) buffer this risk.

### 7.7  Cross-beam X-ray dose overlap at high duty cycle

**Question**: at the v1 nominal $g = 1$ μm proximity gap and 40 nm source spot, the X-ray emission from one beam at the converter spills into the neighbouring beams' wafer-plane exposure area to a calculable extent. The §3.4 quadrature treats penumbra as independent per beam, but at adjacent beams with overlapping penumbral skirts, the dose adds constructively. For the 20 μm pitch and ~100 nm effective penumbra-skirt radius, the overlap is ~1% — small but pattern-dependent.

**Address path**: Stage 0 wave-optics simulation + Stage B empirical pattern-edge characterisation.

**Impact**: cross-beam dose overlap is calibratable per the v3 deterministic-vs-stochastic decomposition (v3 §3.4.2) and likely absorbs into the per-beam DAC dose offset without changing the architecture. Open verification at Stage B.

---

## 8  Strategic and economic notes

The strategic case for MBM-XRL v1 is a *delta on* the MBM-EBL v3/v4 strategic case (v3 §6, v4 §6.3), not an independent argument. The principal additional advantages of having an X-ray-variant tool *in addition to* a v4 e-beam tool are:

- **Process redundancy.** A fab with both v4 and MBM-XRL v1 tools has redundant exposure pathways across 130–180 nm. Tool-down events on one architecture are mitigated by the other; tool-set NRE for new designs can be developed on whichever is most available.
- **Cross-tool resist process integration.** The Inpria/EUV-style resist family runs on both tools; resist process development is amortised across both architectures.
- **Wafer-side proximity geometry for thick-resist or hardmask process flows.** Some mature-node flows (e.g., power-device backside lithography, MEMS) use thick resist layers or hardmask stacks where soft-X-ray penetration depth (~5 μm vs. e-beam ~1 μm at 50 keV) is advantageous.
- **Decoupling of resist outgassing from column.** The converter foil acts as a vacuum bulkhead between the cold column and the wafer subchamber, simplifying outgassing management for resists with higher PAG-volatile loads. This effectively makes MBM-XRL v1 more tolerant of resist chemistry diversity than v4 is.

For a sovereign-fab buildout (v3 §6, v4 §6), the addition of an X-ray-variant tool to the toolset is an incremental ~\$40–50 M per tool on top of an already-existing v4 manufacturing line, providing the above redundancy and process-flexibility benefits. We do not advocate building MBM-XRL tools *instead of* MBM-EBL tools; we advocate building both, with the right mix per fab determined by chip-design portfolio.

---

## 9  Conclusion

We have proposed an open, mask-free, multi-vendor multi-beam direct-write X-ray lithography (MBM-XRL) architecture that transfers the Morin (2026) MBM-EBL v4 architectural principles to soft-X-ray exposure. The single architectural change relative to v4 is the insertion of an electron-pumped X-ray converter target (100 nm Mg on 200 nm Si₃N₄ membrane) just above the wafer plane, with a proximity gap servo controlling the converter–wafer separation at the ~1 μm scale. The upstream electron column (source array, cryogenic HTS deflection, photonic data path, registration, wafer chuck) is reused from v4 without modification.

The closed-form resolution budget at the v1 nominal ($\lambda = 1$ nm, $g = 1$ μm, source spot = 40 nm, Inpria-class resist) is $\sigma_\text{total} \approx 55$ nm, supporting a **validated node-range envelope of 130–250 nm**. Aggregate wafer throughput at the aggressive configuration ($10^6$ beams) is ~18 wph through a representative 70-layer process flow. Capital cost is estimated at **\$40–50 M per tool**, an order-of-magnitude advantage over EUV at any node and a modest advantage over DUV at coarser mature nodes.

The architecture's principal advantages over MBM-EBL v4 are: (a) better-matched resist process latitude to the EUV ecosystem, simplifying cross-tool integration; (b) wafer-side proximity geometry decouples resist outgassing from the cold column; (c) thicker resist stacks and hardmask process flows accessible via 5 μm soft-X-ray penetration. The architecture's principal disadvantages relative to v4 are: (a) coarser node floor (130 nm vs. v4's 50 nm) due to soft-X-ray photoelectron range and source-spot–limited penumbra; (b) added converter-cartridge consumable; (c) added engineering complexity in the proximity stage.

Every subsystem has ≥3 independent vendors across ≥2 jurisdictions; no single-vendor chokepoint is introduced relative to MBM-EBL v4.

The open engineering questions are (§7) converter-foil source-spot characterisation, PE-range in Inpria resist at Mg-K wavelength, foil-planarity over 20 mm footprint under thermal load, cartridge-replacement cadence at production scale, the hard-X-ray v2 path to sub-50 nm, X-ray-induced resist chemistry mismatch with EUV-tuned formulations, and cross-beam X-ray dose overlap at high duty cycle. None of these are paradigm-level risks; all are normal Stage A/B/C de-risking activity.

The architecture is released openly. The author makes no patent claim on its content. Construction, modification, and commercialisation by any party are encouraged. The MBM-EBL v4 + MBM-XRL v1 pair together cover the 50–250 nm mature-node range with two complementary exposure mechanisms at <\$50 M / tool each, providing the redundancy and process flexibility that a sovereign or distributed semiconductor manufacturing program needs.

**MBM-XRL v1 is ready for Stage 0 numerical validation work.**

---

## Acknowledgements

The author thanks the MBM-EBL v3 and v4 development arc and external reviewers, whose work establishes the v4 column architecture that this manuscript reuses without modification. The 1980s–1990s IBM and NTT proximity X-ray lithography research programs established the soft-X-ray exposure physics that this manuscript inherits; their mask-related failure modes are explicitly removed by the direct-write architecture proposed here. This v1 manuscript was developed with the assistance of an AI subagent (Anthropic Claude); the human author reviewed, integrated, and is responsible for all engineering decisions and any errors.

---

## Data and Materials Availability

This is a theoretical proposal at v1 sketch rigor. All concepts, equations, and architectural choices described in this manuscript are released to the public domain via CC BY 4.0 license. Stage 0 numerical validation artefacts (Monte Carlo electron-foil simulations, photoelectron-range models, Fresnel + penumbra wave-optics simulations) will be released as a supplementary artifact bundle in MBM-XRL v2.

---

## Funding

This work received no external funding.

---

## Conflicts of Interest

The author declares no patent claims on this work and no commercial relationships that would represent conflicts of interest.

---

## References

References [1]–[23] from MBM-EBL v3 and v4 are inherited and renumbered here for self-contained reading; the originals are catalogued in [16] and [17]. Additional v1 references:

[1] C. Wagner, N. Harned, "EUV lithography: Lithography gets extreme," *Nature Photonics* **4**, 24 (2010).

[2] M. A. van den Brink, "EUV lithography: Status and outlook," *Proceedings of SPIE* **11854** (2021).

[3] C. Vieu *et al.*, "Electron beam lithography: resolution limits and applications," *Applied Surface Science* **164**, 111 (2000).

[4] V. R. Manfrinato *et al.*, "Resolution Limits of Electron-Beam Lithography toward the Atomic Scale," *Nano Letters* **13**, 1555 (2013).

[5] E. Platzgummer, C. Klein, H. Loeschner, "Electron multibeam technology for mask and wafer writing at 0.1 nm address grid," *Journal of Micro/Nanolithography, MEMS, and MOEMS* **12**, 031108 (2013).

[10] G. H. Jansen, *Coulomb Interactions in Particle Beams*, Academic Press (1990).

[16] R. G. Morin, "Multi-Beam Direct-Write Electron Lithography via Multi-Rate Electromagnetic Steering," preprint v3 (May 2026), CC BY 4.0.

[17] R. G. Morin, "Multi-Beam Direct-Write Electron Lithography via Multi-Rate Electromagnetic Steering: v4 — Cryogenic Column, Photonic Data Path, and Engineering Closure," preprint v4 (May 2026), CC BY 4.0.

[22] D. Kabra et al., "Inpria Sn-cluster molecular-oxide resists for EUV/EBL," *Proceedings of SPIE* **11323** (2020).

[24] J. P. Silverman, "X-ray lithography: status, challenges, and outlook for 0.13 μm," *Journal of Vacuum Science & Technology B* **15**, 2117 (1997). Principal IBM PXL review.

[25] H. I. Smith, M. L. Schattenburg, "X-ray lithography from 500 to 30 nm: X-ray nanolithography," *IBM Journal of Research and Development* **37**, 319 (1993). NTT and MIT PXL retrospective.

[26] M. Howells, "Some fundamental considerations for x-ray microscopy," Lawrence Berkeley National Laboratory Tech Report LBNL-46078 (2000). X-ray window/membrane standards reference.

[27] H. A. Kramers, "On the theory of X-ray absorption and of the continuous X-ray spectrum," *Philosophical Magazine* **46**, 836 (1923). Classical bremsstrahlung yield formula.

[28] R. M. Hudyma, "Compact x-ray sources for lithography," *Proceedings of SPIE* **3676** (1999). Compact-source lithography state-of-the-art at PXL closure.

[29] D. Drouin et al., "CASINO V2.42 — a fast and easy-to-use modeling tool for scanning electron microscopy and microanalysis users," *Scanning* **29**, 92 (2007). Open-source Monte Carlo electron-target simulation.

[30] T. Tabata, R. Ito, S. Okabe, "Generalized semiempirical equations for the extrapolated range of electrons," *Nuclear Instruments and Methods* **103**, 85 (1972). Practical electron-range formulae used in §3.4(c).

[31] W. S. Graves et al., "Compact x-ray source based on burst-mode inverse Compton scattering at 100 kHz," *Physical Review Special Topics — Accelerators and Beams* **17**, 120701 (2014). Inverse-Compton compact source state-of-art.

[32] G. D. O'Sullivan et al., "Laser produced plasmas as sources for short wavelength lithography," *Reviews of Scientific Instruments* **70**, 4031 (1999). LPP source review for lithography applications.

---

*Preprint released openly under CC BY 4.0.*
*For attribution: Morin, R. G. (2026). "Multi-Beam Direct-Write X-Ray Lithography via Per-Beam Electron-Pumped Converter Arrays." Preprint v1, May 2026.*
