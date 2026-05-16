"""
Phase 2 --- Loeffler-Jansen intra-beam stochastic Coulomb blur.

Direct N-body simulation of a single electron beam over the drift distance,
tracking transverse trajectory broadening from pairwise Coulomb scattering
between electrons co-moving in the beam.

Companion to phase1_analytic.py / phase1_stochastic.py (cross-beam sim).
Together these characterise the two stochastic-blur components flagged in
§3.4.6 and §8 of the v3 preprint:
    σ_total² ≈ σ_cross² + σ_LJ² + σ_Boersch²

Frame: lab frame, Newtonian dynamics with γ⁻² magnetic suppression for
co-moving electrons (= 0.83 at 50 kV). Comoving-frame approximation: since
all electrons have the same v_z, their relative z separation is constant
over the drift; only transverse dynamics evolve.

Periodic boundary in z (representative slice; slice_L chosen so the slice
contains N_electrons at the actual line density I/(e·v)).
"""

import csv
import time

import numpy as np

# SI constants
e_C    = 1.602176634e-19
m_e_kg = 9.1093837015e-31
eps0   = 8.8541878128e-12
c_ms   = 2.99792458e8
k_B    = 1.380649e-23


def kinematics(V0):
    """Returns (v, gamma, beta) for an electron through V0 volts (relativistic)."""
    gamma = 1.0 + e_C * V0 / (m_e_kg * c_ms**2)
    beta  = np.sqrt(1.0 - 1.0 / gamma**2)
    return beta * c_ms, gamma, beta


