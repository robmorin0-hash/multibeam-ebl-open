## §X  Cryogenic Column Subsystem (v4 architectural revision)

The v3 architecture placed $10^6$ Lorentz deflection coils at 20 μm pitch in a 20 mm × 20 mm × ~100 mm column operating in UHV. Peer review (post-v3) flagged two coupled problems that no amount of room-temperature engineering resolves:

1. **Thermal infeasibility.** $10^6$ normal-metal coils each dissipating ~1 mW (the minimum to push a few mA through a 20-μm-pitch micro-coil at the required slew rate) deposit ~1 kW into a 20 mm × 20 mm × 100 mm volume in UHV. With no convective cooling and a radiative dissipation budget of order $\sigma T^4 A \approx 10$ W at 295 K from the column's outer surface, the column would run away thermally on millisecond timescales.
2. **Magnetic crosstalk.** At 20 μm pitch a copper-cored coil energised to 1 mT leaks ~10–100 μT into its nearest neighbours (roughly 20–40 dB attenuation by geometry alone), which is comparable to the deflection signal itself. μ-metal shielding is not patternable at 20 μm pitch and saturates well below 1 T anyway.

Both problems collapse if the column is cooled to 77 K (LN₂) and the coils plus inter-coil walls are made of a high-temperature superconductor (HTS). Resistive heating goes to zero, and the Meissner effect provides perfect (to ppm) magnetic screening from any patternable HTS sheet. This section specifies the resulting cryogenic column to the level needed for capital-cost estimation and vendor qualification.

### X.1  Superconducting coil material

| Material | $T_c$ (K) | $J_c$ @ 77 K, self-field | Form factor | Notes |
|---|---|---|---|---|
| NbTi | 9.2 | not SC at 77 K | wire | Excluded — needs liquid He |
| Nb₃Sn | 18.3 | not SC at 77 K | wire/tape | Excluded — needs liquid He |
| MgB₂ | 39 | not SC at 77 K | wire | Excluded — works only below ~25 K |
| **YBCO** (REBCO) | 93 | $2{-}5 \times 10^{10}$ A/m² | 2G coated tape | **Selected** |
| BSCCO-2223 | 110 | $\sim 1 \times 10^{10}$ A/m² | 1G tape | Backup; lower $J_c$ at 77 K |

At 77 K only YBCO-class HTS materials are superconducting at all; the LTS options are confirmed excluded. YBCO 2G coated conductor is the mainstream choice and is what every commercial HTS magnet program (fusion, MRI, fault-current limiters) now uses.

**Coil geometry.** A wound solenoid is impractical at 20 μm pitch — the bend radius of even thinned YBCO tape (~50 μm) exceeds the pitch. Two options remain:

- **Planar spiral (lithographed YBCO film on sapphire/MgO).** YBCO is deposited by PLD or MOCVD onto a 500-μm sapphire wafer, then patterned by ion-mill or wet-etch into spiral coils at 20 μm pitch. This is the same process used for HTS microwave filters (Superconductor Technologies, STI) and HTS SQUID arrays. Achievable line/space ~2 μm, well below the 20 μm pitch.
- **Stacked-pair Helmholtz planar coils**, one on each face of a thin sapphire wafer, giving a quasi-uniform $B_\perp$ across the 5 mm beam-passage length. This is the proposed geometry.

**Field capability at 77 K.** For a planar spiral coil of $N = 30$ turns, mean radius $\bar r = 8$ μm, carrying current $I$, the on-axis field at the geometric centre is

$$B_z \approx \frac{\mu_0 N I}{2 \bar r}.$$

To reach $B_\perp = 1$ mT (v3 representative; the 5 mT "envelope" cited in §X is the worst-case slew target, not the nominal operating point) requires $I \approx 0.42$ A. The cross-section of a 2-μm-wide × 0.5-μm-thick YBCO trace is $10^{-12}$ m²; at $J_c = 2 \times 10^{10}$ A/m² (conservative 77 K self-field figure for commercial 2G tape, derated 2× for thin-film patterning) the trace carries 20 A, **48× the required current**. The 5 mT worst-case still leaves 9.6× margin. The geometry is comfortable at 77 K with conservative $J_c$.

