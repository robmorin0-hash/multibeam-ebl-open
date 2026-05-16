"""
Phase 1 — analytical line-charge model for multi-beam EBL space-charge.

Tests the principal physics claim in Morin (2026) v2: that an N×N parallel
electron-beam array at ~5 μm pitch can write semiconductor wafers without
unacceptable cross-beam Coulomb perturbation.

Model
-----
Each beam carries linear charge density λ = I_b / v (line-charge approximation;
column aspect ratio D/P ~ 2e4 makes end-effect corrections O(1e-5)).

Field at a target beam from one neighbor at distance r:
    E = λ / (2πε₀ r)

For co-moving parallel electron beams, the lab-frame transverse force is
suppressed by the magnetic self-pinch:
    F_net = q E (1 - β²) = q E / γ²

Trajectory under constant transverse force over drift D (valid for small
deflections, which is the regime we're in):
    Δr = ½ a t²,   a = F/m,   t = D/v

Sweep (MVP per engineering review)
----------------------------------
P (pitch) × N (beams per side) × I_b (per-beam current) × f (fill fraction).
Fixed: V₀ = 50 kV, D = 100 mm.
"""

import csv
import time
from dataclasses import dataclass
from itertools import product

import numpy as np

# SI constants
e_C    = 1.602176634e-19
m_e_kg = 9.1093837015e-31
eps0   = 8.8541878128e-12
c_ms   = 2.99792458e8


def kinematics(V0):
    """Electron (v, gamma, beta) after acceleration through V0 volts (relativistic)."""
    gamma = 1.0 + e_C * V0 / (m_e_kg * c_ms ** 2)
    beta  = np.sqrt(1.0 - 1.0 / gamma ** 2)
    return beta * c_ms, gamma, beta


def perturbation(positions, currents, targets, V0, D):
    """
    Lateral perturbation (Δx, Δy) at z = D for each target beam, line-charge model.

    Parameters
    ----------
    positions : (M, 2) float array  -- beam x,y in meters
    currents  : (M,)   float array  -- beam current in amps (0 = blanked)
    targets   : (T,)   int array    -- indices into positions to evaluate
    V0        : float               -- acceleration voltage, volts
    D         : float               -- drift distance, meters

    Returns
    -------
    delta : (T, 2) float array  -- (Δx, Δy) in meters
    """
    v, gamma, beta = kinematics(V0)
    rel_factor = 1.0 - beta ** 2  # = 1/γ², magnetic suppression for co-moving beams
    lambdas = currents / v
    t_flight = D / v

    M = len(positions)
    T = len(targets)
    delta = np.zeros((T, 2))

    for i, k in enumerate(targets):
        dr = positions[k] - positions               # (M, 2), points from source to target
        r2 = np.einsum('ij,ij->i', dr, dr)
        r2[k] = np.inf                              # exclude self
        r = np.sqrt(r2)
        # E vector at target from each source: magnitude λ/(2πε₀r), direction r̂
        E_mag = lambdas / (2.0 * np.pi * eps0 * r)
        E_vec = E_mag[:, None] * (dr / r[:, None])
        E_sum = E_vec.sum(axis=0)
        a = e_C * E_sum * rel_factor / m_e_kg
        delta[i] = 0.5 * a * t_flight ** 2

    return delta


def validate_single_neighbor(V0=50e3, P=5e-6, I_b=5e-9, D=0.1):
    """One source beam at distance P, target at origin; both at current I_b."""
    pos = np.array([[0.0, 0.0], [P, 0.0]])
    cur = np.array([I_b, I_b])
    d = perturbation(pos, cur, np.array([0]), V0, D)
    return float(np.linalg.norm(d[0]))


@dataclass
class Case:
    P:    float        # pitch (m)
    N:    int          # beams per side
    I_b:  float        # current per unfilled beam (A)
    fill: float = 1.0  # fraction of beams unblanked
    n_real: int = 1    # MC realizations of fill pattern
    sample: int = 400  # target beams evaluated per realization


