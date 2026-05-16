# §Y  Per-Beam Blanker Array Subsystem (v4)

*Spec section for Morin (2026) v4 preprint. Closes the middle loop in the
multi-rate control hierarchy: between the inner-loop deflection coils
(§X, 10–100 kHz, Lorentz) and the outer-loop wafer stage (1–10 Hz,
mechanical). The blanker physically deflects unwanted beamlets into a
stop aperture; only ON-beams reach the wafer. $10^6$ blankers at 20 μm
pitch, 1 kHz nominal switching, cryo-compatible at 77 K, UHV.*

## Y.1  Mechanism choice — why electrostatic

Three candidate mechanisms span the design space:

| Mechanism | Switching time | Power / beam | Wear | Cryo @ 77 K |
|---|---|---|---|---|
| Electrostatic plate pair (capacitor) | <1 ns intrinsic, ~10 ns RC-limited | ~10 μW @ 1 kHz | none (no moving parts) | trivial |
| MEMS shutter / micro-mirror | 1–100 μs | μW range | mechanical fatigue at $10^{10}$ cycles | actuator metals fine; gas damping absent in UHV (fine) |
| Magnetic blanker (deflection coil pair) | 1–10 μs (L/R limited) | mW range (resistive) or AC loss (SC) | none | feasible but redundant with §X coils |

At 1 kHz update and 20 μm pitch, **electrostatic plates win on every axis simultaneously**: they are the fastest, the lowest-power, have zero wear, are routinely fabricated by silicon-MEMS processes at sub-μm precision, and have ~50 years of incumbency in single-beam EBL and IMS/MAPPER-class multi-beam tools. MEMS shutters add mechanical fatigue with no compensating advantage at 1 kHz (their reaction-time advantage matters only below ~100 ns, which capacitor blankers also reach). Magnetic blankers replicate the §X deflection-coil function at lower per-channel efficiency. **Selected: electrostatic plate-pair blanker, fabricated CMOS-MEMS, integrated with on-chip HV switch.**

## Y.2  Electrostatic blanker geometry

A pair of parallel plates of length $L_p$ separated by gap $d$, with voltage $V_p$ between them, applies a transverse electric field $E_\perp = V_p / d$ to a beam transiting along the plate axis. For an electron of kinetic energy $V_0 = 50$ kV traversing the plates at velocity $v_z$, the time-of-flight is $\tau = L_p / v_z$, and the transverse momentum acquired gives a deflection angle

$$\theta = \frac{eE_\perp \tau}{p_z} = \frac{V_p L_p}{2 V_0 d}.$$

Rearranged:

$$\boxed{V_p = \frac{2 V_0 d\,\theta}{L_p}.}$$

### Geometry budget at 20 μm pitch

The blanker chip sits in the pitch lattice already locked by the deflection-coil layer (§X). Allocating ~80% of the 20 μm cell to the plate stack and routing/ground guard around it:

| Parameter | Value | Notes |
|---|---|---|
| Plate length $L_p$ | 50 μm | along beam axis; 2.5× the lateral pitch is allowed because the column z-direction is uncongested |
| Plate gap $d$ | 10 μm | clear aperture for a ~10 nm spot with ample alignment margin |
| Beam energy $V_0$ | 50 kV | from v3/v4 column spec |
| Stop-aperture standoff $L_s$ | 5 mm | distance from blanker midplane to stop aperture |
| Stop-aperture hole radius $r_s$ | 5 μm | passes the ON-beam, blocks anything deflected by $\theta \geq r_s / L_s = 1$ mrad |
| Required deflection angle | $\theta = 2$ mrad | 2× margin over stop geometry |
| **Required plate voltage** | $V_p = 2 \cdot 50{,}000 \cdot 10\,\mu\text{m} \cdot 2\,\text{mrad} / 50\,\mu\text{m} = 40$ V | comfortable |

**Headline:** a 40 V swing between plates is sufficient. Practical drivers operate at $\pm 50$ V (one plate grounded, one switched) with margin for tolerance stack-up and to push the deflected beam well off the stop aperture edge.

The 40 V figure is conservative because $L_p$ is generous. If chip-area pressure forces $L_p = 25$ μm, $V_p$ doubles to 80 V; still trivial for CMOS HV processes.

### Bandwidth check

