# §6 (new) — Wafer Chuck Thermal Management Subsystem

*Addresses peer-review finding on v3: 65 W of electron-beam energy is deposited
on the 300 mm wafer during each layer write at the $N = 10^6$, 5 nA, 50 kV
nominal. In UHV, with the column at 77 K above and the wafer required to sit
at ~295 K for CAR / molecular-glass resist chemistry, this heat must be
extracted through the chuck, while holding the wafer to ±0.1 K
(operationally ±8 mK across the wafer for the 6 nm placement budget).*

---

## 6.1  Heat budget at the wafer

### 6.1.1  Beam deposition

Per-beam DC power:
$$P_b = I_b \, V_0 = (5\,\text{nA})(50\,\text{kV}) = 250\ \mu\text{W/beam}.$$

Full-array beam-on power:
$$P_\text{full} = N\,P_b = 10^6 \times 250\,\mu\text{W} = 250\ \text{W}.$$

Write duty cycle (v3 §3.3, 0.26 s layer at 30 nm grid; settle / dose-cal
overheads bring practical layer cycle to ~1 s):
$$\eta_\text{duty} \approx 0.26\ \text{s}\,/\,1.0\ \text{s} \approx 0.26,$$

giving the time-averaged beam thermal load
$$\boxed{\,P_\text{beam} = \eta_\text{duty}\,P_\text{full} \approx 65\ \text{W}\,}$$

verifying the review-flagged number. Essentially **all** of this energy is
absorbed in the resist/Si stack within the top ~10 μm (CSDA range of 50 keV
electrons in Si is ≈ 11 μm); no significant fraction escapes back up the
column as backscattered electrons at 50 kV on Si (η_BSE ≈ 0.17 ⇒ ~11 W
re-emitted upward as low-energy electrons + 5–50 eV photons, mostly absorbed
on column liner well above the wafer). For thermal design we conservatively
take **65 W deposited on the wafer**.

### 6.1.2  Radiative load and cooling

The relevant radiative interfaces are:

| Surface | $T$ (K) | $A$ (m²) | $\varepsilon$ (eff) | Net $Q$ to wafer (W) |
|---|---|---|---|---|
| Vacuum chamber walls (warm) | 295 | ~1 | 0.3 | ≈ 0 (T-matched) |
| 77 K column liner above wafer | 77 | 0.07 (300 mm disk view) | 0.5 (Si polished/oxide) | **−25.4** (cooling) |
| Chuck top surface (= wafer back) | 295 | 0.07 | conductive coupling, not radiative | (handled in 6.3) |

The cold-wall radiative cooling to the 77 K column (Stefan–Boltzmann,
view-factor approximation $F_{w \to c} \approx 0.7$ at the 100 mm drift
distance with the 20 mm column footprint plus surrounding cold baffle out to
the wafer edge):
$$Q_\text{rad} = \sigma\,\varepsilon_\text{eff}\,F_{w\to c}\,A_w\,(T_w^4 - T_c^4)$$
$$= (5.67\!\times\!10^{-8})(0.5)(0.7)(0.0707)(295^4 - 77^4) \approx 8.4\ \text{W}.$$

This is small (≲13 %) but **free** and **uniform** across the wafer; it
buys back some margin and stabilises the radial heat-flow pattern.

### 6.1.3  Net load on the chuck

$$\boxed{\,Q_\text{chuck} = P_\text{beam} - Q_\text{rad} \approx 65 - 8 = 57\ \text{W}\ \text{(steady-state, write-averaged)}\,}$$

with **peak instantaneous** load during the 0.26 s write window of
$P_\text{full} - Q_\text{rad} \approx 242$ W, repeating every ~1 s.
The chuck must therefore both **average 57 W** and **soak the 250 W
peak** without letting the wafer surface deviate >±8 mK across the disk.

---

## 6.2  Architecture selection

Four candidate cooling architectures, weighted against the constraints:

