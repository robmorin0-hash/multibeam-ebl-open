"""
Tesla-pitch sweep: P ∈ {3, 6, 9} μm at the architecture target.
Same stochastic decomposition as phase1_stochastic.py.
"""
import time, csv
from itertools import product
from phase1_analytic import Case
from phase1_stochastic import run_stochastic

pitches_um  = [3, 6, 9]
Ns          = [100, 316]
currents_nA = [1, 5, 10]
fills       = [0.3, 0.5, 0.7]
n_real      = 30

cases = [
    Case(P=P*1e-6, N=N, I_b=I*1e-9, fill=f, sample=300)
    for P, N, I, f in product(pitches_um, Ns, currents_nA, fills)
]
print(f"3-6-9 sweep: {len(cases)} cases, {n_real} realizations each\n")
print(f"{'P':>5} {'N':>4} {'I':>4} {'f':>4}   "
      f"{'det_rms':>9}   {'σ_rms':>8} {'σ_p99':>8} {'σ_max':>8}   verdict")
print(f"{'(μm)':>5} {'':>4} {'(nA)':>4} {'':>4}   "
      f"{'(nm)':>9}   {'(nm)':>8} {'(nm)':>8} {'(nm)':>8}")
print("-" * 88)

t0 = time.time()
rows = []
for c in cases:
    r = run_stochastic(c, n_real=n_real)
    rows.append(r)
    verdict = "PASS" if r['stoch_rms_nm'] < 6.0 else "fail"
    print(f"{r['P_um']:5.1f} {r['N']:4d} {r['I_b_nA']:4.1f} {r['fill']:4.1f}   "
          f"{r['det_rms_nm']:9.1f}   "
          f"{r['stoch_rms_nm']:8.2f} {r['stoch_p99_nm']:8.2f} {r['stoch_max_nm']:8.2f}   "
          f"{verdict}   [{time.time()-t0:5.0f}s]")

keys = list(rows[0].keys())
with open('phase1_369.csv', 'w', newline='') as fh:
    w = csv.DictWriter(fh, fieldnames=keys)
    w.writeheader()
    for r in rows: w.writerow(r)
print(f"\n→ phase1_369.csv  ({len(rows)} rows)")

print("\nArchitecture target (I=5 nA, N=316, f=0.5):")
for r in rows:
    if r['N'] == 316 and r['I_b_nA'] == 5 and r['fill'] == 0.5:
        v = "PASS" if r['stoch_rms_nm'] < 6.0 else "FAIL"
        print(f"  P={r['P_um']:.0f} μm: σ_rms={r['stoch_rms_nm']:5.2f} nm  "
              f"σ_max={r['stoch_max_nm']:5.2f} nm  [{v}]")