The plate capacitance is $C \approx \varepsilon_0 L_p w_p / d \approx 8.85 \times 10^{-12} \cdot 50\,\mu\text{m} \cdot 15\,\mu\text{m} / 10\,\mu\text{m} \approx 0.7$ fF intrinsic, dominated by stray and pad capacitance to ~0.5–1 pF in practice. With an on-chip switch driving through ~1 kΩ output impedance, the RC time constant is ~1 ns — six orders of magnitude faster than the 1 kHz update rate. Bandwidth is **vastly overprovisioned**; this is what enables future migration to a 10× faster greyscale PWM mode (§Y.8) without redesigning the plate stack.

## Y.3  Driver electronics — per-blanker HV switch

Each blanker plate is driven by one CMOS HV switch. At $V_p = 40$–100 V, the relevant process families are:

| Process / part class | $V_{DS,max}$ | Footprint per channel | Cryo @ 77 K | Vendors |
|---|---|---|---|---|
| 0.18 μm BCD (BiCMOS-DMOS) HV | 80–200 V | ~50 × 50 μm | functional; threshold shifts ~50 mV | TowerJazz/TowerSemi, X-FAB, ams OSRAM, TSMC HV |
| 0.13 μm SOI HV CMOS | 60–120 V | ~30 × 30 μm | functional; mature for cryo readout | GlobalFoundries 8RF/12SOI, ST FD-SOI, Tower SOI |
| GaN HEMT (discrete or integrated) | 100–650 V | ~100 × 100 μm | works to 4 K (literature) | EPC, GaN Systems (Infineon), Navitas, Transphorm |
| HV LDMOS in standard CMOS | 40–80 V | ~25 × 25 μm | as CMOS | TSMC 0.18 HV, SMIC, UMC |

The lattice cell is 20 × 20 μm, which is too small for a full BCD HV switch unless the switch sits **off-axis** in a tiled CMOS substrate below (or above) the plate stack — i.e. a standard "logic-under-plate" stacked-die or CMOS-MEMS arrangement. This is exactly the MAPPER architecture: 49,000-blanker arrays on a CMOS chip with one switch per blanker, routed via TSV or surface metal to a plate on a paired aperture die.

**Cryo-compatibility at 77 K** is well-established for bulk and SOI CMOS down to ~10 K (cf. cryo-CMOS qubit-control papers from Intel Horse Ridge, IMEC's cryo platform, and Google's cryoCMOS readout). Threshold voltages shift by ≲100 mV at 77 K, mobility increases ~2×, and leakage drops; the net effect on a digital switch is *improved* performance. **No reason to keep the switch warm.** Keeping the switch at 77 K eliminates ~$10^6$ HV feedthroughs through the cryostat wall — a decisive architectural simplification.

### Power per switch

CMOS dynamic switching loss per blanker:

$$P_{\text{sw}} = C V_p^2 f \cdot \alpha$$

with $C \approx 1$ pF (plate + interconnect + switch parasitic), $V_p = 100$ V (worst-case full-swing design), $f = 1$ kHz, activity factor $\alpha \leq 1$:

$$P_{\text{sw}} = 10^{-12} \cdot 10^4 \cdot 10^3 \cdot 1 = 10\,\mu\text{W per blanker (worst case, 100% activity).}$$

At typical layer-write activity factors of ~30–50% (most beamlets spend most of their time in one state per local feature):

$$P_{\text{sw,typ}} \approx 3{-}5\,\mu\text{W per blanker.}$$

**Static leakage** in 0.18 μm HV CMOS at 77 K is ~1 nA per device at 100 V — negligible (~100 pW × $10^6$ = 0.1 mW total).

## Y.4  CMOS-MEMS integration

The blanker array is a **stacked-die assembly**:

1. **Plate die (top).** Silicon-on-insulator wafer, ~200 μm thick, with through-wafer trenches forming the 10 μm gaps. Plates are metallised (Au or TiN, ~200 nm). Each cell has two plate electrodes routed to bond pads on the bottom surface.
2. **CMOS switch die (below).** 0.18 μm HV CMOS, one HV switch per blanker plus row/column addressing logic and a small SRAM buffer (1 bit per blanker × ~1000-blanker tile × 4 buffer depth = ~4 kbit per tile) so the L0 serial-link layer (see §7 datapath) can stream patterns without per-blanker addressing every frame.
3. **Stop-aperture die (bottom).** Refractory-metal (Mo or W) sheet with patterned 5 μm pinholes aligned to each beam axis. Thermally isolated from the blanker stack (see §Y.5).

The plate die and CMOS die are joined by hybrid bonding (Cu-Cu thermocompression or oxide-bonded with TSVs), the standard ≤10 μm-pitch wafer-bond technique used in CMOS image sensors and HBM stacks.