**Vendor candidates for the YBCO source material:**

| Vendor | Country | Product | Notes |
|---|---|---|---|
| SuperPower (Furukawa) | US/JP | 2G HTS wire, SCS4050 | Industry standard; thin-film deposition service available |
| American Superconductor (AMSC) | US | Amperium 2G | Long-length tape; sub-licenses film deposition |
| SuperOx | RU/EU | 2G HTS tape, films-on-demand | Sells custom YBCO-on-sapphire films |
| Faraday Factory Japan | JP | 2G HTS tape | Spinout of SuperOx; redundant supplier |
| Fujikura | JP | 2G HTS tape (FESC) | Independent supply chain |
| Shanghai Superconductor | CN | 2G HTS tape | Export-controlled in some jurisdictions |
| THEVA | DE | YBCO-on-sapphire films | Long history as PLD service for filter-makers |

Six independent suppliers across four jurisdictions. No chokepoint.

### X.2  Magnetic crosstalk shielding via Meissner screen

Each 20 × 20 μm coil cell is bounded on its four lateral faces by a thin YBCO sheet ("Meissner screen") deposited on the inter-coil wall. Below $T_c$, the screen expels all magnetic flux: surface currents in the screen exactly cancel the normal component of $B$ at the screen face, with the residual leakage set only by the London penetration depth $\lambda_L$ and the screen thickness $t$.

For a screen of thickness $t \gg \lambda_L$, the field on the far side decays as

$$B_\text{leak} / B_\text{source} \;\approx\; e^{-t/\lambda_L}.$$

For YBCO at 77 K, $\lambda_L \approx 0.2$ μm in the $ab$-plane. A 10-μm-thick screen gives

$$B_\text{leak}/B_\text{source} = e^{-10/0.2} = e^{-50} \approx 2 \times 10^{-22},$$

i.e. **attenuation of roughly 440 dB**, dominated entirely by other leakage paths (over the top/bottom of the screen, through pinhole defects in the deposition). Defect-limited real-world attenuation for HTS shields measured in SQUID and dark-matter experiments is 80–120 dB [Reim et al., Krautz et al.]. Even at the pessimistic 80 dB figure, the 20 μm-neighbour crosstalk goes from ~−30 dB (geometry alone) to ~−110 dB — completely below the 16-bit DAC LSB ($-96$ dB). **Crosstalk is no longer a budget item.**

Patterning is straightforward — the same PLD/MOCVD + etch process used for the coils deposits the inter-coil wall film in the same lithography pass.

### X.3  Cryocooler selection and thermal budget at 77 K

Heat load on the 77 K stage breaks into four sources. Each is estimated for the 20 mm × 20 mm × 100 mm column with a 50 mm working-distance gap to the warm wafer.

**(a) Radiation from 295 K outer cryostat wall.**  The cold-mass radiative area is the column lateral surface plus end caps, $A_\text{cold} \approx 4 \times (0.02 \times 0.1) + 2 \times (0.02)^2 = 8.8 \times 10^{-3}$ m². With a 30-layer MLI blanket (effective $\varepsilon \approx 5 \times 10^{-4}$):

$$Q_\text{rad,wall} = \varepsilon \sigma A (T_h^4 - T_c^4) \approx 5\times 10^{-4} \cdot 5.67\times 10^{-8} \cdot 8.8\times 10^{-3} \cdot (295^4 - 77^4) \approx 1.9 \text{ mW.}$$

**(b) Conduction down support structures.** Assume 4 × G10 fibreglass support legs, each 5 mm × 5 mm × 50 mm. Integrated thermal conductivity of G10 from 77 K to 295 K is $\int k\,dT \approx 150$ W/m. Heat leak:

$$Q_\text{cond} = 4 \times \frac{A}{L} \int k\,dT = 4 \times \frac{2.5\times 10^{-5}}{0.05} \times 150 \approx 0.30 \text{ W.}$$