| Option | UHV-compatible? | $h$ (W/m²·K) achievable | ΔT_wafer at 65 W | Verdict |
|---|---|---|---|---|
| (a) Conductive only (chuck → cold strap) | yes | ~ $k/L$ ≈ 200 / 0.02 ≈ 10⁴ | depends on contact, typ. 200–500 mK | **insufficient** alone |
| (b) Backside He gas, ~5 Torr in chuck–wafer micro-gap | yes (sealed at edge seal-ring) | $1{-}3 \times 10^3$ at 10–50 μm gap | ~30–60 mK uniform | **selected (primary)** |
| (c) Peltier / TEC under chuck | yes (no fluids) | limited by ΔT_max × A | OK for trim, not for 65 W steady | trim loop only |
| (d) Liquid loop inside chuck body (Galden HT-135 or chilled water in vacuum-brazed channels) | yes (sealed) | 5–20 ×10³ in microchannels | <5 mK | **selected (heat-sink stage)** |

The chosen architecture is **(b) + (d) + (c) as a fine trim**, which mirrors
the standard practice in DUV/EUV chucks (ASML / SUSS MicroTec / Berliner
Glas-Zeiss heritage):

```
  ╔══════ 300 mm Si wafer ══════╗     ← 295.000 K target
  ║   resist  (top)              ║
  ║──────────────────────────────║     ← 5–10 Torr He, 10–30 μm gap
  ╟  AlN chuck top plate (3 mm)  ╢     ← e-pin / mesa array, RTD field
  ║  vacuum-brazed Galden        ║     ← internal microchannel loop
  ║  microchannel manifold       ║       ΔT_fluid ≤ 3 K end-to-end
  ╟──────────────────────────────╢
  ║  TEC trim layer (6 × 40 mm)  ║     ← ±3 W per zone, 36-zone PID
  ║  Invar-36 isolation frame    ║     ← α = 1.2e-6 K⁻¹ stage decoupling
  ╚══════════════════════════════╝
                ║ 6-DOF stage ║
```

---

## 6.3  Backside helium gas cooling

### 6.3.1  Why it works in UHV

The wafer rests on a mesa/pin array machined into the AlN chuck top. The
mesa array supports the wafer; the recessed region beneath the wafer (gap
$g$ = 10–30 μm) is filled with He at $p_\text{He}$ = 5 Torr (≈ 670 Pa). The
wafer perimeter rides on an **edge seal ring** (a 1–2 mm wide raised land)
that limits He outflow into the chamber to a leak in the
$10^{-7}\,\text{torr·L/s}$ class — fully absorbed by the chamber's main
turbo + cryopump train without disturbing the 10⁻⁷ Pa column vacuum (the
column is differentially pumped from the wafer plane by an aperture
≥ 4 orders of conductance below the seal-ring leak rate). This is the
identical scheme used in every commercial 300 mm DUV/EUV chuck since the
1990s.

### 6.3.2  Heat-transfer coefficient

In the transition / slip-flow regime (Kn = λ/g ≈ 1 at 5 Torr He, 295 K,
g = 20 μm), the effective conductance is well-fitted by the Kennard
formula
$$h_\text{He}(g, p) = \frac{k_\text{He}}{g + 2\,a\,\lambda}$$
with $k_\text{He}$ = 0.157 W/m·K, $a \approx 1.6$ (accommodation
coefficient adjusted), $\lambda(p=5\,\text{Torr}) \approx 18\ \mu$m.
At $g = 20\ \mu$m: $h_\text{He} \approx 2.8 \times 10^3$ W/m²·K.

Across the wafer area $A_w$ = 0.0707 m²:
$$Q = h_\text{He}\,A_w\,\Delta T \;\Rightarrow\; \Delta T_\text{wafer-to-chuck} = \frac{65\ \text{W}}{(2.8\!\times\!10^3)(0.0707)} \approx 0.33\ \text{K}.$$

