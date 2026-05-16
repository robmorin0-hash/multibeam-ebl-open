"""
Phase 3c — Node-scale accessibility for the v4 architecture.

Plots σ_total vs per-beam current, with the achievable lithographic node
overlaid (20% sub-pixel budget convention). Shows where the v4 architecture
sits in the (current × node × throughput) tradespace.
"""

import numpy as np
import matplotlib.pyplot as plt

# Scaling constants (calibrated from Phase 1 + Phase 2)
SIG_CROSS_PER_NA = 1.0   # nm/nA, linear scaling
SIG_LJ_AT_2NA    = 6.04  # nm at 2 nA per Jansen, scales as I^(2/3)
SIG_B_AT_2NA     = 1.35  # nm at 2 nA per Boersch+chromatic, scales as I^(2/3)
SIG_STAGE        = 1.0   # nm (Zygo ZMI + 3-tier registration)
SIG_COLUMN       = 1.0   # nm (well-designed condenser optics)


def sigma_total(I_b_nA):
    """σ_total at given per-beam current (v4 column geometry, 50 kV, 100 mm)."""
    sig_cross = SIG_CROSS_PER_NA * I_b_nA
    sig_LJ    = SIG_LJ_AT_2NA * (I_b_nA / 2.0)**(2/3)
    sig_B     = SIG_B_AT_2NA  * (I_b_nA / 2.0)**(2/3)
    return np.sqrt(sig_cross**2 + sig_LJ**2 + sig_B**2 + SIG_STAGE**2 + SIG_COLUMN**2)


def min_node_nm(sigma_total_nm):
    """Min node accessible at 20% sub-pixel placement budget."""
    return 5.0 * sigma_total_nm


def throughput_relative(I_b_nA, I_b_v4=2.0):
    """Throughput relative to v4 nominal (linear in current at fixed pixel dose)."""
    return I_b_nA / I_b_v4


def main():
    print('=' * 76)
    print(' Phase 3c — v4 node-scale accessibility')
    print('=' * 76)

    # Sweep
    I_grid = np.logspace(-1.5, 1.5, 100)  # 0.03–30 nA

    sigmas = np.array([sigma_total(I) for I in I_grid])
    nodes = np.array([min_node_nm(s) for s in sigmas])
    throughputs = np.array([throughput_relative(I) for I in I_grid])

    # Floor at I → 0:
    floor = np.sqrt(SIG_STAGE**2 + SIG_COLUMN**2)
    print(f'\nv4 architectural floor (I → 0, optics+stage only):')
    print(f'  σ_total floor = √({SIG_STAGE:.1f}² + {SIG_COLUMN:.1f}²) = {floor:.2f} nm')
    print(f'  Min node accessible:   {5*floor:.1f} nm')
    print(f'  (Below this: resist + spot-size limits dominate, ~3-5 nm)')

    # Operating points
    points = [
        (5.0,  '5 nA (v3 nominal)', 'gray'),
        (2.0,  '2 nA (v4 nominal)', 'red'),
        (1.0,  '1 nA',              'orange'),
        (0.5,  '0.5 nA',            'gold'),
        (0.1,  '0.1 nA',            'green'),
    ]
    print(f'\nOperating points:')
    print(f'  {"I_b":>8} {"σ_total":>10} {"Min node":>10} {"Throughput":>12}')
    print(f'  {"(nA)":>8} {"(nm)":>10} {"(nm)":>10} {"vs v4":>12}')
    for I, label, _ in points:
        s = sigma_total(I)
        n = min_node_nm(s)
        t = throughput_relative(I)
        print(f'  {I:8.2f} {s:10.2f} {n:10.1f} {t:12.2f}×')

    # Figure
    fig, ax = plt.subplots(figsize=(9.5, 5.5))

    # Main curve: σ_total vs I
    ax.loglog(I_grid, sigmas, 'b-', lw=2, label=r'$\sigma_{\rm total}$  (Niki v4 model)')

    # Plot operating points
    for I, label, color in points:
        s = sigma_total(I)
        ax.plot(I, s, 'o', color=color, markersize=10, markeredgecolor='black',
                markeredgewidth=0.5, zorder=5, label=f'{label}: {s:.1f} nm → {min_node_nm(s):.0f} nm node')

    # Node-tolerance reference lines
    for node_nm, color, label in [(180, 'tab:green', '180 nm'),
                                    (90, 'tab:cyan', '90 nm'),
                                    (50, 'tab:purple', '50 nm'),
                                    (30, 'tab:orange', '30 nm'),
                                    (22, 'tab:olive', '22 nm'),
                                    (14, 'tab:red', '14 nm'),
                                    (7, 'darkred', '7 nm (floor)')]:
        budget = 0.2 * node_nm
        ax.axhline(budget, color=color, linestyle='--', linewidth=0.8, alpha=0.7)
        ax.text(28, budget*1.05, f'{label} node (20% = {budget:.1f} nm)',
                color=color, fontsize=8.5, va='bottom', ha='right')

    # Floor line
    ax.axhline(floor, color='black', linestyle=':', lw=1.5,
               label=f'Architectural floor: {floor:.2f} nm')

    ax.set_xlabel(r'Per-beam current $I_b$ (nA)')
    ax.set_ylabel(r'Total stochastic placement budget $\sigma_{\rm total}$ (nm)')
    ax.set_title('v4 architecture — node accessibility vs per-beam current\n'
                 '($V_0 = 50$ kV, $L = 100$ mm, $N = 10^6$, $P = 20$ μm; '
                 'σ floor = stage + column optics only)')
    ax.grid(which='both', linestyle='-', linewidth=0.3, alpha=0.4)
    ax.legend(loc='lower right', fontsize=8.5)
    ax.set_xlim(0.03, 30)
    ax.set_ylim(1, 30)

    # Add secondary y-axis: min accessible node
    ax2 = ax.twinx()
    ax2.set_yscale('log')
    ax2.set_ylim(5 * ax.get_ylim()[0], 5 * ax.get_ylim()[1])
    ax2.set_ylabel('Min accessible node (nm)', color='gray')

    plt.tight_layout()
    plt.savefig('figure_phase3_node_scale.pdf', bbox_inches='tight', dpi=300)
    plt.savefig('figure_phase3_node_scale.png', bbox_inches='tight', dpi=200)
    print(f'\n→ figure_phase3_node_scale.pdf, .png')


if __name__ == '__main__':
    main()
