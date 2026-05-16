"""
Generates §3.4 figure for the v3 preprint:
  Panel (a) — σ_cross (cross-beam Coulomb only) vs P at architecture target,
              showing measured points across three exploration grids, the 1/P
              fit, the 6 nm threshold, and the three candidate v3 pitches.
  Panel (b) — total stochastic budget (σ_cross + σ_LJ band + σ_B) vs P at v3
              nominal, with placement-tolerance bands for 30 nm / 90 nm /
              180 nm nodes.
"""

import csv
import math

import matplotlib.pyplot as plt
import numpy as np

phi = (1 + math.sqrt(5)) / 2

# ---- load sim data: CSVs --------------------------------------------------
rows = []
for fname in ('phase1_stochastic.csv', 'phase1_369.csv'):
    with open(fname) as fh:
        for r in csv.DictReader(fh):
            rows.append({k: float(v) if k != 'N' else int(v) for k, v in r.items()})

# Probe-run data (boundary + golden + 369), captured from run logs
extra = [
    # (P_um, N, I_nA, f, sigma_rms, sigma_p99, sigma_max)
    # boundary probe (boundary 12-24 μm)
    (12,    316, 5, 0.5, 7.909,  9.581,  9.904),
    (15,    316, 5, 0.5, 6.320,  7.836,  8.064),
    (18,    316, 5, 0.5, 5.247,  6.419,  6.559),
    (21,    316, 5, 0.5, 4.603,  5.918,  6.102),
    (24,    316, 5, 0.5, 3.930,  4.780,  5.170),
    # golden-spaced probe
    (3.090, 316, 5, 0.5, 31.418, 39.732, 41.285),
    (4.854, 316, 5, 0.5, 19.734, 24.190, 24.867),
    (8.090, 316, 5, 0.5, 11.756, 14.028, 15.202),
    (13.090,316, 5, 0.5, 7.382,  8.712,  9.356),
    (15.708,316, 5, 0.5, 6.007,  7.366,  8.026),
    (21.180,316, 5, 0.5, 4.496,  5.733,  6.103),
    (34.271,316, 5, 0.5, 2.788,  3.492,  3.640),
    # 369 μm probe
    (369,   316, 5, 0.5, 0.2508, 0.3096, 0.3193),
]

# Filter CSV rows to architecture target
target = [r for r in rows if r['N'] == 316 and r['I_b_nA'] == 5 and r['fill'] == 0.5]

P_csv     = np.array([r['P_um']        for r in target])
sigma_csv = np.array([r['stoch_rms_nm'] for r in target])
p99_csv   = np.array([r['stoch_p99_nm'] for r in target])

P_probe   = np.array([row[0] for row in extra])
sig_probe = np.array([row[4] for row in extra])
p99_probe = np.array([row[5] for row in extra])

P_all   = np.concatenate([P_csv, P_probe])
sig_all = np.concatenate([sigma_csv, sig_probe])
p99_all = np.concatenate([p99_csv,   p99_probe])

# Sort by pitch
order = np.argsort(P_all)
P_all, sig_all, p99_all = P_all[order], sig_all[order], p99_all[order]

# ---- 1/P fit -------------------------------------------------------------
def sigma_model(P_um, I_nA=5, N=316, f=0.5):
    """Eq. 6: σ_cross ≈ 19 nm · (I/5) · (5/P) · √(ln N / ln 316) · √(f(1-f)/0.25)"""
    return 19.0 * (I_nA / 5.0) * (5.0 / P_um) * \
           math.sqrt(math.log(N) / math.log(316)) * \
           math.sqrt(f * (1 - f) / 0.25)

P_fit = np.logspace(0, 3, 200)
sig_fit = np.array([sigma_model(P) for P in P_fit])

# ---- placement-tolerance lines -------------------------------------------
# 20% of pitch (sub-pixel budget) at given node sizes (nm)
def tol_20pct(node_nm): return 0.20 * node_nm

# ---- figure ---------------------------------------------------------------
fig, (axA, axB) = plt.subplots(1, 2, figsize=(11, 4.6))

# === Panel A — σ_cross vs P ============================================
axA.loglog(P_fit, sig_fit, '-', color='steelblue', lw=1.6, label=r'Eq. 6  ($1/P$ fit, $N{=}316$)', zorder=2)
axA.loglog(P_all, sig_all, 'o', color='black', ms=4.5, label=r'simulation, $\sigma_{\rm rms}$',  zorder=3)
axA.loglog(P_all, p99_all, '^', color='gray',  ms=3.5, label=r'simulation, $\sigma_{p99}$', zorder=3, alpha=0.7)

# 6 nm threshold
axA.axhline(6, color='crimson', linestyle='--', lw=1, alpha=0.8, zorder=1)
axA.text(1.2, 6.6, '6 nm RMS budget  (20% of 30 nm grid)',
         color='crimson', fontsize=8.5, va='bottom')

