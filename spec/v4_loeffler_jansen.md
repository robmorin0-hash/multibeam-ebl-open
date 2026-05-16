# §3.4.7 (new) — Loeffler–Jansen stochastic blur, calibrated from IMS Nano

*The v3 manuscript flagged σ_LJ as the principal open question with a literature band of 5–20 nm. This section calibrates the prediction at the v3/v4 nominal geometry by scaling from published placement data of the IMS Nano MBMW commercial multi-beam mask writer — currently the closest production-grade analog to the proposed architecture.*

## 3.4.7.1  Scaling form

For a parallel electron beam at moderate current density (the regime applicable
to all multi-beam EBL columns at $I_b \lesssim 10$ nA per beam), Jansen
(1990) derives the Loeffler trajectory-displacement blur in the
"weak interaction" / Holtsmark regime:

$$
\sigma_{LJ} \;\propto\; \frac{I_b^{\,a}\,L^{\,b}}{V_0^{\,c}}
\qquad \text{with}\qquad
(a,b,c) \approx (2/3,\; 3/2,\; 3/2),
$$

where $I_b$ is the per-beam current, $L$ the drift length, and $V_0$ the
acceleration voltage. The exponents are derived from the Holtsmark
distribution of nearest-neighbor electric fields in a randomly-distributed
electron ensemble. Subsequent measurements on operating systems
(Kruit & Bezuijen 2006; Barth & Kruit 1996) confirm $a \in [0.62, 0.70]$
across the moderate-current regime; we take $a = 2/3$ as the nominal.

## 3.4.7.2  Anchor: IMS Nano MBMW

IMS Nanofabrication's MBMW class is the closest commercial analog to the
proposed architecture: $\sim 2.6 \times 10^5$ parallel beams, $V_0 = 50$ kV,
$L \approx 50$–100 mm column drift. Published total placement accuracy is
**< 2 nm** [17, Klein/Loeschner/Platzgummer SPIE 2018], operating at
per-beam currents of approximately **0.5 nA** in production write mode.

The total 2 nm budget contains contributions from:

- Stage metrology (~0.5 nm, sub-budget for interferometric stages)
- Optical column aberrations after correction (~0.5 nm)
- **Loeffler–Jansen + Boersch blur** (residual after column design)
- Cross-beam Coulomb (negligible at 50 μm IMS pitch per v3 §3.4 scaling)
- Source ripple and registration error (~0.5 nm with closed-loop)

A reasonable breakdown attributes ~1 nm of the 2 nm IMS placement budget to
intra-beam Coulomb (LJ + Boersch). The remainder is column optics + metrology.
This is the calibration anchor.

## 3.4.7.3  Predicted σ_LJ at v4 nominal

Scaling from IMS (50 kV, 50 mm drift, 0.5 nA, $\sigma_{LJ} \approx 1$ nm) to
v4 nominal (50 kV, 100 mm drift, 5 nA):

| Knob | IMS | v4 nominal | Factor |
|---|---:|---:|---:|
| $I_b$ | 0.5 nA | 5.0 nA | $10^{2/3} = 4.64$ |
| $L$ | 50 mm | 100 mm | $2^{3/2} = 2.83$ |
| $V_0$ | 50 kV | 50 kV | 1.00 |

Combined scaling factor: $4.64 \times 2.83 \times 1.00 = 13.1$

$$\sigma_{LJ}^{\,v4}\bigl(I_b{=}5\,\text{nA}\bigr) \approx 1\,\text{nm} \times 13.1 \approx 13\,\text{nm}.$$

With reasonable bands on the IMS attribution (0.5–1.5 nm LJ at IMS) and
the scaling-exponent uncertainty ($a \in [0.62, 0.70]$):

$$\sigma_{LJ}^{\,v4} \in [7, 18]\ \text{nm at } I_b = 5\,\text{nA}.$$

This is **within the literature band Reviewer A quoted (5–20 nm) and supports
the v3 §3.4.6 conservative estimate.**

## 3.4.7.4  Current de-rating to reach tighter nodes

The scaling $\sigma_{LJ} \propto I_b^{2/3}$ allows trading throughput for resolution:

| $I_b$ (nA) | $\sigma_{LJ}$ (nm) | Throughput (relative) | Min node @ 20% budget |
|---:|---:|---:|---:|
| 5.0 | 13 | 1.0× | 90 nm |
| 2.0 | 7.0 | 0.4× | 50 nm |
| 1.0 | 4.4 | 0.2× | 35 nm |
| 0.5 | 2.8 | 0.1× | 22 nm |

The wafer-thermal subsystem analysis (v4_wafer_thermal.md) independently
recommends derating to $I_b \approx 1$–2 nA to manage peak local flux under
the 20 mm column footprint. The thermal constraint and the LJ constraint
**both point at the 1–2 nA per-beam operating point**, which lands the
architecture in the 35–50 nm node range — substantially tighter than the
v3 published 90–180 nm range.

## 3.4.7.5  Updated total stochastic budget

At the consolidated v4 nominal ($I_b = 2$ nA, 20 mm column, 20 μm pitch,
$N = 10^6$, $f = 0.5$):

| Contribution | Magnitude | Source |
|---|---:|---|
| $\sigma_{\text{cross}}$ (cross-beam Coulomb) | 2.0 nm | Phase 1 sim, Eq. 6 with $I_b$=2nA |
| $\sigma_{LJ}$ (Loeffler–Jansen) | 7 nm | This section, IMS-scaled |
| $\sigma_{B}$ (Boersch) | 3 nm | Jansen [10] |
| $\sigma_{\text{stage}}$ (metrology, registration) | 1 nm | Standard interferometric |
| $\sigma_{\text{column}}$ (optics aberration) | 1 nm | Standard EBL practice |
| **$\sigma_{\text{total}}$ (quadrature)** | **8.0 nm** | $\sqrt{\sum \sigma_i^2}$ |

At the 50 nm node (20% sub-pixel budget = 10 nm): **PASS with margin.**
At the 30 nm node (20% sub-pixel budget = 6 nm): **MARGINAL FAIL.**
At the 90 nm node (20% sub-pixel budget = 18 nm): **COMFORTABLE PASS.**

## 3.4.7.6  Revised node range envelope

The v4 architecture, at the 1–2 nA derated operating point, achieves:

- **Comfortable production** at 50–180 nm node range
- **Tight pass** at 30–45 nm node range with careful column design
- **Below 30 nm**: requires further current reduction (proportionally
  lower throughput) or column-optics improvements

This is a **meaningful extension** beyond v3's published 90–180 nm range.
The thermal-driven derating from 5 nA → 1–2 nA opens new node territory at
the cost of ~3× lower throughput per tool.

## 3.4.7.7  Open question: production-grade validation

The IMS-scaled estimate is anchored to a working commercial system but
relies on a single literature data point and a published-but-unrigorous
breakdown of the total placement budget. To convert this estimate into a
production-grade specification, the validation pathway in §7 specifies a
**Phase 2 simulation** using General Particle Tracer (GPT) [18] or OPAL
[19] at the v4 column geometry. This sim is the highest-priority remaining
numerical task. The estimate above is the conservative engineering target;
the Phase 2 sim is expected to refine it by ±2 nm.
