"""
Phase 1.1 — stochastic decomposition of multi-beam space-charge perturbation.

Separates the perturbation at each target beam into:
  - deterministic component: mean over fill-pattern realizations
                             (calibratable by per-beam DAC steady-state offset)
  - stochastic component:    std over fill-pattern realizations
                             (uncorrectable residual; pattern changes faster
                             than deflection loop can track)

Architectural pass criterion: σ_stochastic < 6 nm (20% of 30 nm grid).
"""

import csv
import time
from itertools import product

import numpy as np

from phase1_analytic import perturbation, kinematics, Case  # reuse


def run_stochastic(case, n_real=50, V0=50e3, D=0.1, seed=0):
    """Per-beam stochastic decomposition across n_real fill realizations."""
    rng = np.random.default_rng(seed + int(case.P * 1e10) + case.N + int(case.I_b * 1e12))
    M = case.N * case.N
    coords = np.arange(case.N)
    xx, yy = np.meshgrid(coords, coords, indexing='ij')
    pos = np.stack([xx.ravel(), yy.ravel()], axis=1).astype(float) * case.P

    # Stratified targets: center, edge-mid, corner, plus random interior + edge samples
    cN = case.N // 2
    stratified = [cN * case.N + cN, 0 * case.N + cN, 0]
    n_rand = max(0, case.sample - len(stratified))
    rand_idx = rng.choice(M, size=min(n_rand, M - len(stratified)), replace=False)
    targets = np.array(list(stratified) + list(rand_idx), dtype=int)
    T = len(targets)

    perts = np.zeros((n_real, T, 2))
    for r_i in range(n_real):
        mask = rng.random(M) < case.fill
        currents = np.where(mask, case.I_b, 0.0)
        perts[r_i] = perturbation(pos, currents, targets, V0, D)

    # Decompose per beam
    det = np.mean(perts, axis=0)                  # (T, 2)
    det_mag = np.linalg.norm(det, axis=1)
    stoch_per_axis = np.std(perts, axis=0)        # (T, 2)
    stoch_mag = np.sqrt(np.sum(stoch_per_axis ** 2, axis=1))

    return dict(
        P_um=case.P * 1e6, N=case.N, I_b_nA=case.I_b * 1e9, fill=case.fill, n_real=n_real,
        det_rms_nm   = float(np.sqrt(np.mean(det_mag ** 2)) * 1e9),
        det_max_nm   = float(np.max(det_mag) * 1e9),
        stoch_rms_nm = float(np.sqrt(np.mean(stoch_mag ** 2)) * 1e9),
        stoch_max_nm = float(np.max(stoch_mag) * 1e9),
        stoch_p99_nm = float(np.quantile(stoch_mag, 0.99) * 1e9),
        stoch_mean_nm= float(np.mean(stoch_mag) * 1e9),
    )


def main():
    v, gamma, beta = kinematics(50e3)
    print("=" * 72)
    print(" Phase 1.1 — stochastic decomposition of cross-beam Coulomb perturbation")
    print("=" * 72)
    print(f" v = {v:.3e} m/s, γ = {gamma:.4f}, β = {beta:.4f}, 1/γ² = {1/gamma**2:.4f}")
    print(f" Tolerance budget: 6 nm RMS (20% of 30 nm grid)")
    print(f" Pass = σ_stochastic < 6 nm (deterministic is per-beam calibratable)\n")

    # Architectural sweet spot focused sweep
    pitches_um  = [2, 5, 10, 20]
    Ns          = [100, 316]
    currents_nA = [1, 5, 10]
    fills       = [0.3, 0.5, 0.7]
    n_real      = 30

    cases = [
        Case(P=P * 1e-6, N=N, I_b=I * 1e-9, fill=f, sample=300)
        for P, N, I, f in product(pitches_um, Ns, currents_nA, fills)
    ]
    print(f"Cases: {len(cases)}  ({len(pitches_um)} P × {len(Ns)} N × "
          f"{len(currents_nA)} I × {len(fills)} f),  {n_real} realizations each\n")

    print(f"{'P':>5} {'N':>4} {'I':>4} {'f':>4}   "
          f"{'det_rms':>9} {'det_max':>9}   {'σ_rms':>8} {'σ_p99':>8} {'σ_max':>8}   verdict")
    print(f"{'(μm)':>5} {'':>4} {'(nA)':>4} {'':>4}   "
          f"{'(nm)':>9} {'(nm)':>9}   {'(nm)':>8} {'(nm)':>8} {'(nm)':>8}")
    print("-" * 100)

    t0 = time.time()
    rows = []
    for i, c in enumerate(cases, 1):
        r = run_stochastic(c, n_real=n_real)
        rows.append(r)
        verdict = "PASS" if r['stoch_rms_nm'] < 6.0 else "fail"
        print(f"{r['P_um']:5.1f} {r['N']:4d} {r['I_b_nA']:4.1f} {r['fill']:4.1f}   "
              f"{r['det_rms_nm']:9.1f} {r['det_max_nm']:9.1f}   "
              f"{r['stoch_rms_nm']:8.2f} {r['stoch_p99_nm']:8.2f} {r['stoch_max_nm']:8.2f}   "
              f"{verdict}   [{time.time()-t0:5.0f}s]")

    keys = list(rows[0].keys())
    with open('phase1_stochastic.csv', 'w', newline='') as fh:
        w = csv.DictWriter(fh, fieldnames=keys)
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"\n→ phase1_stochastic.csv ({len(rows)} rows)")

    # Summary: stochastic floor at architecture target
    print("\nStochastic σ at architecture target (I=5 nA, f=0.5):")
    for r in rows:
        if r['I_b_nA'] == 5 and r['fill'] == 0.5:
            v = "PASS" if r['stoch_rms_nm'] < 6.0 else "FAIL"
            print(f"  P={r['P_um']:4.1f}μm  N={r['N']:4d}  "
                  f"σ_rms={r['stoch_rms_nm']:6.2f} nm  σ_max={r['stoch_max_nm']:6.2f} nm  [{v}]")


if __name__ == '__main__':
    main()