# Candidate pitches
for P_c, label, color in [(18, '18 μm  (Tesla 3·6)',   'darkgreen'),
                          (20, '20 μm  (engineering)', 'navy'),
                          (21.18, '21.2 μm  (5φ³)',   'purple')]:
    axA.axvline(P_c, color=color, linestyle=':', lw=1.1, alpha=0.7)
    axA.text(P_c * 1.03, 0.15, label, color=color, fontsize=8.5, rotation=90, va='bottom')

# v2 nominal annotation
axA.annotate('v2 nominal: P=5 μm\nσ=18.8 nm  (FAIL by 3×)',
             xy=(5, 18.75), xytext=(1.4, 60),
             fontsize=8.5, ha='left',
             arrowprops=dict(arrowstyle='->', color='gray', lw=0.7))

axA.set_xlabel(r'Beam pitch $P$  (μm)')
axA.set_ylabel(r'Cross-beam Coulomb $\sigma_{\rm cross}$  (nm)')
axA.set_title(r'(a)  Cross-beam Coulomb residual vs pitch'
              '\n' r'$I_b = 5$ nA, $N = 316\;(\approx10^5$ beams$)$, $f = 0.5$',
              fontsize=10)
axA.set_xlim(1, 500)
axA.set_ylim(0.1, 100)
axA.grid(which='both', linestyle='-', linewidth=0.3, alpha=0.4)
axA.legend(loc='lower left', fontsize=8.5, framealpha=0.92)

# === Panel B — total budget at v3 nominal ==============================
# Build the Loeffler-Jansen band (assumed 5-20 nm, pitch-independent intra-beam)
P_b = np.logspace(0, 2.7, 200)
sigma_cross_b = np.array([sigma_model(P) for P in P_b])
sigma_B = 5.0
sigma_LJ_lo, sigma_LJ_hi = 5.0, 20.0

# Total stochastic budget (quadrature)
sig_total_lo = np.sqrt(sigma_cross_b**2 + sigma_LJ_lo**2 + sigma_B**2)
sig_total_hi = np.sqrt(sigma_cross_b**2 + sigma_LJ_hi**2 + sigma_B**2)

axB.fill_between(P_b, sig_total_lo, sig_total_hi,
                 color='steelblue', alpha=0.30, label=r'$\sigma_{\rm total}$ band')
axB.plot(P_b, sigma_cross_b, '-', color='steelblue', lw=1.6, label=r'$\sigma_{\rm cross}$  (Eq. 6)')

# horizontal placement-tolerance lines for various nodes
node_lines = [
    (30,  'tab:red',    '30 nm node (20%)'),
    (90,  'darkorange', '90 nm node (20%)'),
    (180, 'darkgreen',  '180 nm node (20%)'),
]
for node_nm, color, label in node_lines:
    tol = tol_20pct(node_nm)
    axB.axhline(tol, color=color, linestyle='--', lw=1, alpha=0.85)
    axB.text(1.05, tol + 0.6, f'{label}: {tol:.0f} nm',
             color=color, fontsize=8.5, va='bottom')

# Mark v3 nominal pitch
axB.axvline(20, color='navy', linestyle=':', lw=1.1, alpha=0.8)
axB.text(20.5, 32, 'v3 nominal\nP=20 μm', color='navy', fontsize=8.5, va='top')

axB.set_xscale('log')
axB.set_xlabel(r'Beam pitch $P$  (μm)')
axB.set_ylabel(r'Total stochastic placement budget  (nm)')
axB.set_title('(b)  Total stochastic budget at v3 nominal\n'
              r'$\sigma_{\rm total}^2 = \sigma_{\rm cross}^2 + \sigma_{\rm LJ}^2 + \sigma_{\rm B}^2$,'
              r'  $\sigma_{\rm LJ}\in[5,20]$ nm (Phase 2 open)',
              fontsize=10)
axB.set_xlim(1, 500)
axB.set_ylim(0, 50)
axB.grid(which='both', linestyle='-', linewidth=0.3, alpha=0.4)
axB.legend(loc='upper right', fontsize=8.5, framealpha=0.92)

plt.suptitle(r'Figure 4.  Phase 1 numerical validation of the cross-beam'
             r' Coulomb perturbation claim (§3.4).',
             y=1.02, fontsize=10.5)
plt.tight_layout()

plt.savefig('figure_phase1.pdf', bbox_inches='tight', dpi=300)
plt.savefig('figure_phase1.png', bbox_inches='tight', dpi=200)
print('→ figure_phase1.pdf, figure_phase1.png')

# Print a sanity summary
print('\nSimulation points plotted in panel (a):')
print(f"  P range: {P_all.min():.2f} – {P_all.max():.1f} μm  ({len(P_all)} points)")
print(f"  σ range: {sig_all.min():.3f} – {sig_all.max():.1f} nm")

print('\nKey thresholds:')
print(f"  6 nm budget: crossing at P_min = 19·5/6 = {19*5/6:.2f} μm")
print(f"  Candidate pitches: 18, 20, 21.2 μm  →  σ_cross = "
      f"{sigma_model(18):.2f}, {sigma_model(20):.2f}, {sigma_model(21.18):.2f} nm")
print(f"  Total budget at v3 nominal (P=20, LJ=15): "
      f"{np.sqrt(sigma_model(20)**2 + 15**2 + 5**2):.1f} nm")
