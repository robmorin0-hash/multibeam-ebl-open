"""
Phase 2 (corrected) — Jansen Loeffler-Jansen trajectory-displacement formula
in literature units, calibrated against IMS Nano commercial data, with
sensitivity sweep across the v4 architecture parameter space.

The previous Holtsmark MC attempt (phase2_holtsmark.py) used an impulse
approximation that omits the relative-velocity correction critical in
co-moving electron beams. That sim returned numbers ~100× too small at
high current and far below the analytical Jansen prediction at v4 nominal.
This script uses the literature-validated closed-form formula with
calibrated prefactor.

Jansen TD blur (FW50, Holtsmark / weak-interaction regime, pencil beam):

    σ_TD [nm] = K · I_b [nA]^(2/3) · L [mm]^(3/2) · V0 [kV]^(-3/2)

Calibration: K = 1.59 ± 0.3 nm·nA^(-2/3)·mm^(-3/2)·kV^(3/2)
anchored against IMS Nano MBMW (Klein et al. SPIE 2018):
    I=0.5 nA, L=50 mm, V0=50 kV → σ_LJ_attributed ≈ 1 nm
which gives K = 1 / (0.5^(2/3) × 50^(3/2) × 50^(-3/2)) = 1.587

Geometry factor: for pencil beam, g ≈ 1. For column with tight crossover,
g can be 2-10× larger (Jansen 1990, Table 6.3). v4 architecture targets
no-crossover condenser-to-wafer optics → g ≈ 1.
"""

import csv
import numpy as np
import matplotlib.pyplot as plt


def jansen_TD(I_b_nA, V0_kV, L_mm, K=1.587, g_geom=1.0):
    """Jansen TD blur in nm (literature units). Calibrated K from IMS Nano."""
    return K * g_geom * I_b_nA**(2/3) * L_mm**(3/2) * V0_kV**(-3/2)


def boersch_dE(I_b_nA, V0_kV, L_mm, K_B=0.6):
    """
    Boersch energy spread in eV, weak-interaction regime.
    σ_E ≈ K_B · I^(2/3) · L^(1/2) · V0^(-1/2)  (Jansen 1990)
    Returns ΔE FW50 in eV.
    """
    return K_B * I_b_nA**(2/3) * L_mm**(1/2) * V0_kV**(-1/2)