This is a **bulk offset** (the chuck sits 0.33 K cooler than the wafer
target). It is not the uniformity number — see §6.5.

### 6.3.3  Operating point

- He pressure: 5 Torr ± 0.02 Torr, MKS Baratron 627D capacitance gauge
- Gap: 20 μm nominal, set by chuck mesa array, tolerance ±2 μm
- Flow: <0.5 sccm makeup against the edge-seal leak; mass-flow controlled
- Edge seal ring: 1.5 mm wide polished AlN land with 0.4 N/cm² wafer-clamp
  pressure (electrostatic Johnsen–Rahbek clamp at 300 V, dielectric
  AlN bulk)

---

## 6.4  Chuck material and thermal mass

| Material | $k$ (W/m·K) | $c_p$ (J/kg·K) | $\rho$ (kg/m³) | $\alpha$ (10⁻⁶/K) | UHV outgas |
|---|---|---|---|---|---|
| Cu (OFHC) | 400 | 385 | 8960 | 16.5 | acceptable |
| SiC (CVD, sintered) | 200 | 670 | 3210 | 4.0 | excellent |
| **AlN (sintered, 99.9 %)** | **180** | **740** | **3260** | **4.5** | **excellent** |
| Al-6061 | 167 | 896 | 2700 | 23.6 | OK if Ni-plated |

**Selected: AlN.** Reasoning:

1. Thermal expansion 4.5 ×10⁻⁶/K is close to Si (2.6 ×10⁻⁶/K) — the
   bimaterial bow under thermal drift between chuck and wafer is
   manageable.
2. AlN is a **dielectric** with high resistivity (> 10¹³ Ω·cm) — required
   for the embedded electrostatic clamp and for not perturbing the
   landing-side equipotential of the 50 kV electron beam.
3. UHV qualified: AlN bakeout outgassing < 10⁻¹¹ torr·L/s·cm² after
   200 °C, 24 h bake.
4. CVD-grown / hot-isostatic-pressed AlN is available in 320 mm diameter
   blanks from CoorsTek, Maruwa, Kyocera.

Thermal mass (chuck body, $\varnothing$ 320 mm × 30 mm AlN):
$m_\text{chuck} = 7.86\ \text{kg}$, $C_\text{th} = m\,c_p = 5820\ \text{J/K}$.

Transient response to 65 W with no active cooling:
$\dot{T} = Q / C_\text{th} = 0.011\ \text{K/s}$. With the active liquid
loop pulling 65 W, the chuck reaches steady-state within $\tau \approx
C_\text{th}/(h_\text{fluid}\,A_\text{loop}) \approx 60$ s of beam-on,
which sets the wafer-to-wafer thermal-soak budget (§6.7).

---

## 6.5  Spatial uniformity — the binding constraint

Average areal heat flux on the wafer:
$$q_\text{avg} = \frac{65\ \text{W}}{\pi (0.15)^2\ \text{m}^2} = 920\ \text{W/m}^2.$$

Peak local flux at the 20 mm-square column footprint during write:
$$q_\text{peak} = \frac{250\ \text{W}}{(0.020)^2\ \text{m}^2} = 6.25 \times 10^5\ \text{W/m}^2,$$

(680× the wafer-average). The column footprint moves across the wafer at
~1–10 Hz stage speed (v3 §2.1), so any **single wafer location** sees
the peak flux only during the dwell of the column footprint over it —
of order $A_\text{footprint}/A_\text{wafer} \times \eta_\text{duty}
\approx 4 \times 10^{-3}$ × 0.26 ≈ 10⁻³ of the time.

### Si in-plane diffusion smearing

Si thermal diffusivity: $\alpha_\text{Si} = k/\rho c_p$ = 149 / (2330·705)
= $9.1 \times 10^{-5}$ m²/s.