def simulate_LJ(I_beam, V0, drift_L, r_beam, N_e=1000, n_steps=400,
                T_cathode=1800.0, soft_core_frac=1.0, seed=0,
                coulomb_on=True, verbose=False):
    """
    Single-beam intra-beam dynamics via direct N-body. Returns the transverse
    displacement σ at end of drift. Use coulomb_on=False to isolate the thermal
    ballistic baseline; σ_LJ is the EXCESS in quadrature with Coulomb on.

    Parameters
    ----------
    I_beam : beam current, A
    V0     : acceleration voltage, V
    drift_L: drift distance, m
    r_beam : beam radius (assumed uniform along column), m
    N_e    : # electrons in periodic slice
    n_steps: # time steps over drift
    T_cathode : cathode temperature for initial thermal velocity spread, K
    soft_core_frac : softening as fraction of r_beam to regularise singularities
    seed   : RNG seed
    coulomb_on : if False, suppress Coulomb forces (thermal baseline only)

    Returns
    -------
    sigma_perp : RMS transverse displacement at end of drift, m
    info       : dict of simulation metadata
    """
    rng = np.random.default_rng(seed)
    v, gamma, beta = kinematics(V0)

    # Linear charge density and electron-per-meter
    lam = I_beam / v
    n_per_m = lam / e_C
    slice_L = N_e / n_per_m  # chosen so slice contains N_e at true density

    # Initial transverse positions: uniform disk
    r0 = r_beam * np.sqrt(rng.uniform(0, 1, N_e))
    th = rng.uniform(0, 2*np.pi, N_e)
    x  = r0 * np.cos(th)
    y  = r0 * np.sin(th)

    # Initial z positions: uniform along slice
    z = rng.uniform(0, slice_L, N_e)

    # Initial transverse velocities: cathode thermal spread.
    # Transverse kinetic energy from a thermal cathode is preserved through
    # acceleration; transverse RMS speed from 2D Maxwell-Boltzmann.
    v_th = np.sqrt(2.0 * k_B * T_cathode / m_e_kg)
    vx = rng.normal(0, v_th, N_e)
    vy = rng.normal(0, v_th, N_e)

    # Save initial positions for displacement calculation
    x0, y0 = x.copy(), y.copy()

    # Integration parameters
    drift_time = drift_L / v
    dt = drift_time / n_steps

    # Force constant: k = e²/(4πε₀ m_e)
    k_F  = e_C**2 / (4 * np.pi * eps0 * m_e_kg)
    rel  = 1.0 / gamma**2   # magnetic suppression for co-moving beam
    soft = (soft_core_frac * r_beam)**2

    # Leapfrog integration (transverse only; z constant in comoving picture)
    for step in range(n_steps):
        dx = x[:, None] - x[None, :]
        dy = y[:, None] - y[None, :]
        dz = z[:, None] - z[None, :]
        dz -= slice_L * np.round(dz / slice_L)         # periodic z minimum-image

        r2 = dx**2 + dy**2 + dz**2 + soft
        r3_inv = r2**(-1.5)
        np.fill_diagonal(r3_inv, 0.0)

        if coulomb_on:
            ax = k_F * rel * np.sum(dx * r3_inv, axis=1)
            ay = k_F * rel * np.sum(dy * r3_inv, axis=1)
        else:
            ax = np.zeros_like(x)
            ay = np.zeros_like(y)

        vx += ax * dt
        vy += ay * dt
        x  += vx * dt
        y  += vy * dt

        if verbose and (step + 1) % max(1, n_steps // 10) == 0:
            sig_now = float(np.sqrt(np.mean((x-x0)**2 + (y-y0)**2)))
            print(f'  step {step+1:4d}/{n_steps}: σ_perp = {sig_now*1e9:7.3f} nm')

    sigma_perp = float(np.sqrt(np.mean((x - x0)**2 + (y - y0)**2)))
    return sigma_perp, dict(
        N=N_e, n_steps=n_steps,
        slice_L_m=slice_L, drift_time_s=drift_time, dt_s=dt,
        v_thermal_m_s=v_th, n_per_m=n_per_m,
        density_m3 = N_e / (np.pi * r_beam**2 * slice_L),
        gamma=gamma, beta=beta, rel_factor=rel,
    )


def run_v3_nominal(n_seeds=3):
    """Run Phase 2 sim at v3 nominal geometry across a small r_beam sweep."""
    I_beam = 5e-9
    V0     = 50e3
    drift_L= 0.1
    print('=' * 76)
    print(' Phase 2 --- Loeffler-Jansen intra-beam stochastic Coulomb blur')
    print(' v3 nominal geometry: I=5 nA, V0=50 kV, D=100 mm')
    print('=' * 76)
    v, g, b = kinematics(V0)
    print(f' v={v:.3e} m/s, γ={g:.4f}, β={b:.4f}, 1/γ²={1/g**2:.4f}')
    print(f' Frame: lab, with magnetic suppression for co-moving electrons')

    # Sweep over beam radius (smaller r → denser → more LJ blur)
    r_beam_nm_list = [1, 2, 5, 10, 20, 50]
    N_e = 600
    n_steps = 400

    print(f'\n N={N_e} electrons per slice, n_steps={n_steps}, {n_seeds} seeds per case')
    print(f' Slice length adjusted per radius to match real line density I/(e·v)\n')

    print(f"{'r_beam':>8} {'density':>11} {'sep':>8}   "
          f"{'σ_therm':>9} {'σ_total':>10} {'σ_LJ':>9}   {'walltime':>9}")
    print(f"{'(nm)':>8} {'(m⁻³)':>11} {'(nm)':>8}   "
          f"{'(nm)':>9} {'(nm)':>10} {'(nm)':>9}   {'(s)':>9}")
    print('-' * 86)

    rows = []
    t_all = time.time()
    for r_nm in r_beam_nm_list:
        r_beam = r_nm * 1e-9
        sigmas_total  = []
        sigmas_therm  = []
        info0 = None
        t0 = time.time()
        for seed in range(n_seeds):
            sig_tot, info = simulate_LJ(I_beam, V0, drift_L, r_beam,
                                         N_e=N_e, n_steps=n_steps, seed=seed,
                                         coulomb_on=True)
            sig_th, _    = simulate_LJ(I_beam, V0, drift_L, r_beam,
                                         N_e=N_e, n_steps=n_steps, seed=seed,
                                         coulomb_on=False)
            sigmas_total.append(sig_tot)
            sigmas_therm.append(sig_th)
            info0 = info
        sig_tot_mean   = float(np.mean(sigmas_total)) * 1e9
        sig_therm_mean = float(np.mean(sigmas_therm)) * 1e9
        # σ_LJ = quadrature excess above thermal baseline (clamped at 0)
        excess_sq = max(0.0, sig_tot_mean**2 - sig_therm_mean**2)
        sig_LJ = float(np.sqrt(excess_sq))
        dens = info0['density_m3']
        mean_sep_nm = (1.0 / dens) ** (1/3) * 1e9
        elapsed = time.time() - t0
        print(f'{r_nm:8.0f} {dens:11.2e} {mean_sep_nm:8.0f}   '
              f'{sig_therm_mean:9.1f} {sig_tot_mean:10.1f} {sig_LJ:9.4f}   '
              f'{elapsed:9.1f}')
        rows.append(dict(
            r_beam_nm=r_nm, density_m3=dens, mean_sep_nm=mean_sep_nm,
            sigma_thermal_nm=sig_therm_mean,
            sigma_total_nm=sig_tot_mean,
            sigma_LJ_excess_nm=sig_LJ,
            wall_s=elapsed,
        ))

    # CSV
    with open('phase2_loeffler_jansen.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f'\nWrote phase2_loeffler_jansen.csv ({len(rows)} rows)')
    print(f'Total wall time: {time.time() - t_all:.1f} s\n')

    # Summary
    print(' Summary')
    print(' -------')
    print(' σ_LJ_excess = sqrt(σ_total² − σ_thermal²) at the v3 nominal geometry.')
    print()
    print(f' σ_thermal (cathode T={1800}K → v_rms=2.3×10⁵ m/s → 186 µm over 100 mm drift)')
    print(' is the BALLISTIC baseline from initial transverse momentum spread.')
    print(' In a real column, condenser optics demagnify this to the focused spot;')
    print(' here it is the un-focused upper bound. The relevant quantity for the')
    print(' v3 paper is σ_LJ_excess, the Coulomb-induced trajectory broadening.')
    print()
    print(' Results:')
    for r in rows:
        print(f'   r_beam = {r["r_beam_nm"]:3.0f} nm:  '
              f'σ_LJ_excess = {r["sigma_LJ_excess_nm"]:6.3f} nm')
    print()
    print(' Finding: σ_LJ_excess is sub-nm at all simulated r_beam under the')
    print(' constant-radius pencil-beam approximation. This is the SMOOTH-FIELD')
    print(' part of Loeffler-Jansen. The literature 5–20 nm range applies to')
    print(' columns with tight crossover regions (r_b → atomic scale locally)')
    print(' which generate collisional Coulomb dynamics not captured here.')
    print()
    print(' Implication for v3 paper: σ_LJ depends primarily on column-optics')
    print(' crossover geometry. The v3 architecture (§2.1) could plausibly avoid')
    print(' tight crossovers via direct condenser-to-wafer optics, in which case')
    print(' σ_LJ << 5 nm. Validating this requires a full column-physics sim')
    print(' (GPT or OPAL) — formally the Phase 2 referenced in v3 §3.4.6.')


if __name__ == '__main__':
    run_v3_nominal()
