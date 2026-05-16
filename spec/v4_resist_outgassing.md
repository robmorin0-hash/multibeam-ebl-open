# v4 — Resist Chemistry & Outgassing Management Subsystem

*Companion engineering specification to Morin (2026) v3, addressing peer-review flag on
chemically-amplified resist (CAR) outgassing under 65 W e-beam deposition. Status:
spec for prototype build; numerical values are first-pass estimates to be validated in
Phase 2 hardware.*

## 1. Resist Family Selection

Three viable families exist for sub-100 nm e-beam patterning. The selection trade is
between **dose sensitivity** (throughput-critical at our 0.26 s aggressive exposure),
**line-edge roughness** (LER, sets the achievable node), and **outgassing rate** (sets
the column-contamination problem we are trying to engineer away).

| Resist family | Typical dose @ 50 keV | LER (3σ) | Outgassing | Resolution demonstrated |
|---|---|---|---|---|
| CAR (TOK, JSR, Sumitomo) | 10–30 μC/cm² (~5–15 mJ/cm²) | 3–5 nm | High: ~10¹⁵ molec/cm² per exposure [Hada 2009, Kozawa 2013] | sub-20 nm production-proven |
| Molecular glass (Inpria org-MGR, academic Calix/Pol) | 50–150 μC/cm² | 2–4 nm | Moderate: ~10¹⁴ molec/cm² | sub-15 nm research-grade |
| HSQ (Dow Corning XR-1541, DisChem-equivalent) | 1000–4000 μC/cm² (~50–200 mJ/cm²) | 1.5–3 nm | Very low: ~10¹²–10¹³ molec/cm² (inorganic, no PAG) | sub-5 nm demonstrated |
| Metal-oxide (Inpria YA-series, Sn-oxo cluster) | 30–80 μC/cm² | 2–3 nm | Low: predominantly H₂O, alcohol | sub-15 nm, EUV-qualified |

**Recommendation.**
- **Phase 2 prototype (16–64 beams, characterisation):** HSQ (XR-1541, 2% in MIBK). The
  inorganic SiO₁.₅-network chemistry produces negligible volatile organic load; the
  slow process is acceptable for a non-production characterisation tool, and the 1.5–3
  nm LER gives clean Loeffler–Jansen blur measurements not confounded by resist noise.
- **Phase 3 pilot (10⁴-beam, throughput-relevant):** Inpria metal-oxide
  (Sn-cluster). Dose 30–80 μC/cm² is throughput-compatible; outgassing is ~50–100×
  lower than CAR; commercial supply chain exists (Applied Materials owns Inpria, broad
  EUV qualification). The metal-oxide platform is the production answer.
- **CAR retained as fallback** only for the unlikely case that Inpria supply becomes
  restricted; the differential-pumping subsystem below is sized for CAR-grade
  outgassing to keep that option open.

## 2. Outgassing Physics

CAR outgassing under 50 keV electron irradiation has been characterised in detail by
Hada, Kozawa, Tagawa and co-workers (J. Photopolym. Sci. Tech., 2008–2013). For a
typical poly(hydroxystyrene)-protected CAR at production dose:

- Volatile yield per absorbed dose: **G(outgas) ≈ 0.5–1.5 molecules / 100 eV** absorbed.
- Dominant species: isobutylene (t-butyl scission, m/z 56), CO₂, CO, water, acetone,
  and PAG-derived sulfonate fragments (m/z 64–150).
- Surface yield at 30 mJ/cm² and 50 keV: **~1×10¹⁵ molecules/cm²** integrated through
  the resist (Kozawa 2013, table 2).

**Wafer-integrated load (v3 aggressive case, 0.26 s exposure of 300 mm wafer).**

- Wafer area: π·(15)² = 707 cm².
- Total molecules released per wafer: 707 × 10¹⁵ = **7.1×10¹⁷ molecules**.
- Released in 0.26 s → instantaneous source rate **2.7×10¹⁸ molecules/s**.
- In SI throughput units: 2.7×10¹⁸ / N_A = 4.5×10⁻⁶ mol/s ≈ **0.1 mg/s** of mixed
  organic (average MW ~60).