**Tile size.** A single CMOS die at modern 300 mm reticle is up to 26 × 33 mm, accommodating $1300 \times 1650 = 2.1 \times 10^6$ blanker cells at 20 μm pitch — *more than the entire array on a single die.* In practice the column footprint is ~20 × 20 mm, so the entire $10^6$-blanker array fits on **one** CMOS die plus **one** plate die plus **one** stop-aperture die. This is the cleanest possible integration: no tile-to-tile alignment, no inter-tile dead zones.

**Vendor candidates (CMOS-MEMS integration):**

| Vendor | Country | Capability |
|---|---|---|
| CEA-Leti | FR | Combined CMOS + MEMS + hybrid bonding pilot line |
| Imec | BE | 300 mm CMOS + MEMS R&D foundry |
| Fraunhofer IPMS | DE | CMOS-MEMS for micro-mirror arrays (DLP-class) |
| SUSS MicroTec (process) | DE | Wafer-bond / lithography tooling, fabless support |
| TowerSemi | IL/US | HV BCD foundry runs |
| GlobalFoundries 12SOI | US/SG | HV SOI CMOS at 300 mm |
| Silex Microsystems | SE | MEMS pure-play, hybrid-bond capable |
| Teledyne DALSA | CA | MEMS + HV CMOS for imaging |

≥3 independent vendors per critical step (HV CMOS, plate-die MEMS, hybrid bond) across ≥3 jurisdictions.

## Y.5  Stop-aperture geometry and thermal management

The stop aperture is a thin (~10 μm) refractory-metal sheet placed 5 mm below the blanker midplane. Each beam axis passes through a 5 μm-radius hole. ON-beams pass through (slight collimation effect, beneficial). OFF-beams strike the surrounding metal and are absorbed.

**Material stack:**

- Base: Mo or W foil (10 μm), chosen for low sputter yield at 50 kV and for melting point (Mo: 2890 K; W: 3695 K).
- Surface coating: pyrolytic graphite or amorphous carbon (~100 nm), low secondary-electron yield (~0.4 vs 1.1 bare W) to minimise scattered secondaries re-entering the column.
- Conductive path to ground: continuous metal sheet, brazed to a copper heat-spreader frame, frame DC-grounded through the column ground bus.

**Charging.** Stopped 50 kV electrons embed ~5 μm into Mo; without a conductive path, the surface would float to ~$V_0$. With a continuous grounded metal substrate beneath the carbon coating, charge drains in $RC \ll 1$ μs for any realistic geometry. *Not a budget concern given proper grounding.* The graphite coat itself is semi-conductive ($\sim 10^{-5}\,\Omega\cdot\text{m}$), so even the surface layer drains fast.

**Heat load** — see §Y.7.

## Y.6  Power budget at 77 K (electrical only — thermal beam load in §Y.7)

Per-blanker switching power: ~5 μW typical, 10 μW worst-case.

Across $10^6$ blankers:

| Term | Power |
|---|---|
| Dynamic switching ($CV^2f$, $\alpha=0.5$, $V=100$ V) | **5 W** |
| Static leakage at 77 K | 0.1 mW |
| Row/column addressing + SRAM buffer (digital, ~10 nW per cell) | 10 mW |
| Serial-link receivers (L0 datapath, ~$10^3$ inputs at ~10 mW each) | 10 W |
| Margin (1.5×) | 7.5 W |
| **Total at 77 K** | **~22 W** |

**Compare with §X 77 K budget (~2.1 W for coils + radiation + conduction).** Adding the blanker stack roughly **10×'s** the cold-side electrical load. The §X cryocooler line item must be re-sized:

- §X selected 2 × Cryomech PT-90 (30 W @ 77 K each) for N+1 redundancy at 2.1 W load.
- §Y adds ~22 W at 77 K.
- Combined load: ~24 W; single PT-90 has 30 W lift, so 2 × PT-90 still provides N+1 redundancy. **No cryocooler count change required, but the margin shrinks from 6× to 1.25× on a single unit.** Recommend upgrading to PT-180 (~50 W @ 77 K, ~\$45 k) for healthy margin: net \$30 k addition to the v3 → v4 capital delta.

### Alternative: warm switches, cold plates

If the CMOS dissipation proves uncomfortable at 77 K, the architecture supports moving the HV switches outside the cryostat at the cost of $\sim 10^6$ HV feedthroughs (or $\sim 10^3$ multiplexed bus feedthroughs with cold demultiplexers, which puts most of the cold dissipation back). **Recommendation:** keep switches cold. The 22 W is well inside the budget and avoids the feedthrough explosion.

## Y.7  Beam shadow heating in the stop aperture