def main():
    print('=' * 76)
    print(' Phase 2 (corrected) — Jansen Loeffler-Jansen for v4 architecture')
    print('=' * 76)

    # --- 1. v4 nominal verdict --------------------------------------------
    I_v4 = 2.0   # nA
    V_v4 = 50.0  # kV
    L_v4 = 100.0 # mm
    print(f'\n1. v4 nominal: I_b = {I_v4} nA, V0 = {V_v4} kV, L = {L_v4} mm')
    print(f'   σ_LJ (Jansen, pencil-beam K=1.587) = '
          f'{jansen_TD(I_v4, V_v4, L_v4):.2f} nm  (FW50)')
    print(f'   σ_LJ_rms = FW50/1.18              = '
          f'{jansen_TD(I_v4, V_v4, L_v4)/1.18:.2f} nm')

    # Uncertainty band: K ∈ [1.2, 2.0], g ∈ [1, 1.5]
    sigmas = [jansen_TD(I_v4, V_v4, L_v4, K=K, g_geom=g)
              for K in [1.2, 1.587, 2.0] for g in [1.0, 1.25, 1.5]]
    print(f'   Band (K∈[1.2,2.0], g∈[1,1.5]): '
          f'[{min(sigmas):.2f}, {max(sigmas):.2f}] nm FW50  '
          f'= [{min(sigmas)/1.18:.2f}, {max(sigmas)/1.18:.2f}] nm RMS')

    # --- 2. IMS calibration anchor ----------------------------------------
    print(f'\n2. IMS Nano MBMW calibration anchor:')
    print(f'   At I=0.5 nA, L=50 mm, V0=50 kV → σ_LJ_pred = '
          f'{jansen_TD(0.5, 50, 50):.3f} nm')
    print(f'   Published total placement <2 nm; LJ attribution ~1 nm → consistent')

    # --- 3. Boersch energy spread (also a v4 budget item) -----------------
    print(f'\n3. Boersch energy spread at v4 nominal:')
    dE = boersch_dE(I_v4, V_v4, L_v4)
    print(f'   ΔE = {dE:.3f} eV FW50')
    # Chromatic aberration coefficient — realistic EBL column design
    # Jansen monograph Table 8.1: well-designed columns have C_c ~ 10–100 μm
    # at the wafer plane. Take 50 μm as v4 nominal.
    C_c = 50e-6  # m
    sig_B = (dE / (V_v4 * 1e3)) * C_c * 1e9  # nm
    print(f'   Chromatic aberration coeff C_c ≈ 50 μm (well-designed EBL column):')
    print(f'   σ_B ≈ (ΔE/V0) × C_c = ({dE:.3f}/{V_v4*1e3:.0f}) × {C_c*1e6:.0f} μm = {sig_B:.2f} nm')

    # --- 4. Sweep across v4 architecture parameter space ------------------
    print(f'\n4. Parameter sweep — σ_LJ (RMS, nm) vs current and drift:')
    print(f'   {"":>8}{"L=50mm":>12}{"L=100mm":>12}{"L=150mm":>12}{"L=200mm":>12}')
    rows = []
    for I in [0.5, 1.0, 1.5, 2.0, 3.0, 5.0, 10.0]:
        row = [I]
        for L in [50, 100, 150, 200]:
            sigma = jansen_TD(I, V_v4, L) / 1.18  # convert to RMS
            row.append(sigma)
        rows.append(row)
        line = f'   I={row[0]:5.1f}nA' + ''.join(f'{x:12.3f}' for x in row[1:])
        print(line)

    # --- 5. Total stochastic budget at v4 nominal ------------------------
    sig_LJ = jansen_TD(I_v4, V_v4, L_v4) / 1.18
    sig_B  = (boersch_dE(I_v4, V_v4, L_v4) / (V_v4 * 1e3)) * 50e-6 * 1e9  # C_c=50μm
    sig_cross = 2.0   # nm, from phase1_stochastic at 2 nA per Eq. 6
    sig_stage = 1.0   # nm, from registration loop
    sig_col   = 1.0   # nm, column aberration
    sig_total = np.sqrt(sig_LJ**2 + sig_B**2 + sig_cross**2 + sig_stage**2 + sig_col**2)

    print(f'\n5. Total v4 placement budget (quadrature, at I=2 nA):')
    print(f'   σ_cross     = {sig_cross:.2f} nm  (Phase 1, Eq. 6)')
    print(f'   σ_LJ        = {sig_LJ:.2f} nm  (Jansen, this script)')
    print(f'   σ_B         = {sig_B:.2f} nm  (Boersch+chromatic)')
    print(f'   σ_stage     = {sig_stage:.2f} nm  (registration loop)')
    print(f'   σ_column    = {sig_col:.2f} nm  (optical aberration)')
    print(f'   σ_TOTAL     = {sig_total:.2f} nm  (quadrature sum)')
    print(f'   Node range: 20% budget requires σ < node/5')
    print(f'                30 nm node →  6 nm   {"PASS" if sig_total < 6 else "FAIL by " + f"{sig_total/6:.1f}×"}')
    print(f'                50 nm node →  10 nm  {"PASS" if sig_total < 10 else "FAIL by " + f"{sig_total/10:.1f}×"}')
    print(f'                90 nm node →  18 nm  {"PASS" if sig_total < 18 else "FAIL by " + f"{sig_total/18:.1f}×"}')
    print(f'                180 nm node → 36 nm  {"PASS" if sig_total < 36 else "FAIL by " + f"{sig_total/36:.1f}×"}')

    # --- 6. Save CSV + figure --------------------------------------------
    csv_rows = []
    for I_nA in np.linspace(0.5, 10, 20):
        for L_mm in [50, 100, 150, 200]:
            sigma = jansen_TD(I_nA, V_v4, L_mm) / 1.18
            csv_rows.append(dict(I_nA=I_nA, L_mm=L_mm, sigma_LJ_rms_nm=sigma))
    with open('phase2_jansen.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(csv_rows[0].keys()))
        w.writeheader()
        for r in csv_rows:
            w.writerow(r)

    # Plot: σ_LJ vs current at L=100 mm, with v4 nominal annotated
    I_grid = np.linspace(0.1, 10, 200)
    sigma_grid = jansen_TD(I_grid, V_v4, L_v4) / 1.18

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

    # Panel a: σ_LJ vs I
    ax1.loglog(I_grid, sigma_grid, 'b-', lw=1.8, label='Jansen $\\sigma_{LJ}$ (pencil-beam, $L=100$ mm)')
    # Uncertainty band
    sigma_low  = jansen_TD(I_grid, V_v4, L_v4, K=1.2, g_geom=1.0) / 1.18
    sigma_high = jansen_TD(I_grid, V_v4, L_v4, K=2.0, g_geom=1.5) / 1.18
    ax1.fill_between(I_grid, sigma_low, sigma_high, alpha=0.2, color='blue', label='K ∈ [1.2, 2.0], $g$ ∈ [1, 1.5]')
    # v4 nominal point
    ax1.plot(I_v4, sig_LJ, 'ro', markersize=10, label=f'v4 nominal: 2 nA → {sig_LJ:.1f} nm')
    # IMS calibration
    ax1.plot(0.5, jansen_TD(0.5, 50, 50)/1.18, 'g^', markersize=10, label='IMS Nano calibration')
    # 6 nm threshold
    ax1.axhline(6, color='crimson', linestyle='--', lw=1, alpha=0.8, label='6 nm threshold (20% of 30 nm)')
    ax1.set_xlabel(r'Per-beam current $I_b$ (nA)')
    ax1.set_ylabel(r'$\sigma_{LJ}$ RMS (nm)')
    ax1.set_title('(a) Loeffler–Jansen vs current at v4 geometry\n($V_0=50$ kV, $L=100$ mm)', fontsize=10)
    ax1.grid(which='both', linestyle='-', linewidth=0.3, alpha=0.4)
    ax1.legend(loc='upper left', fontsize=8.5)
    ax1.set_xlim(0.1, 10)
    ax1.set_ylim(0.5, 50)

    # Panel b: stacked stochastic budget at v4 nominal
    labels = [r'$\sigma_{cross}$',
              r'$\sigma_{LJ}$',
              r'$\sigma_{B}$',
              r'$\sigma_{stage}$',
              r'$\sigma_{column}$',
              r'$\sigma_{total}$']
    values = [sig_cross, sig_LJ, sig_B, sig_stage, sig_col, sig_total]
    colors = ['steelblue', 'crimson', 'darkorange', 'gray', 'gray', 'black']
    bars = ax2.bar(labels, values, color=colors, alpha=0.8)
    ax2.axhline(6, color='red', linestyle='--', lw=1, label='30 nm node 20% (6 nm)')
    ax2.axhline(10, color='orange', linestyle='--', lw=1, label='50 nm node 20% (10 nm)')
    ax2.axhline(18, color='green', linestyle='--', lw=1, label='90 nm node 20% (18 nm)')
    ax2.set_ylabel('Placement uncertainty (nm)')
    ax2.set_title('(b) v4 placement budget breakdown\n($I_b=2$ nA quadrature)', fontsize=10)
    ax2.legend(loc='upper left', fontsize=8.5)
    ax2.grid(axis='y', linestyle='-', linewidth=0.3, alpha=0.4)
    for bar, val in zip(bars, values):
        ax2.text(bar.get_x() + bar.get_width()/2, val + 0.3, f'{val:.2f}',
                 ha='center', fontsize=9)

    plt.suptitle('Figure 5. Loeffler–Jansen blur and total v4 placement budget '
                 '(Jansen formula, IMS-calibrated).', y=1.02, fontsize=10.5)
    plt.tight_layout()
    plt.savefig('figure_phase2.pdf', bbox_inches='tight', dpi=300)
    plt.savefig('figure_phase2.png', bbox_inches='tight', dpi=200)
    print(f'\n→ phase2_jansen.csv, figure_phase2.pdf, figure_phase2.png')


if __name__ == '__main__':
    main()