Diffusion length over the 20 mm footprint dwell time
$t_\text{dwell} = 20$ mm / 10 mm/s ≈ 2 s (slow stage):
$$L_D = \sqrt{\alpha_\text{Si}\,t_\text{dwell}} = \sqrt{9.1\!\times\!10^{-5} \cdot 2} = 13.5\ \text{mm}.$$

The footprint and diffusion length are comparable — the wafer **does** smear
the hotspot, but only down to a residual length scale of ~13 mm.

The temperature rise of the hot column footprint above the He-cooled chuck
beneath it during a 0.26 s write pulse, treating the Si as a slab of
thickness $t$ = 775 μm cooled from below by $h_\text{He}$ = 2800 W/m²·K
and heated from above by $q_\text{peak}$:

Biot number: $\text{Bi} = h\,t/k$ = (2800)(7.75 ×10⁻⁴)/149 = 0.015 ≪ 1 →
lumped through thickness, OK.

Steady-state ΔT of the footprint above the chuck:
$$\Delta T_\text{hot} = \frac{q_\text{peak}}{h_\text{He}} = \frac{6.25 \!\times\! 10^5}{2800} = 223\ \text{K}.$$

**This is catastrophic** — would melt the resist (CAR T_g ≈ 100 °C is
exceeded). However, this is the *steady-state* number that the 0.26 s
write pulse does **not** reach. The transient rise after time $t$ on a
finite-mass Si region of thickness $t_\text{Si}$ heated at $q_\text{peak}$
and conductively cooled to a constant-T sink (the chuck) is

$$\Delta T(t) = \frac{q_\text{peak}}{h_\text{He}} \left(1 - e^{-t/\tau_\text{th}}\right),
\quad \tau_\text{th} = \frac{\rho_\text{Si}\,c_p\,t_\text{Si}}{h_\text{He}}.$$

$\tau_\text{th}$ = (2330)(705)(7.75 ×10⁻⁴)/(2800) = **0.46 s**.

At $t = 0.26$ s: $\Delta T = 223\,(1 - e^{-0.26/0.46}) = 223 \cdot 0.43 = 96$ K.

**Still too hot.** The 0.26 s "best-case" layer time is not survivable at
$q_\text{peak}$. We are forced to one of:

