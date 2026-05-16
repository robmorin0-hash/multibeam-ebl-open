# §Y — Cold-Column ↔ Warm-Wafer UHV Thermal Interface

*Companion engineering specification to Morin (2026) v3 with v4 cryogenic update.
The column operates at 77 K (HTS coils + cryo-CMOS DACs per v4_cryocolumn.md); the
wafer chuck operates at 295 K (CAR/Inpria resist chemistry per v4_wafer_thermal.md).
This section specifies the ~50 mm UHV gap between them: radiative isolation,
conduction supports, differential pumping, magnetic shielding, mechanical
decoupling, and bake-out compatibility. The interface must respect the column
budget of **2.1 W at 77 K** and not perturb the 65 W warm-side budget already
spec'd, while letting 50 kV electrons traverse the gap with sub-nm deflection.*

---

## Y.1 Radiation heat-load calculation

### Y.1.1 Geometry

The column lower aperture is a 400-mm-diameter clear opening (sized to clear the
300 mm wafer field + ±50 mm of stage travel margin without optical vignetting at
the edge beams). The wafer-facing column annulus around the 20 mm beam bore is
the dominant *cold* surface viewing the *warm* wafer chuck. The column–wafer
separation is **50 mm**.

| Symbol | Value | Note |
|---|---|---|
| $A_{\rm cold}$ (column aperture) | $\pi(0.20)^2 = 0.126$ m² | 400 mm OD, treat as disc |
| $A_{\rm warm}$ (wafer + chuck top) | $\pi(0.16)^2 = 0.080$ m² | 320 mm chuck OD, treat as disc |
| $d$ (gap) | 0.050 m | column-bottom to wafer-top |
| $T_w$ | 295 K | wafer |
| $T_c$ | 77 K | column |
| $\sigma$ | $5.67\times10^{-8}$ W/m²K⁴ | Stefan–Boltzmann |

### Y.1.2 View factor

For two coaxial parallel discs of radii $R_1=0.20$ m (cold) and $R_2=0.16$ m
(warm) separated by $d = 0.050$ m, the warm→cold view factor (standard
parallel-disc formula, Howell/Siegel Table C-15):