Add ~0.1 W for instrumentation wiring and DAC return lines (small-gauge phosphor bronze or manganin, ~$10^6$ channels × ~100 nW each = 100 mW; this is dominated by the bus structure, not by individual leads, since channels are time-multiplexed onto serialised buses with $\sim 10^3$ physical wires crossing the boundary).

**(c) AC losses in the coils.** See §X.5 below — budget $\boxed{0.5\text{ W}}$ at 100 kHz worst-case duty.

**(d) Radiation from the 295 K wafer through the 50 mm gap.** See §X.4 — budget $\boxed{0.16\text{ W}}$ with an intermediate 150 K shield, or $\boxed{1.3\text{ W}}$ without one. The intermediate shield is mandatory.

**Total 77 K heat lift required:**

| Source | Power |
|---|---|
| Radiation (MLI wall) | 0.002 W |
| Conduction (supports + leads) | 0.40 W |
| AC losses (coils @ 100 kHz, 1 mT) | 0.50 W |
| Wafer-side radiation through bore (with 150 K shield) | 0.16 W |
| Margin (2×) | 1.06 W |
| **Total** | **~2.1 W @ 77 K** |

With 2× engineering margin: design to **4–5 W lift at 77 K**.

**Cryocooler trade.** Two families dominate the 77 K / few-watt regime:

| Vendor | Family | Cycle | Lift @ 77 K | Vibration | Unit cost (2026) |
|---|---|---|---|---|---|
| Sumitomo (SHI) | RDK-415D | GM | 1.5 W @ 4 K (or ~40 W @ 77 K w/ single-stage equiv.) | High | \$35 k |
| Sumitomo SHI | CH-110 | GM single-stage | 25 W @ 77 K | Medium | \$20 k |
| Cryomech | PT415 | Pulse-tube | 1.5 W @ 4 K | **Low** | \$55 k |
| Cryomech | AL325 | GM single-stage | 25 W @ 77 K | Medium | \$22 k |
| Brooks (CTI) | Cryodyne 1050 | GM | ~30 W @ 77 K | Medium | \$25 k |
| Edwards (Sumitomo OEM) | rebadged RDK | GM | as above | as above | \$25 k |

For a multi-beam EBL column, **vibration is the dominant trade**. GM coolers produce 5–50 μm peak-to-peak displacement at the cold head from displacer reciprocation at 1–2 Hz, which translates directly into beam placement error at the wafer plane unless heroic isolation is added. Pulse-tube coolers eliminate the moving displacer at the cold head and have measured residual vibration of 100 nm or less.

**Selection: Cryomech PT-90 pulse-tube** (≈ 30 W @ 77 K, single-stage, ~\$30 k) or equivalent. One unit covers the entire column with 6× margin. Specify two units in active redundancy ($N+1$) for production-tool uptime: total cryocooler capital ≈ \$60 k.

### X.4  Thermal isolation to the 295 K wafer

The column terminates ~50 mm above the wafer chuck. The wafer must stay at 295 K (CAR resist constraint). The column-facing wafer area visible through the column bore is the bore footprint $\approx (20\text{ mm})^2 = 4 \times 10^{-4}$ m².

Direct view-factor radiative load on the 77 K column from the 295 K wafer:

$$Q_\text{bore} = \varepsilon_\text{eff} \sigma A (T_h^4 - T_c^4) \approx 0.5 \cdot 5.67\times 10^{-8} \cdot 4\times 10^{-4} \cdot (295^4 - 77^4) \approx 84 \text{ mW.}$$