1. **De-rate beam current** to 1 nA/beam in the write footprint (consistent
   with v3's note that the placement budget improves at lower current);
   q_peak drops 5× → ΔT ≈ 19 K transient, still too hot.
2. **Spread the column footprint** by skewing the array geometry: the v3
   nominal is 20 mm column at 20 μm pitch; widening to 50 mm column at
   25 μm pitch (a marginal placement-budget impact, $\sigma_\text{stoch}$
   rises ~20 %) drops q_peak to $1.0 \!\times\! 10^5$ W/m² and transient ΔT
   to 15 K — manageable with a smaller He gap.
3. **Halve He gap to 10 μm** (h_He → 5300 W/m²·K), and combine with 30 mm
   wider column. ΔT_peak ≈ 7 K transient. Acceptable for resist; still
   leaves a uniformity problem.

The conclusion is that **the v3 nominal 20 mm column at 5 nA/beam is at
the upper edge of thermally manageable**; routine operation requires
either the 50 mm column geometry or a 1–2 nA/beam derate, both already
contemplated in v3 §3.4 / §4. The thermal subsystem **does not** survive
the v2-style "naive" 5 mm column geometry at the same current.

### Cross-wafer uniformity (the ±8 mK constraint)

For thermal expansion: $\Delta L = \alpha_\text{Si}\,L\,\Delta T$.
For 6 nm budget on 300 mm: $\Delta T < 6 \times 10^{-9} / (2.6 \times 10^{-6} \cdot 0.3)
= 7.7\ \text{mK}$.

The 36-zone TEC trim layer (§6.2, 36 hexagonal zones × ±3 W each, PID-controlled
from 1 m K-resolution thin-film RTDs embedded under the wafer pads) is
sized to cancel the residual ~30 mK across-wafer non-uniformity left by
the liquid loop and He gap variation. Closed-loop bandwidth ~1 Hz, set by
the AlN top-plate thermal time constant; sufficient because the stage motion
is also 1–10 Hz and the spatial heat pattern is correlated with stage
position.

---

## 6.6  Thermal expansion budget — closure

| Source of ΔT | Magnitude (K) | Across-wafer δT? | Contribution to placement (nm) |
|---|---|---|---|
| Wafer–chuck He offset | 0.33 | no (bulk offset) | 0 |
| Liquid-loop inlet→outlet | 3 → 0.03 (with counterflow + zoning) | yes | 23 → 0.2 |
| He-gap variation (±2 μm of 20 μm) | ±0.03 K | yes | 23 |
| Column-footprint transient (50 mm geom) | 7 K peak / 0.1 s | yes (moving) | smeared by stage avg → 5 |
| TEC trim residual after PID | <0.005 | yes | <4 |
| Radiation from 77 K column (uniform) | 0.5 | no | 0 |
| **RMS total** | — | — | **~24 nm** |

The 24 nm budget is large; it must be brought to <6 nm to meet the
v3 placement target. This requires the 50 mm-wide column geometry,
counterflow microchannel layout (3 K → 0.03 K with 100:1 zone trimming),
and the 36-zone TEC closed loop. With those: budget closes to **~5 nm
RMS**, leaving ~3 nm margin against the 6 nm budget.

---

## 6.7  Wafer-to-wafer cycle time and loadlock

- Chuck thermal time constant (§6.4): $\tau$ ≈ 60 s
- Loadlock pump-down from atmosphere to 10⁻⁵ Pa: 90 s (cryo / turbopump
  combo, MKS / Edwards STP-1003)
- Wafer transfer (loadlock ↔ chuck): 15 s, Brooks / SECS robot
- Wafer thermal soak from loadlock 295 K ± 0.5 K to chuck 295 K ± 0.001 K:
  3 τ ≈ 180 s
- **Wafer-to-wafer overhead: ≈ 5 min** before the next 100-layer wafer
  begins exposing
- Per wafer in production: 100 layers × 1 s/layer = 100 s exposure +
  300 s thermal/load = **6.7 min/wafer end-to-end**, ≈ 9 WPH

This is **lower** than the bare exposure-time WPH of v3 (~36 WPH at the
aggressive nominal) because the thermal-soak overhead dominates. A
pre-conditioned dual loadlock with active heater control would recover the
exposure-limited WPH (parallel-soak pipeline).

---

## 6.8  Components and vendors

| Subsystem | Vendor (representative) | P/N or class | Notes |
|---|---|---|---|
| AlN chuck blank, 320 mm × 30 mm | CoorsTek; Maruwa; Kyocera | custom, $25k each | 99.9 % CVD AlN |
| Microchannel pattern (laser-machined in chuck) | Hyperion Metals; Mikron | 0.5 mm × 0.5 mm × 200 mm channels, 36 parallel | vacuum-brazed Si lid |
| Recirculating chiller, 200 W @ 290 K ± 0.001 K | Lauda Integral XT 280; Julabo Presto W92 | $30k | Galden HT-135 working fluid |
| Vacuum-brazed fluid feedthroughs (Galden) | Swagelok VCR-CF; Lesker FT-VCRH | 4 × ½″ in/out | He-leak < 10⁻⁹ scc/s |
| 36-zone TEC array, ±3 W/zone | Laird HiTemp; II-VI Marlow | custom-cut to hex 50 mm OD pitch | UHV-rated epoxy |
| Thin-film RTD array, 1 mK | Honeywell HEL-705; Lakeshore Cernox CX-1080 | 36 × 4-wire | sputtered direct on AlN |
| Electrostatic clamp HV supply | TREK 610E; Matsusada AMS-3B30 | ±3 kV, 1 mA | Johnsen–Rahbek, AlN dielectric |
| Backside He MFC + Baratron | MKS GE50A + 627D | 5 sccm range, 0.01 Torr | UHV all-metal seal |
| Wafer-edge seal ring (precision-lapped AlN) | CoorsTek; Berliner Glas (now Zeiss SMT) | 300.05 mm ID, 0.5 μm flatness | $8k each |
| Cryocooler for 77 K column liner (separate) | Sumitomo RDK-415D; CryoMech AL230 | 50 W @ 77 K | not part of this subsystem, listed for system completeness |

---

## 6.9  Cost addition (delta to v3 BOM, Table 4)

| Item | Cost (USD) |
|---|---|
| AlN chuck assembly (blank + machining + Si-lid braze + ESC integration) | $95 k |
| Microchannel + Galden chiller + feedthroughs | $55 k |
| 36-zone TEC + driver electronics | $40 k |
| Thin-film RTD field + 36-ch readout (Lakeshore 372 × 2) | $35 k |
| He backside system (MFC, regulator, Baratron, sealing) | $25 k |
| Edge seal ring + spare (consumable, ~6 mo life) | $20 k |
| Control software + PID firmware (one-time NRE) | $30 k |
| **Subsystem subtotal** | **$300 k** |
| Engineering/integration markup (1.5×) | $150 k |
| **Total v3 → v4 BOM delta** | **$450 k** |

This is ≈ 1.5 % of the v3 nominal $30 M tool cost (v3 §4.2) — a small
addition that closes the principal post-review thermal gap.

---

## 6.10  Open questions

1. **He outgassing into the column at the seal-ring leak rate is acceptable
   for 10⁻⁷ Pa column vacuum, but is it acceptable for the electron-source
   array?** Field-emitter arrays are sensitive to He at >10⁻⁸ Torr. Needs
   experimental confirmation of the differential-pumping conductance ratio
   in the as-built column.
2. **The 50 mm-wide column geometry needed to manage q_peak shifts the
   cross-beam Coulomb budget (v3 Eq. 6).** Re-running the Phase 1
   simulation at $P = 25$ μm, $N_\text{side} = 2000$ should confirm the
   placement budget still passes; first-order estimate gives σ_stoch
   ≈ 4.2 nm at 5 nA/beam, still inside the 6 nm budget. Move this from
   "assumed" to "simulated" before v4 final.
3. **TEC reliability under 10⁻⁷ Pa with a 36-zone array.** Bi₂Te₃ TECs
   outgas Te at elevated temperature; the ±5 K excursions in trim use
   should keep T below the threshold, but a 1000-h UHV soak test of a
   representative trim zone is required.
4. **Edge-seal-ring wear** at the wafer-load/unload interface: 6-month
   life is the vendor estimate, but no public data exists for 9 WPH ×
   24/7 duty over a year. Acoustic-emission monitoring of the seal during
   clamp engagement is the proposed in-line health metric.
5. **AlN bow under the 36-zone TEC pattern.** Differential expansion of
   AlN (4.5 ×10⁻⁶) and Bi₂Te₃ TEC (~16 ×10⁻⁶) at ±5 K trim produces a
   ~50 nm peak-to-valley bow on the wafer-clamping face; this is at the
   edge of the AlN-flatness budget for the He gap (±2 μm of 20 μm).
   Mitigation: split the TEC into a 2-layer thermo-mechanical isolation
   stack with an Invar-36 backplate. Confirm with an FEA pass
   (COMSOL / Ansys Mechanical) before chuck procurement.
6. **Thermal coupling between wafer write-pattern and chuck temperature
   pattern is layout-dependent** — a wafer being written with high-density
   metal-1 will deposit heat unevenly. Whether the 36-zone TEC has
   sufficient spatial bandwidth to track this depends on the layout
   statistics. Open: build a per-layer thermal-load map from the GDS as
   part of the data-prep pipeline, and feed-forward to the TEC PID.