**Partial-pressure rise into the bare chamber** (volume ~0.5 m³, no pumping, ideal gas
at 295 K) over the 0.26 s pulse:
ΔP = NkT/V = 7.1×10¹⁷ × 1.38×10⁻²³ × 295 / 0.5 = **5.8×10⁻³ Pa**, i.e. **~6×10⁴×
above the 10⁻⁷ Pa UHV baseline**. This is the burst the pumping system must absorb
before the next wafer arrives.

Switching to Inpria metal-oxide cuts the source rate by ~50–100×, to **~3×10¹⁶
molec/s** and a burst ΔP ≈ 6×10⁻⁵ Pa. HSQ cuts it by another order.

## 3. Cryosorption from the Cold Column

The 77 K electron-optics column above the wafer is, fortuitously, a very effective
cryopump for the species of concern. Vapor pressures at 77 K:

| Species | P_vap @ 77 K (Pa) | Notes |
|---|---|---|
| H₂O | <10⁻²⁰ | freezes immediately |
| Acetone | <10⁻¹⁵ | freezes |
| Isobutylene (t-Bu) | ~10⁻¹⁰ | freezes (Tm = 132 K, far above 77 K) |
| CO₂ | ~10⁻⁷ | borderline; sticks but desorbs slowly |
| CO | ~50 (not pumped) | does not stick at 77 K |
| N₂ | ~10⁵ (not pumped) | does not stick at 77 K |
| H₂ | not pumped | requires <20 K |

Sticking probabilities on contaminated technical surfaces (steel, YBCO-coated) at 77 K
are in the literature range **0.3–0.9** for the condensable organics (Sedgley 1987;
Day 2006 for ITER cryopanels). Take **s = 0.5** as a conservative working value.

**Effective pumping speed of the cold column entrance** (annular area facing wafer,
ID ≈ 30 cm, OD ≈ 40 cm → A_cold ≈ 550 cm² = 0.055 m²):

S_cryo = (1/4) · v̄ · A · s, with v̄ = √(8kT/πm) for MW 60 at 295 K = 290 m/s.

S_cryo = 0.25 × 290 × 0.055 × 0.5 = **2.0 m³/s = 2000 L/s** for the condensable
fraction. This handles the 2.7×10¹⁸ molec/s burst with margin: the cold column alone
pumps ~80–90% of the load on first surface impact.

The non-condensable fraction (CO, H₂, N₂ baseline) — perhaps 10–20% of the total —
passes through and must be handled by the turbo subsystem.

## 4. Differential-Pumping Geometry

The geometry separates the wafer chamber (where outgassing originates) from the column
volume (where contamination matters) with a conductance-limiting aperture:

```
    [77 K column / electron optics]      <- cryosorption sink, ~2000 L/s condensable
    ===========|=====================
                |  conductance shield (small aperture, ~5 cm dia.)
    -----------|----------               <- pump port: 2× turbo, 2× ion pump
    [wafer at 295 K, resist exposure]    <- gas source, 2.7×10¹⁸ molec/s burst
```

**Aperture conductance.** A 5 cm dia. × 5 cm long tube has C ≈ 200 L/s for MW 60 at
295 K (molecular flow, Knudsen). Most outgassed molecules see the pump port before
they see the column.

**Turbo selection.** The pump port wants ≥1000 L/s nominal for N₂-equivalent to absorb
the non-condensable fraction and to keep base pressure during idle:

| Vendor | Model | Pumping speed (N₂) | Inlet | Price (est.) |
|---|---|---|---|---|
| Pfeiffer | HiPace 2300 | 1900 L/s | DN 250 ISO-K | ~\$25 k |
| Edwards | STP-iXR1606 | 1600 L/s | ISO-200 | ~\$22 k |
| Leybold | TurboVac MAG W 2200 iP | 2050 L/s | DN 250 | ~\$28 k |
| Agilent | TwisTorr 2200 | 1900 L/s | CFF-250 | ~\$24 k |