With a polished-Au bore liner ($\varepsilon \approx 0.03$) on the column side and intermediate **150 K radiation shield** at the column exit (thermally tied to the cryocooler's first stage or a dedicated 150 K stage):

- Wafer → 150 K shield: 1.3 W (absorbed by the warm cryocooler stage at low COP cost)
- 150 K shield → 77 K column: 0.16 W

This 150 K intercept stage is included in the cryocooler budget above. Off-the-shelf two-stage GM/PT coolers provide it natively.

**MLI on the column outer surface:** 30-layer aluminised-Mylar/Dacron-net blanket (standard Ruag or Aerospace Fabrication & Materials product). Trivial integration; effective emissivity 5e-4.

### X.5  AC loss budget for 10–100 kHz switching

Even superconductors dissipate when carrying time-varying transport current, principally via hysteretic vortex motion in the YBCO and eddy currents in the normal-metal stabiliser/substrate. For 2G coated conductor at 77 K, measured AC loss per unit length scales as [Grilli et al., 2014; Stavrev et al., 2002]:

$$P_\text{AC}/\ell \sim \frac{f B_\text{a}^2 w}{\mu_0} \cdot g(I/I_c)$$

where $w$ is the tape width and $g(I/I_c)$ is a Norris/Brandt-form factor $\sim 0.01$–$0.1$ for $I/I_c < 0.5$. For our lithographed traces ($w = 2$ μm, $B_a = 1$ mT, $f = 100$ kHz, $I/I_c = 0.05$):

$$P_\text{AC}/\ell \sim \frac{10^5 \cdot (10^{-3})^2 \cdot 2\times 10^{-6}}{4\pi \times 10^{-7}} \cdot 0.01 \approx 1.6 \times 10^{-3} \text{ W/m.}$$

Per coil, trace length $\approx 30 \text{ turns} \times 2\pi \cdot 8\,\mu\text{m} \approx 1.5 \times 10^{-3}$ m, so $P_\text{coil} \approx 2.4 \times 10^{-9}$ W = 2.4 nW.

Across $10^6$ coils, with a 20% duty cycle in fast-switching mode (most coils sit at quasi-DC offsets and only the active scan pattern switches at full speed):

$$P_\text{AC,total} \approx 10^6 \cdot 2.4\text{ nW} \cdot 0.2 \approx 0.5 \text{ W.}$$

This is the dominant *electrically generated* heat load and the largest single number in the 77 K budget. Worst-case scaling: at the 5 mT slew-target field cited in v3, $B^2$ scaling pushes this to ~12 W, which would force a second cryocooler or limit the worst-case duty cycle. **Recommendation:** specify the worst-case slew event to ≤1% duty, keeping the time-averaged AC loss below 1 W and the cryocooler sizing intact.

### X.6  Capital cost addition over v3 baseline

| Item | Qty | Unit | Subtotal |
|---|---|---|---|
| Cryomech PT-90 (or Sumitomo equiv) cryocooler, N+1 redundant | 2 | \$30 k | \$60 k |
| He compressor + lines | 2 | \$20 k | \$40 k |
| UHV cryostat with optical bore (Montana Instruments custom, or Janis SHI integrated) | 1 | \$250 k | \$250 k |
| MLI blanketing + thermal straps + 150 K shield fabrication | 1 lot | — | \$60 k |
| YBCO-on-sapphire wafers (1 m² total of patterned 2G film at \$200/cm²) | 1 lot | — | \$2.0 M |
| YBCO Meissner shield deposition (additional 0.5 m² film) | 1 lot | — | \$1.0 M |
| HTS current leads (HTS-Cu hybrid bus, ~10³ at \$300) | 1000 | \$300 | \$300 k |
| Cryo-CMOS DAC ASIC (if any DACs at 77 K — see §X.8) | optional | — | \$0–5 M |
| Cryogenic control electronics (temperature sensors, heaters, controllers) | 1 lot | — | \$150 k |
| Integration / labour / contingency (20%) | — | — | \$0.8 M |
| **Net addition over v3** | | | **≈ \$4.7 M** (excl. cryo-CMOS) |

The v3 baseline was \$25–30 M. The cryo retrofit pushes the tool to **\$30–35 M**, comfortably under the \$40 M envelope. Even with the optional cryo-CMOS DAC path (§X.8), total stays ≤\$40 M.

### X.7  Supply-chain check

Three-or-more vendors per subsystem:

| Subsystem | Vendors |
|---|---|
| YBCO 2G tape / films | SuperPower (US), AMSC (US), SuperOx (EU/RU), Faraday Factory (JP), Fujikura (JP), THEVA (DE), Shanghai SC (CN) |
| Cryocoolers (PT @ 77 K) | Cryomech (US), Sumitomo SHI (JP), Edwards (UK, Sumitomo OEM), Brooks/CTI (US), Leybold/Atlas Copco (DE) |
| UHV cryostats | Montana Instruments (US), Janis (US, now Lake Shore), Oxford Instruments (UK), CryoVac (DE), Advanced Research Systems (US) |
| MLI / thermal blanketing | Ruag (CH), Aerospace Fabrication & Materials (US), Sheldahl/Multek (US), Beyond Gravity (CH) |
| HTS deposition service (if not bought as wafer) | THEVA, Ceraco (DE), iBeam Materials (US), Theva spin-outs |
| Cryogenic temperature sensors / controllers | Lake Shore (US), CryoCon (US), Scientific Instruments (US), Stanford Research (US) |

Every subsystem has ≥3 independent suppliers across ≥2 jurisdictions. The cryogenic retrofit does **not** introduce a new chokepoint. (Contrast: EUV pellicle suppliers — single vendor.)

### X.8  Open engineering questions

The following items are not blockers for the spec but require prototype-stage validation before tape-out of the production tool:

1. **DAC placement: warm or cold?** Running $10^6$ DAC channels at 295 K and bringing current pairs through the cryostat wall requires $\sim 2 \times 10^6$ low-thermal-conductivity current leads — large but tractable with HTS-stabilised leads. The alternative is cryo-CMOS DACs at 77 K (cf. Intel Horse Ridge for qubit control). Cryo-CMOS removes the lead-count problem but adds ~5–10 W of dissipation at 77 K, which doubles the cryocooler count. Trade study required in Phase 2.

2. **AC loss measurement at lithographed coil geometry.** Published AC-loss data is for commercial tape widths (4 mm), not 2-μm lithographed traces. Filamentary geometry typically reduces hysteretic loss but may increase coupling loss between adjacent traces. Direct measurement on a $10^2$-coil prototype is essential before locking in the worst-case slew duty.

3. **Quench protection at $10^6$ coils.** A single coil going normal dissipates trivial energy ($\frac{1}{2}LI^2 \sim 100$ pJ), but a propagating normal zone across many coils could drive local hotspots. Need per-coil voltage-tap monitoring or distributed quench-detection — but at $10^6$ channels, the monitoring electronics need their own architecture pass.

4. **Thermal-cycle fatigue of patterned YBCO-on-sapphire over $\sim 10^4$ thermal cycles.** Production tools cycle for maintenance. Existing HTS-filter literature covers ~$10^3$ cycles; $10^4$ cycles at the lithographed-coil geometry is unmeasured.

5. **Cold-stage vibration coupling to the column.** PT coolers nominally produce <100 nm displacement at the cold head, but coupling through the cold-mass structure to the 5 mm beam-passage region must be measured. Provisional plan: passive eddy-current damper + flexible thermal links between cooler and column.

6. **Vacuum compatibility of HTS coatings.** YBCO outgassing at $10^{-7}$ Pa is dominated by absorbed water; a 150 °C bake-out is incompatible with full YBCO patterning. Need to validate that low-temperature bakeout (≤80 °C) reaches the required base pressure.

7. **5 mT vs 1 mT operating field.** v3 Table 1 cites 0.1–1 mT typical with 5 mT as a slew-target envelope. The AC-loss budget is comfortable at 1 mT and tight at 5 mT. v4 should resolve whether the 5 mT envelope is actually needed or is v3 conservatism — if 1 mT bounds the worst-case, the cryocooler count drops from 2 to 1.

### X.9  Summary

Going cryogenic at 77 K resolves the two principal v3 column-level objections at a capital-cost addition of ~\$5 M (≤20% of the v3 baseline) and zero new supply-chain chokepoints. The dominant heat load is AC switching loss in the YBCO coils themselves; everything else (radiation, conduction, wafer-bore load) is sub-watt and routine for a single off-the-shelf pulse-tube cryocooler. The Meissner-screen approach to inter-coil crosstalk reduces the budget item from "hard" to "below LSB." Six open questions remain for the Phase 2 prototype stage; none of them are show-stoppers at the spec level.