Each OFF-beam deposits its full beam power into the stop aperture:

$$P_{\text{beam}} = I_b V_0 = 2\,\text{nA} \cdot 50\,\text{kV} = 100\,\mu\text{W per OFF-beam.}$$

(Some sources quote 250 μW with the higher v3 current spec; using v4 derated 2 nA = 100 μW. The numbers below are linearly scalable.)

Worst-case 50% duty cycle (half the beams OFF at any instant):

$$P_{\text{stop,total}} = 0.5 \cdot 10^6 \cdot 100\,\mu\text{W} = 50\,\text{W deposited into the stop aperture.}$$

This is **hot**, but the stop aperture is *not* part of the 77 K stage — it sits below the column, can be thermally tied to a room-temperature water-cooled assembly, and is mechanically decoupled from the cold mass by a vacuum gap + low-emissivity radiation baffle. 50 W into a 20 × 20 mm × few-mm copper plate with active water cooling is a textbook problem (heat flux 12.5 kW/m², well below the ~100 kW/m² that ordinary cold plates handle).

**Radiation from the warm stop aperture back to the cold column.** With a polished-Au radiation baffle ($\varepsilon \approx 0.03$) between the 295 K stop plate and the 77 K column over the 5 mm standoff:

$$Q_{\text{rad,back}} \approx 0.03 \cdot 5.67 \times 10^{-8} \cdot 4 \times 10^{-4} \cdot (295^4 - 77^4) \approx 5\,\text{mW.}$$

Negligible compared to the 22 W internal load.

**Cooling assembly:** standard semicon-industry water-cooled chuck (Watlow, ATS, Lytron, Boyd) at ~\$15 k including coolant manifold. The same vendor list as the wafer chuck.

## Y.8  Greyscale dose modulation — PWM option

The 1 kHz nominal rate uses the blanker as a pure on/off switch. Dose modulation (analog grey level for proximity-effect correction, edge smoothing, etc.) is achieved by **PWM the blanker at higher rate**. A 4-bit grey scale (16 levels) requires:

$$f_{\text{PWM}} = 16 \cdot f_{\text{base}} = 16\,\text{kHz.}$$

At 16 kHz the RC bandwidth (1 ns) is still 7 orders of magnitude in excess. The switching power scales linearly with frequency:

$$P_{\text{sw,PWM}} = 16 \cdot P_{\text{sw,1 kHz}} = 80\,\text{W at 77 K worst case.}$$

This **does** exceed the PT-180 budget. Two responses:

1. Restrict PWM-mode operation to a sub-fraction of beamlets at any instant (typical edge-smoothing affects ≤10% of beams per layer), keeping the time-averaged frequency at ~1.6 kHz equivalent and the cold load at ~10 W.
2. Use 2-bit (4-level) PWM at 4 kHz baseline — sufficient for proximity correction in most layers, only ~5× the on/off baseline load, fits in PT-180 with margin.

The architecture supports either; the choice is driven by the resist process window (§ v4_resist_outgassing), not the blanker hardware. **Recommendation:** specify 2-bit greyscale as the v4 standard, with 4-bit reserved as an optional high-fidelity mode.

## Y.9  Vendor list summary (≥3 per critical item)

| Item | Vendors |
|---|---|
| HV CMOS foundry (40–100 V) | TowerSemi, X-FAB, GlobalFoundries 12SOI, TSMC HV 0.18, SMIC HV |
| Plate-die MEMS | CEA-Leti, Imec, Silex Microsystems, Fraunhofer IPMS, Teledyne DALSA |
| Hybrid wafer bond (Cu-Cu, oxide+TSV) | EVG, SUSS MicroTec, TEL, Applied Materials, ASMPT |
| Refractory stop-aperture stock (Mo, W foil) | Plansee, H.C. Starck, A.L.M.T., Goodfellow, Edgetech |
| Stop-aperture coating (pyrolytic carbon) | Toyo Tanso, Mersen, SGL Carbon, Poco Graphite |
| Water-cooled stop-plate chuck | Watlow, Lytron (Boyd), ATS, Wakefield-Vette |
| Cryocooler upgrade (PT-180) | Cryomech (US), Sumitomo SHI (JP), Edwards (UK), Brooks (US) |

All critical items: ≥3 independent suppliers, ≥2 jurisdictions. No new chokepoint over §X.

## Y.10  Cost estimate