def run_case(case, V0=50e3, D=0.1, seed=0):
    """Execute one sweep case; return summary stats over all evaluated targets."""
    rng = np.random.default_rng(seed + int(case.P * 1e10) + case.N + int(case.I_b * 1e12))
    M = case.N * case.N
    coords = np.arange(case.N)
    xx, yy = np.meshgrid(coords, coords, indexing='ij')
    pos = np.stack([xx.ravel(), yy.ravel()], axis=1).astype(float) * case.P

    # Stratified targets: center, edge-mid, corner, plus random
    cN = case.N // 2
    stratified = [cN * case.N + cN, 0 * case.N + cN, 0]
    n_rand = max(0, case.sample - len(stratified))
    rand_idx = rng.choice(M, size=min(n_rand, M - len(stratified)), replace=False)
    targets = np.array(list(stratified) + list(rand_idx), dtype=int)

    all_perts = []
    n_real_eff = case.n_real if case.fill < 1.0 else 1
    for _ in range(n_real_eff):
        if case.fill >= 1.0:
            currents = np.full(M, case.I_b)
        else:
            mask = rng.random(M) < case.fill
            currents = np.where(mask, case.I_b, 0.0)
        d = perturbation(pos, currents, targets, V0, D)
        all_perts.append(np.linalg.norm(d, axis=1))

    arr = np.concatenate(all_perts)
    return dict(
        P_um   = case.P * 1e6,
        N      = case.N,
        I_b_nA = case.I_b * 1e9,
        fill   = case.fill,
        rms_nm  = float(np.sqrt(np.mean(arr ** 2)) * 1e9),
        p99_nm  = float(np.quantile(arr, 0.99) * 1e9),
        max_nm  = float(np.max(arr) * 1e9),
        mean_nm = float(np.mean(arr) * 1e9),
        n_eval  = int(len(arr)),
    )


def main():
    # -- Validation gate --------------------------------------------------
    print("=" * 64)
    print(" Phase 1 — multi-beam EBL space-charge, analytical line-charge")
    print("=" * 64)
    v_corrected = validate_single_neighbor()
    print(f"\nSingle-neighbor validation (P=5 μm, I=5 nA, D=100 mm, V0=50 kV):")
    print(f"  Δr (with γ⁻² correction) = {v_corrected * 1e9:.3f} nm")
    print(f"  Expected from hand-calc  ≈ 6.9 nm")
    if abs(v_corrected * 1e9 - 6.9) > 0.5:
        print("  ⚠  Validation off from expected — check arithmetic before trusting sweep")
    else:
        print("  ✓  Validation matches hand-calc")

    # -- MVP sweep --------------------------------------------------------
    pitches_um  = [1, 2, 5, 10, 20, 50, 100]
    Ns          = [32, 100, 316]
    currents_nA = [1, 5, 10]
    fills       = [1.0, 0.7, 0.5]

    cases = [
        Case(P=P * 1e-6, N=N, I_b=I * 1e-9, fill=f, n_real=10, sample=400)
        for P, N, I, f in product(pitches_um, Ns, currents_nA, fills)
    ]
    print(f"\nSweep: {len(cases)} cases  ({len(pitches_um)} pitches × "
          f"{len(Ns)} N × {len(currents_nA)} currents × {len(fills)} fills)")
    print(f"Tolerance budget: 6 nm RMS at 30 nm grid (20% of pitch)\n")

    t0 = time.time()
    rows = []
    for i, c in enumerate(cases, 1):
        r = run_case(c)
        rows.append(r)
        flag = "" if r['rms_nm'] < 6.0 else "  FAIL"
        print(f"[{i:3d}/{len(cases)}] "
              f"P={r['P_um']:5.1f}μm N={r['N']:4d} I={r['I_b_nA']:4.1f}nA "
              f"f={r['fill']:.1f}  RMS={r['rms_nm']:7.2f}nm "
              f"p99={r['p99_nm']:7.2f}nm  max={r['max_nm']:7.2f}nm"
              f"{flag}    [{time.time() - t0:5.1f}s]")

    # -- Output -----------------------------------------------------------
    keys = list(rows[0].keys())
    with open('phase1_table.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\n→ phase1_table.csv ({len(rows)} rows)")

    # -- Architecture-target verdict --------------------------------------
    print("\nArchitecture target rows (P=5 μm, I=5 nA):")
    for r in rows:
        if r['P_um'] == 5 and r['I_b_nA'] == 5:
            verdict = "PASS" if r['rms_nm'] < 6.0 else "FAIL"
            print(f"  N={r['N']:4d}  f={r['fill']:.1f}  "
                  f"RMS={r['rms_nm']:6.2f} nm  max={r['max_nm']:6.2f} nm  "
                  f"[{verdict} at 6 nm tol]")

    # -- P_min extraction -------------------------------------------------
    print("\nMinimum pitch P_min where RMS first falls below 6 nm (I=5 nA, f=0.5):")
    for N in Ns:
        rows_N = [r for r in rows if r['N'] == N and r['I_b_nA'] == 5 and r['fill'] == 0.5]
        rows_N.sort(key=lambda r: r['P_um'])
        p_min = None
        for r in rows_N:
            if r['rms_nm'] < 6.0:
                p_min = r['P_um']
                break
        print(f"  N={N:4d}: "
              + (f"P_min ≈ {p_min:.1f} μm" if p_min else "no pass within sweep range"))

    print(f"\nTotal wall time: {time.time() - t0:.1f}s")


if __name__ == '__main__':
    main()