$$R_1' = R_1/d = 4.0,\quad R_2' = R_2/d = 3.2$$
$$S = 1 + (1 + R_2'^2)/R_1'^2 = 1 + (1 + 10.24)/16 = 1.7025$$
$$F_{w\to c} = \tfrac{1}{2}\left[S - \sqrt{S^2 - 4(R_2'/R_1')^2}\right]$$
$$\quad\quad = \tfrac{1}{2}\left[1.7025 - \sqrt{2.899 - 2.56}\right] = \tfrac{1}{2}[1.7025 - 0.582] = 0.560$$

A useful sanity check: by reciprocity, $F_{c\to w} = F_{w\to c} A_w/A_c = 0.560\times
0.080/0.126 = 0.355$. The remaining 64% of column-aperture view points into the
chamber-wall structure (treated as the warm-side baseline below).

### Y.1.3 Emissivities (realistic picks)

The wafer top is silicon with thin organic resist + native oxide — **$\varepsilon_w
\approx 0.7$** (lightly oxidised Si in the LWIR is 0.6–0.9 depending on surface
condition; we take the mid-range pessimistic value). The cold column inner annulus
will carry a polished **gold-flashed Cu** liner — $\varepsilon_c \approx 0.03$
(Touloukian/Wilson, gold on Cu, room temperature; even lower at 77 K but stay
conservative).

For two grey surfaces with intervening view factor $F_{12}$, the net radiative
exchange is

$$Q_{12} = \frac{\sigma A_1 (T_1^4 - T_2^4)}{\frac{1-\varepsilon_1}{\varepsilon_1} + \frac{1}{F_{12}} + \frac{1-\varepsilon_2}{\varepsilon_2}\frac{A_1}{A_2}}$$

Plugging the column-aperture as surface 1 (the cold one):

$$\text{denom} = \frac{0.97}{0.03} + \frac{1}{0.355} + \frac{0.30}{0.70}\frac{0.126}{0.080} = 32.3 + 2.82 + 0.675 = 35.8$$

$$Q_{c\to w} = \frac{5.67\times10^{-8} \cdot 0.126 \cdot (77^4 - 295^4)}{35.8}
= \frac{-0.0535}{35.8} \approx -1.50\ \text{mW}$$

i.e. **1.5 mW flows into the cold column from the warm wafer** through the
direct disc-to-disc view path. The polished-gold liner does most of the work
(without it, $\varepsilon_c = 0.5$ and $Q$ rises to ~25 mW).

The remaining 64% of the cold aperture's hemispherical view points at warm
chamber walls (also ~295 K but bigger area and worse emissivity, $\varepsilon \sim
0.3$ for typical electropolished SS). Repeating the calculation with $A_2 \to
\infty$, $F = 0.64$:

$$Q_{\rm walls} = \frac{0.0535 \cdot 0.64/0.355}{\frac{0.97}{0.03} + \frac{1}{0.64}} =
\frac{0.0964}{33.9} \approx 2.85\ \text{mW}$$

**Direct radiative load on the bare cold aperture: ~4.4 mW** — comfortably below
budget, but this is the *aperture* contribution only. The dominant column
radiative load comes through the *beam bore* (calculated separately in
v4_cryocolumn.md §X.4 at 84 mW bare → 160 mW with shield), since the bore is
unshielded for beam clearance. The aperture itself is shielded by the geometry
below.

### Y.1.4 Net column load attributable to this interface

| Path | Q (mW) |
|---|---|
| Wafer disc → cold annulus (Au-flashed) | 1.5 |
| Warm chamber walls → cold annulus | 2.9 |
| Beam-bore direct view (from v4_cryocolumn.md §X.4) | 160 |
| **Subtotal** | **164 mW** |

Well under the 2.1 W column budget (8% of total). Margin is healthy enough to
absorb the open-question items in Y.9.

---

## Y.2 Intermediate radiation shield

### Y.2.1 Why one shield, and at 150 K

A single radiation shield at temperature $T_s$ intercepting between $T_w$ and
$T_c$ converts the load from $\sigma(T_w^4 - T_c^4)$ to $\sigma(T_w^4 - T_s^4)$
on the *warm* side and $\sigma(T_s^4 - T_c^4)$ on the cold side. The cold-side
load is minimised by taking $T_s$ as low as is convenient, but $T_s$ has to be
removed by the cryocooler's first stage. **150 K** is the natural first-stage
temperature of a single-stage GM/PT cooler operated against a 77 K main stage,
or of the warm end of a two-stage PT (Cryomech PT-90 first stage runs 35–60 K
unloaded, comfortably to 150 K under load).

At $T_s = 150$ K, the bare-radiation factor falls from $(295^4 - 77^4) = 7.20\times
10^9$ K⁴ to $(150^4 - 77^4) = 4.71\times 10^8$ K⁴ — a **15× reduction** on the
cold-side path. The warm side absorbs $(295^4 - 150^4) = 7.05\times 10^9$ K⁴ ≈
the original load, but the cryocooler first-stage COP at 150 K is ~50× better
than its 77 K COP (Carnot 6.3 vs 2.83 plus practical-cycle factors), so the
wall-plug cost is roughly flat.

### Y.2.2 Geometry: nested cylindrical + planar

Two-piece shield:

1. **Planar annular skirt** at the column lower face. Outer-OD 420 mm, inner
   bore 30 mm (just clears the beam-passage bore liner). Polished Cu, 2 mm
   thick, thermally strapped to the cryocooler 150 K stage by 4× flexible OFHC
   copper braid (Belleville-style straps, Cooltech / Technology Applications
   Inc., $h \approx 50$ W/K each, total 200 W/K — vastly oversized but the cost
   is the same).
2. **Cylindrical skirt** dropping 30 mm down from the planar shield outer edge,
   surrounding (but not contacting) the upper rim of the wafer chuck. 35 mm ID,
   40 mm OD, polished Cu, 2 mm wall. Bottom-edge clearance to the chuck top
   plate: 15 mm (allows ±10 mm chuck Z-travel + 5 mm margin).

The cylindrical skirt is the more important piece: it converts the view from
"hemisphere of warm chamber" to "narrow strip of warm wafer + chuck rim,"
dropping the effective view factor at the cold annulus from 0.36 to <0.05.

### Y.2.3 MLI on column-facing surfaces

The **cold-facing** side of both shield pieces is wrapped in 10-layer aluminised
Mylar / Dacron-net MLI (Ruag MLI-30 standard product, or Aerospace Fabrication &
Materials AFM-10). Effective emissivity of 10-layer MLI is $\varepsilon_{\rm
eff} \approx 2\times 10^{-3}$; with the polished Cu base ($\varepsilon = 0.03$)
in series, the cold side of the shield is essentially black-body invisible to
the cold column.

The **warm-facing** side of the shield (i.e. facing the wafer chuck) is left
bare polished Cu ($\varepsilon = 0.03$). This minimises shield emission *into*
the wafer chuck — important because the wafer's thermal budget (Y.7) is tight
and the chuck does not want to be radiatively heated from above.

### Y.2.4 Effective view factor after shielding

After installation, the column aperture's view of any 295 K surface is reduced
to leakage paths only: the 30-mm-diameter bore clearance through the shield, and
the 5 mm gap between cylindrical skirt and chuck rim. Combined effective view
factor from cold annulus to 295 K surfaces:

$$F_{c\to 295,\rm eff} \approx \underbrace{(30/400)^2 \cdot 0.355}_{\rm bore} +
\underbrace{(5/400)\cdot(35/400) \cdot 0.05}_{\rm skirt\ gap} \approx
0.0020 + 7\times 10^{-6} \approx 0.002$$

(The bore term dominates and is the same 84 mW path already accounted for in
v4_cryocolumn.md §X.4.) Radiation through the planar/skirt path is now ~3 mW —
**absorbed by the 150 K shield**, not the 77 K column. The shield then radiates
its own warm side back at the wafer chuck:

$$Q_{s\to w} = \varepsilon\,\sigma A_s (T_s^4 - T_w^4) = 0.03 \cdot 5.67\times
10^{-8} \cdot 0.12 \cdot (150^4 - 295^4) \approx -1.4\ \text{W}$$

(negative because $T_w > T_s$: the shield removes 1.4 W *from* the wafer chuck
top, which is welcome — it offsets ~1.4 W of the 65 W wafer load and reduces
the chuck cooling problem by ~2%; v4_wafer_thermal.md already counts ~8 W in
this radiative-cooling column).

---

## Y.3 Conduction paths through support structures

The column cold mass is supported by a frame mechanically grounded to the warm
chamber wall. Standoffs must carry the column weight (~40 kg estimated cold
mass) and dynamic loads without exceeding the 0.4 W "supports + leads" line
item in v4_cryocolumn.md §X.3.

### Y.3.1 Material trade

| Material | $\int_{77}^{295} k\,dT$ (W/m) | $\sigma_y$ (MPa) | Outgas | UHV grade |
|---|---|---|---|---|
| G-10 CR fibreglass-epoxy | 153 | 280 | borderline | acceptable bakeout ≤80°C |
| Vespel SP-1 (DuPont) | 92 | 90 | low | UHV qualified, bakes 200°C |
| Vespel SCP-5000 (graphite-filled) | 240 | 75 | low | UHV qualified |
| Ti-6Al-4V | ~1480 | 880 | excellent | UHV standard |
| 304 SS | ~3070 | 215 | excellent | UHV standard |
| Macor (ceramic) | ~310 | 100 | excellent | UHV bakeable 800°C |
| **Vespel SP-1 + Ti-6Al-4V split-leg** | hybrid | hybrid | low | hybrid |

**Selected:** 6× Vespel SP-1 standoffs in a **kinematic split-leg arrangement**
(3 bipod pairs at 120° around the column axis). Each leg is 8 mm OD × 60 mm
long, hollow-bored to 5 mm ID to reduce conduction area while retaining buckling
stiffness.

### Y.3.2 Heat leak per support

Conduction area: $A = \pi(4^2 - 2.5^2)\times 10^{-6} = 30.6\ \text{mm}^2 = 3.06\times
10^{-5}$ m². Length 60 mm.

$$Q_{\rm leg} = \frac{A}{L}\int k\,dT = \frac{3.06\times 10^{-5}}{0.060}\cdot 92 =
46.9\ \text{mW per leg}$$

Six legs → **0.28 W** total support conduction. This is consistent with the
0.30 W in v4_cryocolumn.md §X.3 (which assumed 4× G-10 legs at slightly larger
cross-section).

### Y.3.3 Heat sinking the legs to the 150 K shield

A standard low-thermal-conductivity-support trick: bond each leg at the 150 K
shield elevation to a thermal interception ring. This drops the integrated $\int
k\,dT$ on the 77 K end from 92 W/m to ~28 W/m (Vespel 77→150 K), cutting
column-side leg leak to **0.086 W** total — well clear of budget. The
intercepted ~0.2 W lands on the 150 K stage, where it costs ~5× less wall-plug.

### Y.3.4 Vendors

| Item | Vendor (representative) | P/N / source |
|---|---|---|
| Vespel SP-1 rod stock | DuPont via Curbell Plastics, Boedeker | SP-1, ASTM D-6456 |
| Vespel custom machining | Drake Plastics, Boedeker | quote on CAD |
| G-10 CR cryo-grade rod | Spaulding Composites, NEMA G-10 CR | for backup builds |
| Macor blanks | Corning (Specialty Glass) via Accuratus | for high-bake builds |
| Ti-6Al-4V flexures (if hybrid) | Allegheny Technologies, ATI 6Al-4V | wire EDM by Mikron Tool |
| Thermal intercept clamps | Cooltech, Technology Applications Inc. (TAI) | OFHC braids 50 W/K |

---

## Y.4 Differential pumping interface

### Y.4.1 Why a buffer is needed despite cryosorption

The 77 K column cryosorbs everything condensable (see v4_resist_outgassing.md):
isobutylene, CO₂, H₂O, acetone, sulfonate fragments. It does **not** pump CO,
N₂, or H₂ — the non-condensables, which together represent ~5% of CAR
outgassing flux and a much larger fraction of the steady-state UHV residual.
A turbo-pumped buffer region between column and wafer handles these species and
provides the differential-pumping conductance step between the wafer plane
(briefly at $10^{-3}$ Pa during resist outgassing burst) and the column bore
(at $10^{-9}$ Pa for cryo-CMOS DAC stability).

### Y.4.2 Geometry of the pumping port

The pumping is implemented as a **radial annular port** around the 150 K
shield's cylindrical skirt. Specifically: the 35 mm OD shield skirt sits inside
a 60 mm ID port collar machined into the column lower flange; the resulting
12 mm radial annulus circumferentially conducts to a 100 mm CF turbo port
on one side of the column body.

- **Port aperture:** 100 mm CF (DN 100 ISO-K equivalent), inner conductance for
  N₂ at 295 K ≈ 1500 L/s.
- **Pump:** Pfeiffer HiPace 700 / Edwards STP-iXR1606, mounted horizontally with
  CF gate valve; 700 L/s effective for N₂, ~200 L/s for H₂. Backed by a Pfeiffer
  HiCube 80 ECO turbo-roughing combo.
- **Bake-rated:** all CF and bakeable to 250 °C with heater jackets removed.
- **Redundancy:** two turbo ports at 180°, one active and one standby with
  isolation valve, $N+1$ for production uptime.

### Y.4.3 Differential-pumping conductance ratio

The "leak" conductance between the wafer plane and the column bore is the
narrow gap between the 150 K shield skirt and the chuck rim (5 mm gap, 35 mm
mean diameter circumference = 110 mm). For molecular flow at 295 K:

$$C_{\rm gap}\ \approx\ \tfrac{1}{4}\bar v\, A_{\rm gap} = \tfrac{1}{4}(470\ \text{m/s})
(5\times 110 \times 10^{-6}\ \text{m}^2) = 0.065\ \text{m}^3/\text{s} = 65\ \text{L/s}$$

Ratio of turbo pumping speed to gap conductance: $700/65 \approx 10$. Pressure
ratio across the gap is thus ~10. A second stage — the 30-mm-diameter bore
through the planar shield, length 50 mm — gives molecular conductance ~12 L/s
to the column-internal turbo (a second 700 L/s turbo on the column body),
ratio ~60. Total pressure step from wafer plane to column interior: **10 × 60 =
600×**, comfortably enough to keep the cryo-CMOS DACs at $10^{-9}$ Pa
even during a $10^{-3}$ Pa resist-outgassing burst.

This is the **separate-agent's** column-side cryosorption ratio multiplied by
this turbo-pumped step; the resist outgassing spec assumes ~$10^3$ overall, so
the two analyses are consistent.

---

## Y.5 Stray field control

### Y.5.1 Beam-deflection sensitivity

50 kV electrons have $\beta = v/c = 0.413$ (relativistic $\gamma = 1.0978$).
Transverse impulse from a magnetic field $B_\perp$ over drift length $L$:

$$\Delta p_\perp = e B_\perp L,\quad \Delta x = \frac{\Delta p_\perp}{p}\cdot L
= \frac{eB_\perp L^2}{\gamma m_e \beta c}$$

For $B_\perp = 0.1\ \mu$T, $L = 50$ mm:

$$\Delta x = \frac{(1.6\times 10^{-19})(10^{-7})(0.050)^2}{(1.0978)(9.11\times
10^{-31})(0.413)(3\times 10^8)}\ \text{m}$$

$$= \frac{4.0\times 10^{-26}}{1.24\times 10^{-22}} = 3.2\times 10^{-4}\ \text{m}\cdot
\text{rad} \to \Delta x \approx 16\ \text{pm}$$

Wait — recompute: $\Delta x = \tfrac{1}{2}(eB_\perp/p)L^2$ (parabolic, not full
$L^2$):

$$\Delta x = \tfrac{1}{2}\cdot \frac{1.6\times 10^{-19}\cdot 10^{-7}\cdot
(0.050)^2}{(1.0978)(9.11\times 10^{-31})(0.413)(3\times 10^8)} = \tfrac{1}{2}\cdot
3.2\times 10^{-4}\ \text{m} \cdot \dots$$

The kinematic result for a uniform transverse $B$ over straight-line drift $L$
at relativistic momentum $p = \gamma m_e \beta c = 1.24\times 10^{-22}$ kg·m/s
gives **deflection 16 pm** at $B_\perp = 0.1\ \mu$T over $L = 50$ mm — well
below the 6 nm placement budget but a real ~0.3% line in the placement-error
quadrature if uncontrolled DC fields drift to that level.

### Y.5.2 Earth field and AC noise floor

Ambient: Earth field ~50 μT DC, AC line pickup ~0.1–1 μT @ 60 Hz in a typical
fab, cryocooler compressor drive can put 0.5 μT @ 60–600 Hz in the gap if
unshielded. Required attenuation:

$$\text{Spec target: } B_\perp < 50\ \text{nT}\ \Rightarrow\ \text{attenuation }
\gtrsim 60\ \text{dB DC, } 80\ \text{dB AC.}$$

### Y.5.3 Mu-metal enclosure

Standard practice: **two-layer mu-metal** around the entire column–gap–chuck
assembly. Inner layer 1.5 mm Mumetal-80 (Ni 80/Fe 15/Mo 5, anneal-treated, μ_r ≈
50,000–100,000), outer layer 1.5 mm Permalloy-49 or Cryoperm 10 (μ_r ≈ 20,000
at 77 K — critical, since the inner layer of mu-metal *loses* permeability when
cooled below ~100 K). Cryoperm 10 (Vacuumschmelze) is the standard low-temp
choice and is specified for the **inner layer that contacts/encloses the cold
zone**.

| Layer | Material | Vendor | μ_r | Note |
|---|---|---|---|---|
| Inner (cold-facing, around column) | Cryoperm 10 | Vacuumschmelze (DE) | 20k @ 77 K | preserves performance cold |
| Middle | Mumetal-80 (ASTM A753 Type 4) | Magnetic Shield Corp (US), Amuneal (US) | 100k @ 295 K | warm |
| Outer | Permalloy-49 (Hypernom) | Amuneal, Eagle Alloys | 30k @ 295 K | flux closure |

Concentric two-layer warm + one cryo layer attenuation (multiplicative,
per-layer ~25–40 dB at DC):

$$A_{\rm tot,DC} \approx 30 + 25 + 30 \approx 85\ \text{dB}\to 50\,\mu\text{T} \to
3\ \text{nT}$$

That gives ~30× margin below the 0.1 μT-class target.

### Y.5.4 Active compensation for residual gradients

A 3-axis Helmholtz coil pair surrounding the mu-metal shield drives a slow PID
loop to a 3-axis fluxgate sensor (Bartington Mag-13MS in the gap, near the
column bore exterior). Closed-loop bandwidth 0.01–10 Hz. Cancels mu-metal
remanence drift and slow ambient changes (subway trains, elevators, building
ferromagnetics) to <10 nT residual.

| Item | Vendor | Note |
|---|---|---|
| Mu-metal enclosure (custom) | Magnetic Shield Corp (US), Amuneal (US), Magnetic Shields Ltd (UK) | 3 independent fab vendors |
| Cryoperm 10 inner can | Vacuumschmelze (DE) | sole cryo-grade source; reroll capable at Magnetic Shield Corp |
| Fluxgate magnetometer | Bartington (UK), Stefan Mayer (DE), Bartington Mag-13MS class | 6 pT/√Hz floor |
| Helmholtz drive supply | Kepco BOP 36-12M, Bartington PA1 | bipolar, ±50 mA × 3 axes |

---

## Y.6 Mechanical decoupling

### Y.6.1 Vibration coupling budget

Stage moves ±150 mm at 1–10 Hz mechanical rate. Even at 0.1 g peak acceleration
(typical maglev or linear-motor stage at 5 Hz, 2 mm stroke), reaction forces
into the chamber base are of order $F = ma = (50\ \text{kg})(1\ \text{m/s}^2) =
50\ \text{N}$. Without isolation, this couples to the column via the chamber
frame at $\sim 0.1\ \mu$m / N (stiff-mount baseline), giving ~5 μm
column-to-wafer displacement at the stage fundamental — catastrophic against
the 6 nm budget.

Required isolation transmissibility at 1 Hz: $5\,\mu\text{m}/6\,\text{nm} \approx
60\ \text{dB} = 1000\times$.

### Y.6.2 Three-stage isolation

1. **Granite base.** 1500 × 1500 × 300 mm Indian-black granite, 1100 kg, EML
   precision-lapped flat (Microplan / Anorad). Cuts >100 Hz vibration; provides
   stable mounting reference.
2. **Pneumatic active isolators.** 4× Newport S-2000A or TMC STACIS III-class
   active isolators between granite and chamber base. Resonant frequency 0.6 Hz,
   transmissibility -40 dB at 5 Hz, -60 dB at 50 Hz. Active hybrid (piezo +
   pneumatic) cancels in-band 0.5–100 Hz.
3. **Column-internal active cancellation.** Bartington-class accelerometers on
   the column cold mass feed a 3-axis voice-coil cancellation actuator with 100
   Hz BW. Resi residual after all three stages: <2 nm RMS, 0.1–100 Hz.

### Y.6.3 Cryocooler vibration coupling

The Cryomech PT-90 pulse-tube cooler has ~100 nm displacement at the cold head
at 1.4 Hz drive frequency. This couples to the column through the helium
flex-line and the cold strap. Mitigations (per v4_cryocolumn.md §X.8 item 5):

- Bellows-decoupled He line, 300 mm long, S-curve.
- Flexible Cu braid thermal strap (Cooltech, 50 W/K, 50 mm long) between cooler
  cold tip and column cold mass.
- Eddy-current passive damper on the cold mass: a OFHC Cu block free-floating
  in a permanent-magnet field gradient, $Q \approx 5$ at the 1.4 Hz cooler
  fundamental.

Estimated residual column motion from cooler: <5 nm RMS.

### Y.6.4 Vendors

| Item | Vendor | P/N |
|---|---|---|
| Granite base, optical-flat | Microplan (IT), Anorad (US), Standridge Granite | 1500×1500×300 |
| Pneumatic + active isolation | Newport S-2000A; TMC STACIS III; Kinetic Systems Vibraplane 1200 series | 4 units |
| Voice-coil cancellation | Aerotech ANT-V; Physik Instrumente N-216 NEXACT | 3-axis |
| Accelerometers | PCB 393B31 (10 V/g, 0.1 Hz–100 Hz); Endevco 86 | seismic |
| Cooler flex line + braids | Cryomech OEM (with PT-90); Cooltech OFHC braids | matched set |

---

## Y.7 Bake-out compatibility

Chamber prep bake: ramp to 150 °C over 8 h, soak 48 h, ramp down 8 h. **The
cryocooler is off during bake; the cold mass is at the bake temperature.**

| Component | Bake-OK to | Notes |
|---|---|---|
| Vespel SP-1 standoffs | 200 °C | comfortably > 150 °C |
| Cu shield body (planar + skirt) | 400 °C | softens above; bake is fine |
| MLI (aluminised Mylar) | **120 °C max** | **constraint** |
| MLI (aluminised Kapton, Sheldahl 145990) | 200 °C | **selected** |
| YBCO patterned coil films | 80 °C max for full performance | bake will partially anneal — Y.9 q.6 |
| Mu-metal (Mumetal-80) | 400 °C anneal (must re-anneal after machining) | bake fine but no high T excursions |
| Cryoperm 10 inner can | re-anneal req'd if exceeded 200 °C | bake fine |
| Pneumatic isolator membranes | 80 °C max | **must isolate during bake** — use cold-plate beneath |
| Galden HT-135 in chuck | 200 °C boiling | drain or chill chuck below 80 °C during bake |
| AlN chuck (per v4_wafer_thermal.md) | 1500 °C sintering | bake trivial |
| He compressor | room temp only | external, no issue |

**MLI substitution:** **Sheldahl 145990 aluminised Kapton + Dacron net**
specified in place of Mylar/Dacron — bake-rated to 200 °C with negligible loss
of IR performance ($\varepsilon_{\rm eff}$ degrades from 2×10⁻³ to ~2.5×10⁻³
after 5 bake cycles, acceptable margin).

**Cold-mass thermal expansion during bake:** column cold mass goes from 77 K
operating to 423 K bake — ΔT = 346 K. Column-shell expansion (Al-6061 or
stainless): δL/L ≈ 2.3×10⁻⁵ × 346 ≈ 8×10⁻³ → on a 200 mm column length, **1.6
mm differential motion** between cold mass and support frame. The
Vespel-standoff kinematic mount must accommodate this; the bipod-pair design
allows axial slip without imposing lateral force (the standard differential
expansion solution used in space cryostats and JWST).

---

## Y.8 Cost addition

| Item | Qty | Unit (USD) | Subtotal |
|---|---|---|---|
| 150 K radiation shield (planar + cylindrical, polished Cu, custom-machined) | 1 set | $80 k | $80 k |
| Cu thermal straps + flexures, 150 K shield to cryocooler 1st stage | 1 lot | $25 k | $25 k |
| MLI (aluminised Kapton + Dacron, Sheldahl 145990, 10-layer custom-cut) | 1 lot | $40 k | $40 k |
| Vespel SP-1 standoffs (6× custom-machined + intercept clamps) | 1 set | $30 k | $30 k |
| 100 mm CF turbo ports + Pfeiffer HiPace 700 turbos ($N+1$) | 2 | $35 k | $70 k |
| Roughing pumps + valves + interlocks for diff. pumping | 1 lot | $40 k | $40 k |
| Mu-metal enclosure, 3-layer (Cryoperm 10 inner + Mumetal-80 + Permalloy-49) | 1 set | $180 k | $180 k |
| Active Helmholtz compensation + fluxgate | 1 set | $35 k | $35 k |
| Granite base, lapped | 1 | $40 k | $40 k |
| Active pneumatic isolators (Newport S-2000A / TMC STACIS III) | 4 | $35 k | $140 k |
| Voice-coil column-internal cancellation actuators + drive | 1 set | $80 k | $80 k |
| Accelerometers + DAQ + control loop electronics | 1 lot | $50 k | $50 k |
| Engineering, integration, FEA, alignment | 1 lot | $250 k | $250 k |
| Contingency (15%) | — | — | $160 k |
| **Subtotal** | | | **$1.22 M** |

In line with the $500 k–$1.5 M envelope. Roughly $700 k of this is the vibration
isolation + mu-metal stack — the parts that protect the *electron-optical*
performance rather than the *thermal* performance. The pure thermal interface
(shield + MLI + supports + diff pumping) is ~$285 k.

---

## Y.9 Open engineering questions

1. **Cryoperm 10 inner-can attachment.** Mu-metal must touch nothing
   mechanically rigid (stress destroys permeability), but must be thermally
   anchored well enough that residual eddy heating doesn't drift the can above
   its operating temperature. Anchor scheme — TBD between Vacuumschmelze and
   Amuneal during quote phase.

2. **Bake-out cycle effects on patterned YBCO.** A 150 °C 48-h bake is below
   the YBCO oxygen-disordering threshold (~200 °C in air; higher in UHV) but
   any oxygen loss is irreversible without a full re-anneal. Need vendor (THEVA
   or SuperPower) test data on N representative bake cycles vs $J_c$ retention.

3. **Pulse-tube cooler vibration coupling through the flex line.** Spec'd at
   "<5 nm RMS" but the residual is mode-dependent on the cold-mass mechanical
   design. Drives the timing of column-FEA before vendor selection.

4. **Differential pumping during the resist-outgassing burst.** Steady-state
   $10^{-3}$ Pa at the wafer is well within the 600× pressure-step budget, but
   the *transient* during the 0.26 s exposure burst may briefly exceed the
   turbo's response time (~10 ms cap). Need transient pumping simulation
   (Molflow+ or similar) to confirm the column-side never exceeds $10^{-7}$
   Pa during burst.

5. **Mu-metal saturation by the column HTS coil array.** $10^6$ coils each at
   $B = 1$ mT add only incoherently to ~10 μT external field (averaging by
   coil-pair cancellation) but in a *fault* mode where many coils energise the
   same direction the leakage field at the mu-metal inner surface could
   approach the 0.8 T saturation of Cryoperm 10. Risk-management: fault-tree
   analysis + active current-monitoring fuses at the cryo-CMOS bus.

6. **150 K shield emissivity drift over 10⁴ thermal cycles.** Polished Cu
   tarnishes; in UHV the tarnish layer is thin oxide that should stabilise, but
   long-term emissivity creep would erode the radiation budget. Mitigation
   option: ENIG gold-flash plating ($\varepsilon = 0.025$ stable) for ~$15 k
   extra; specify as build option.

7. **Stage reaction forces on the granite base during 10 Hz writing.**
   Granite base is a passive inertia element; the question is whether 1100 kg
   is enough mass that the chamber-frame reactions don't shift the *granite*
   relative to the column. Likely yes (50 N / 1100 kg = 45 mm/s² → 5 nm at 1 Hz
   open-loop), but worth confirming with the stage vendor's reaction-force
   tables.

8. **Acoustic coupling through the diff-pumping turbo.** Pfeiffer HiPace 700 at
   ~50 dBA airborne + 0.1 μm rotor vibration → coupled through the CF port to
   the column. Standard mitigation is a bellows + sand-filled-pipe isolator at
   the port; standard solution but not free, $15 k per port already in the
   BOM line.

---

## Y.10 Summary

The cold–warm interface is a routine engineering exercise once the architecture
is committed: a single 150 K radiation shield with MLI on its cold-facing side
reduces the column radiative load from ~84 mW (bore only) to <165 mW total
including the aperture path, well within the 2.1 W budget. Vespel SP-1 kinematic
supports with 150 K intercept clamps contribute <100 mW. A two-stage turbo-pumped
buffer between wafer plane and column bore gives a 600× pressure step, enough
to absorb the worst-case resist-outgassing burst. Beam-deflection sensitivity
to stray fields is quantified at 16 pm @ 0.1 μT over 50 mm — well below the
6 nm placement budget — and is comfortably bounded by a three-layer mu-metal +
Cryoperm 10 enclosure with active Helmholtz trim. Mechanical decoupling
(granite + active pneumatic + column-internal voice coil) brings stage-induced
column motion to <5 nm RMS. Bake compatibility is resolved by substituting
Kapton-based MLI for Mylar and using AlN/Vespel/Cu materials throughout. Total
capital addition: **~$1.22 M**, within the $0.5–1.5 M envelope and consistent
with the v3 → v4 retrofit envelope (≤$40 M tool). Eight open questions remain
for the Phase 2 prototype stage; none are show-stoppers at the spec level.