| Item | Qty | Unit | Subtotal |
|---|---|---|---|
| HV CMOS switch die (one die for $10^6$ blankers, custom NRE amortised) | 1 | \$50 k (production) | \$50 k |
| Plate-die MEMS wafer | 1 | \$30 k | \$30 k |
| Stop-aperture (Mo + carbon) | 1 | \$10 k | \$10 k |
| Hybrid bond + packaging | 1 lot | \$50 k | \$50 k |
| Water-cooled stop-plate chuck | 1 | \$15 k | \$15 k |
| Cryocooler upgrade (PT-90 → PT-180) | 2 | \$15 k delta | \$30 k |
| NRE: custom HV CMOS-MEMS mask set + bring-up | 1 | — | \$3.5 M |
| Integration + test + 20% contingency | — | — | \$0.8 M |
| **Net production unit addition** | | | **~\$185 k** |
| **Net NRE (first article)** | | | **~\$4.3 M** |

Per-blanker IC + plate amortised: \$185 k / $10^6$ = **\$0.19 per blanker** — squarely in the \$0.10–\$0.50 per-blanker range cited in the deliverable spec. Custom CMOS-MEMS NRE of ~\$4.3 M fits the \$2–5 M envelope. **No re-baseline of the v3 \$30–35 M tool cost** — the blanker stack adds <2% to total capital.

## Y.11  Open engineering questions

1. **Plate-die through-wafer alignment to deflection-coil layer.** The blanker stack must register to the §X coil array within ~1 μm to keep ON-beams centred on the stop-aperture holes. The coil layer is fabricated on sapphire (cryogenic, lithographed); the blanker is on Si (CMOS-MEMS, bonded warm). Differential thermal contraction from 295 K → 77 K is ~0.2 mm across a 20 mm column at the relative CTE difference (sapphire 5 ppm/K, Si 2.6 ppm/K). This is **far larger than the alignment budget** and must be absorbed by either (a) lithographing both layers with pre-distortion that anticipates the cold deformation, or (b) using a single substrate material (Si throughout, sacrificing the sapphire optical transparency that §X doesn't actually need). Recommended path: silicon substrate for both layers.

2. **Dielectric breakdown across 10 μm in UHV at 77 K.** Vacuum hold-off at small gaps follows the Paschen-defying micro-discharge regime; published data is mostly at 295 K. Need to validate ≥200 V hold-off at 10 μm gap, 77 K, in pristine UHV, with carbon-coated electrodes.

3. **Field-emission from plate edges.** At $V_p = 100$ V across 10 μm, $E = 10^7$ V/m — below Fowler-Nordheim threshold for clean metal but within reach for sharp lithographic features. Edge rounding (>200 nm radius) required in the plate-etch process.

4. **Cosmic-ray / X-ray induced single-event upsets in cold SRAM buffer.** The blanker SRAM tile holds the current frame of beam-on/off state. A single bit flip writes the wrong pattern over the next 1 ms. Need either ECC on the buffer or refresh from L0 link at 1 kHz. Cryo-CMOS SRAM SEU rate at 77 K is roughly equal to warm SRAM (charge collection physics, not thermal); design for ECC.

5. **Long-term sputter erosion of the stop aperture.** At 50 W deposited 50% duty, even modest sputter yield (~$10^{-3}$ atoms/electron for W at 50 keV) erodes ~10 nm/year over the patterned hole edges. Periodic re-machining or sacrificial coating refresh on a ~5-year maintenance interval. Cost driver in tool lifecycle, not in spec.

6. **Greyscale linearity.** PWM dose modulation assumes the beam-current within a single PWM cycle is constant. Drift in source emission, transit-time effects, and beam-current droop during long ON pulses will distort the integrated dose. Calibration via in-situ Faraday-cup periodic check (already in the v3 metrology spec) is sufficient at 4-level PWM; 16-level PWM may require closed-loop dose feedback per beamlet, which is **not** budgeted in the current architecture and would push complexity hard. Decision deferred to Phase 2.

## Y.12  Summary

The middle-loop blanker is the **cheapest** subsystem in the v4 column: \$185 k production, \$4.3 M NRE, no cryocooler escalation, no new vendor chokepoint, one die per layer of a three-layer hybrid-bonded stack that fits inside the existing 20 × 20 mm column footprint. The dominant uncertainty is thermal-contraction alignment to the §X coil layer; the resolution path (silicon substrate throughout) is cheap. The dominant power line item is HV CMOS switching at 5 W cold, easily absorbed by upgrading the §X PT-90 cryocoolers to PT-180. The dominant heat *load* (50 W of stopped-beam power) lives outside the cold mass on a standard water-cooled chuck. Greyscale dose modulation up to 2-bit (4-level) is free in the architecture; 4-bit grey is available at moderate cost. No show-stoppers.