Spec one **Pfeiffer HiPace 2300** per chamber (DN 250 ISO-K, magnetically levitated,
oil-free — required for UHV near a superconducting column). Back with a Pfeiffer HiCube
80 ECO dry roughing pump (~\$12 k).

Add **two Gamma Vacuum 500 L/s ion pumps** (~\$18 k each, \$36 k total) for steady-state
base pressure and for the post-burst recovery between wafers.

**Net pressure at column entry.** Cryosorbed condensables don't reach the column. The
residual N₂/CO load at the column entry, with 1900 L/s turbo + cold-column pumping in
series, and a steady-state source of ~5×10¹⁷ molec/s of non-condensables at 100%
throughput:

P_col = Q / S_eff = (5×10¹⁷ × kT) / (1900 L/s × 10⁻³ m³/L)
     = (5×10¹⁷ × 4.07×10⁻²¹) / 1.9
     = **1.1×10⁻³ Pa during exposure, decaying to ~10⁻⁷ Pa within ~0.5 s**

The transient excursion to 10⁻³ Pa for ~0.3 s is acceptable: electron-beam mean free
path at 50 keV is still kilometers; what matters is the time-integrated condensable
flux on the cold surfaces, which is bounded by section 5 below.

## 5. Contamination Buildup & Regeneration

The cold surface accumulates condensables. Mass balance at production throughput
(80 wafers/hour ≈ 700 k wafers/year):

- Per wafer: 7×10¹⁷ × 0.5 (sticking) × 0.8 (condensable fraction) ≈ 3×10¹⁷ molec
  retained on cold surface.
- Per year: 700 k × 3×10¹⁷ = 2×10²³ molec/year ≈ **0.3 mol = ~18 g organic ice/year**.
- Over the 0.055 m² cold annulus, this is ~330 g/m²·year, or ~3 mm of solid-organic
  film at unit density — clearly unacceptable without regeneration.

**Regeneration target: monthly.** Heat the cold annulus to 300 K, pump the released
condensables out through the turbo (which will see a ~10⁻³ Pa burst for ~30 min),
re-cool to 77 K. Total cycle:

| Step | Time |
|---|---|
| Warm 77 → 300 K (resistive heaters on cold mass) | 30 min |
| Hold + pump released gas (turbo + ion combination) | 30 min |
| Cool 300 → 77 K | 60 min |
| Wafer-system pump-down recheck | 15 min |
| **Total downtime/month** | **~2.25 h** |

At one cycle per month, **downtime = 2.25 / (30 × 24) = 0.3%**, well under the 1%
budget. Quarterly schedule (every ~700 h of beam-on) is the engineering default;
monthly is the conservative pre-production setting.

Add a **QMS (RGA) head** (SRS RGA200, ~\$18 k) on the chamber to monitor the m/z 56,
44, 64–150 fragments in real time so regeneration is data-triggered, not calendar-triggered.

## 6. Bake-out & Chamber Pre-treatment

Standard UHV practice is a **120–180 °C bake** for 24–48 h after any chamber opening
to drive out water from the steel walls. The constraint here is the cryocooler and
superconducting column:

- **Cryocooler** (Sumitomo RDK-415D 2-stage GM, or Cryomech AL325) must be isolated
  during bake. Either (a) physically remove the cold head, or (b) install a
  bake-through with a gate valve so the column volume is baked separately from the
  cryostat. Standard solution is (b): the column is built as a removable cold module
  with a CF-150 gate valve.
- **Superconducting magnets / YBCO coils** in the column are normally only present in
  the cold-bore region and never see > 100 K. Bake the warm chamber walls; leave the
  cold module pumped but unbaked. This is the standard MRI/NMR practice and
  is well-established hardware.
- Bake the wafer chamber and pump port at **150 °C, 48 h** before first pump-down.
  Subsequent bakes only after chamber-opening events (resist load/unload is via a
  load-lock that does not break main-chamber vacuum).

## 7. Resist Vendor List

| Family | Product | Vendor | Country | Notes |
|---|---|---|---|---|
| HSQ | XR-1541-002 (2% in MIBK) | DuPont / Dow Electronic Materials | US | The reference HSQ; broad academic use |
| HSQ | FOx-12, FOx-15 | DuPont | US | Higher-solids variants |
| HSQ-equivalent | medusa-HSQ | Allresist (AR-N 4000) | Germany | Second source |
| CAR | TDUR-P3000 series | Tokyo Ohka Kogyo (TOK) | Japan | Production-grade KrF/EB CAR |
| CAR | EBR-9, ZEP-520A | Zeon Chemicals | Japan | ZEP is a non-CAR positive, low outgas vs CAR |
| CAR | NEB-22 | Sumitomo Chemical | Japan | Negative CAR |
| CAR | JSR-CAR series | JSR Corporation | Japan | EUV-qualified families |
| Molecular glass | Calixarene-based MG | Academic (Yang, Ober groups) | US | Research-only currently |
| Metal-oxide | YA-series (Sn-oxo cluster) | Inpria (now Applied Materials) | US | EUV production grade |
| Metal-oxide | OrganoTin MG (research) | Multiple academic | global | Open-IP routes published |

A genuine multi-vendor supply chain exists for both ends of the trade space (HSQ
prototyping, metal-oxide production). CAR retains 3+ Japanese suppliers if needed.

## 8. Cost Addition — Pumping & Cryosorption Subsystem

| Item | Cost (USD) |
|---|---|
| 1× Pfeiffer HiPace 2300 turbo + controller | 25 k |
| 1× Pfeiffer HiCube 80 ECO backing pump | 12 k |
| 2× Gamma Vacuum 500 L/s ion pumps | 36 k |
| 1× SRS RGA200 mass spectrometer | 18 k |
| Cold-mass resistive heaters + regeneration controller | 8 k |
| CF-150 gate valve (column isolation, bake-out) | 6 k |
| Conductance shield + aperture machining | 4 k |
| Chamber bake-out jackets (150 °C, 48 h capable) | 12 k |
| Installation, plumbing, electrical | 15 k |
| **Subtotal per chamber** | **~136 k** |

For the v3 pilot tool (16–64 beam, single chamber), add ~\$140 k to BOM. For a
production 10⁶-beam multi-chamber tool, scale linearly with chamber count
(estimate 8–16 chambers → \$1.1–2.2 M). This is <1% of the total tool cost and
well within the v3 cost-budget envelope.

## 9. Open Questions

1. **Resist-specific outgassing characterisation.** Literature numbers are for
   archetypal CAR formulations. Inpria metal-oxide outgassing under 50 keV (vs the
   well-characterised EUV case at 92 eV) needs measurement; the secondary-electron
   cascade differs and the dominant volatile species may shift. Phase 2 should run
   QMS during single-beam exposures of each candidate resist.
2. **Cold-surface sticking probability for PAG-sulfonate fragments.** Sulfonic-acid
   fragments are heavier and stickier than the canonical small-molecule list;
   sticking on YBCO at 77 K may be near 1.0 but data is sparse. Worth a dedicated
   measurement on a witness coupon.
3. **Cryosorbed-film electrical behaviour.** A growing organic film on a
   superconducting electrode could perturb the local steering field. Estimate:
   1 nm of organic = ~3×10⁻⁴ pF/cm² capacitance perturbation, probably negligible at
   our drive impedance, but a transient-response measurement during the regeneration
   warm-up should confirm.
4. **Regeneration cadence under real production load.** The 0.3%-downtime number
   assumes monthly. RGA-triggered adaptive scheduling could push toward
   quarterly; needs a fielded data set.
5. **Bake compatibility of full column assembly.** The CF-150 gate-valve isolation
   strategy is standard but unverified for the specific (open-IP) column geometry
   proposed in v3. Mechanical layout should be reviewed before Phase 2 build.
6. **Resist-to-wafer-chuck thermal load.** 65 W into a 300 mm wafer with limited
   thermal contact may raise wafer temperature 5–15 K during the burst, which
   itself accelerates outgassing. Coupled thermal-vacuum simulation needed; this
   is the closest-coupled open question to §2.
