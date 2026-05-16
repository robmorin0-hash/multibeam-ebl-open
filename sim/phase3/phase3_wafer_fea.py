"""
Phase 3 — 2D axisymmetric finite-volume thermal FEA of v4 wafer chuck.

Verifies the +/-8 mK across-wafer uniformity claim under 65 W steady-state
beam deposition, with and without the 36-zone TEC trim active.

Geometry (axisymmetric, r-z, origin at wafer center top surface, z grows
downward into the stack):

  z = 0                        ---- Wafer top   (Gaussian beam load + 77 K radiation)
  0 < z < t_Si                 Si wafer (k = 150 W/m/K)
  z = t_Si                     ---- Wafer back
  t_Si < z < t_Si + t_He       He gap (modeled as low-k slab of equivalent
                               conductance k_eq = h_He * t_He, so the total
                               resistance across the gap = 1/h_He as expected)
  z = t_Si + t_He              ---- Chuck top
  t_Si+t_He < z < t_stack      AlN chuck (k = 180 W/m/K)
  z = t_stack                  ---- Chuck back: 295 K Dirichlet
                               (Galden microchannel sink + TEC trim BC)

Boundary conditions:
- Top of wafer: Gaussian beam Q(r) = (P/(2 pi s^2)) exp(-r^2/(2 s^2))
  PLUS Stefan-Boltzmann radiation to 77 K cold column (uniform, eps=0.5,
  view factor 0.7) - linearized as h_rad ~= 4 eps F sigma_SB T_w^3
- Bottom of chuck: Dirichlet T = 295 K + TEC_pattern(r)
- Outer cylindrical edge r = R: adiabatic (chuck extends past wafer)
- Axis r = 0: symmetry (no flux)

Two cases:
  A. TEC ON   (delta_TEC ~ 0.1 mK)   -- nominal v4 operating point
  B. TEC OFF  (delta_TEC ~ 30 mK)    -- bare microchannel residual
                                        (the trim layer is the secret sauce)

Solver: direct sparse LU on the finite-volume matrix (3000 unknowns,
trivial for scipy.sparse.linalg.spsolve).
"""

import numpy as np
import scipy.sparse as sp
import scipy.sparse.linalg as spla
import matplotlib.pyplot as plt
import time

# --- Physical constants ----------------------------------------------------

sigma_SB = 5.670374419e-8        # W/(m^2 K^4)

# --- Materials -------------------------------------------------------------

k_Si  = 150.0    # W/m/K
k_AlN = 180.0    # W/m/K
h_He  = 2800.0   # W/m^2/K   He gas film, 5 Torr in 20 um gap (Kennard)
alpha_Si = 2.6e-6   # 1/K   thermal expansion (for placement budget)

# Wafer / chuck geometry
R = 0.150            # m, wafer radius
t_Si  = 775e-6       # m, 775 um Si wafer
t_He  = 20e-6        # m, 20 um He gap
t_AlN = 10e-3        # m, 10 mm AlN chuck body
t_stack = t_Si + t_He + t_AlN

# Beam load
P_beam = 65.0        # W total deposited (steady-state, write-averaged)
sigma_beam = 0.010   # m, Gaussian beam sigma -- matches 20 mm column footprint
                     # (FWHM = 2.355 sigma ~ 23.5 mm)

# Radiative cooling to 77 K cold column above wafer
T_cold_column = 77.0
eps_rad = 0.5
F_rad   = 0.7
T_setpoint = 295.0   # K, wafer target

# TEC residual amplitude
delta_TEC_off = 0.030    # K  -- 30 mK residual from microchannel inlet->outlet
                         # spatial pattern that the TEC is sized to cancel (v4 6.5)
delta_TEC_on  = 0.0001   # K  -- 0.1 mK closed-loop residual after PID trim
                         # (36-zone x 1 mK RTD x 1 Hz loop)


# --- Mesh ------------------------------------------------------------------

N_r = 100
N_z_Si  = 12
N_z_He  = 3
N_z_AlN = 15
N_z = N_z_Si + N_z_He + N_z_AlN     # = 30

r = np.linspace(0, R, N_r)
dr = r[1] - r[0]

# z grid: CELL-CENTERED, with each layer's faces exactly at the layer
# interfaces. Within each layer, nodes are at (i+0.5)*dz from the layer top.
# This guarantees the layer-interface face sits between an in-layer node and
# the next-layer's adjacent node at distance dz_a/2 + dz_b/2, and the
# harmonic-mean conductance recovers the per-layer film resistance correctly.

dz_Si  = t_Si  / N_z_Si
dz_He  = t_He  / N_z_He
dz_AlN = t_AlN / N_z_AlN

z_Si  = 0.0           + (np.arange(N_z_Si)  + 0.5) * dz_Si
z_He  = t_Si          + (np.arange(N_z_He)  + 0.5) * dz_He
z_AlN = t_Si + t_He   + (np.arange(N_z_AlN) + 0.5) * dz_AlN
z = np.concatenate([z_Si, z_He, z_AlN])

i_Si_top    = 0
i_Si_bot    = N_z_Si - 1
i_He_top    = N_z_Si
i_He_bot    = N_z_Si + N_z_He - 1
i_AlN_top   = N_z_Si + N_z_He
i_AlN_bot   = N_z - 1

# Half-cell distances (for boundary faces at z=0 and z=t_stack)
dz_half_top    = dz_Si  / 2     # node 0 (top Si)  to z=0 boundary
dz_half_bottom = dz_AlN / 2     # node N_z-1 (bot AlN) to z=t_stack boundary

# Conductivity per z-node (axial). For the He gap, we use an equivalent
# bulk-k that produces the right film conductance: total resistance through
# the gap = t_He / k_He_eq = 1 / h_He   =>   k_He_eq = h_He * t_He.
k_layer = np.empty(N_z)
k_layer[:N_z_Si]              = k_Si
k_He_eq = h_He * t_He
k_layer[N_z_Si:N_z_Si+N_z_He] = k_He_eq
k_layer[N_z_Si+N_z_He:]       = k_AlN


# --- Beam source -----------------------------------------------------------

def gaussian_beam_flux(r_grid, P_total, sigma):
    """Areal heat flux (W/m^2) at radius r for a Gaussian beam of total power P."""
    return P_total / (2 * np.pi * sigma**2) * np.exp(-r_grid**2 / (2 * sigma**2))

# Two beam profiles:
# (1) STATIONARY: the column dwells at r=0 -- worst-case Gaussian (sigma=10 mm)
# (2) SCANNED:   uniform 65 W over the full 300 mm wafer area (920 W/m^2)
#                -- this is the stage-averaged operating mode the v4 +/-8 mK
#                claim refers to (v4 6.5 "the column footprint moves across
#                the wafer at 1-10 Hz stage speed").

q_stationary = gaussian_beam_flux(r, P_beam, sigma_beam)
P_recovered = np.trapezoid(2 * np.pi * r * q_stationary, r)
q_stationary *= P_beam / P_recovered   # rescale to hit exact 65 W on disk

q_scanned = np.full_like(r, P_beam / (np.pi * R**2))   # uniform 920 W/m^2

print(f"[init] Stationary Gaussian beam: peak flux = {q_stationary.max():.3e} W/m^2 "
      f"(sigma={sigma_beam*1e3:.0f} mm, FWHM={sigma_beam*2.355*1e3:.1f} mm)")
print(f"[init] Scanned uniform load    : flux      = {q_scanned[0]:.1f} W/m^2 "
      f"(= 65 W / disk area)")

# Default: q_top is set per-case below.
q_top = q_stationary

# Radiative cooling -- linearize around T_setpoint as a Robin BC
h_rad = 4 * eps_rad * F_rad * sigma_SB * T_setpoint**3      # W/m^2/K
T_rad_equiv = T_setpoint - (sigma_SB * eps_rad * F_rad
                            * (T_setpoint**4 - T_cold_column**4) / h_rad)
print(f"[init] h_rad (linearized)          = {h_rad:.3f} W/m^2/K")
print(f"[init] equivalent radiation T sink = {T_rad_equiv:.3f} K")
print(f"[init] mesh: N_r x N_z = {N_r} x {N_z} = {N_r*N_z} cells "
      f"({N_r*(N_z-1)} unknowns after Dirichlet bottom)")


# --- Build sparse system ---------------------------------------------------

def build_system(q_top_profile):
    """
    Build sparse linear system A T = b_const + b_BC for the steady-state
    heat equation on the (r, z) cell-centered finite-volume mesh.

    Ordering: idx(i, j) = i * N_z + j, with j in [0, N_z-1].
    All cells are unknowns. Boundary conditions enter through:
      - Top face of (i, 0): Robin radiative + beam (z=0).
      - Bottom face of (i, N_z-1): Dirichlet T_bottom(r) at z=t_stack,
        coupled via conductance k_AlN * A_z / dz_half_bottom.
      - Axis r=0 and rim r=R: adiabatic (no flux).

    Parameters
    ----------
    q_top_profile : (N_r,) array of areal flux W/m^2 deposited on the wafer top.

    Returns: A (CSC), b_const, b_bottom_coef (per-i scale that multiplies
             case-specific T_bottom[i] into the (i, N_z-1) row's RHS).
    """
    # Axial face conductances per UNIT AREA (W/m^2/K).
    # For face between cells j and j+1 with potentially different k and cell sizes,
    # the proper series resistance is (dz_j/2)/k_j + (dz_{j+1}/2)/k_{j+1},
    # NOT the equal-mesh harmonic-mean shortcut. This matters at the Si/He and
    # He/AlN interfaces where dz changes by orders of magnitude.
    dz_node_local = np.empty(N_z)
    dz_node_local[:N_z_Si]              = dz_Si
    dz_node_local[N_z_Si:N_z_Si+N_z_He] = dz_He
    dz_node_local[N_z_Si+N_z_He:]       = dz_AlN
    R_face_z = (dz_node_local[:-1] / (2 * k_layer[:-1])
                + dz_node_local[1:] / (2 * k_layer[1:]))        # (N_z-1,)
    Gz_face = 1.0 / R_face_z                                    # (N_z-1,)
    Gr_face = k_layer / dr                                      # (N_z,) -- radial: same k both sides

    # Axial face areas (ring areas) at radial cell i -- same for all z
    A_z = np.empty(N_r)
    A_z[0]    = np.pi * (dr/2)**2
    A_z[-1]   = 2 * np.pi * r[-1] * (dr/2)
    A_z[1:-1] = 2 * np.pi * r[1:-1] * dr

    # Cell axial extents: dz_Si in Si layer, dz_He in He layer, dz_AlN in AlN
    dz_node = np.empty(N_z)
    dz_node[:N_z_Si]              = dz_Si
    dz_node[N_z_Si:N_z_Si+N_z_He] = dz_He
    dz_node[N_z_Si+N_z_He:]       = dz_AlN

    # Radial face areas at i+1/2 -- shape (N_r, N_z)
    A_r_plus = np.outer(2 * np.pi * (r + dr/2), dz_node)

    # Conductances per face (W/K)
    K_z      = np.outer(A_z, Gz_face)            # (N_r, N_z-1)
    K_r_plus = A_r_plus * Gr_face[None, :]       # (N_r, N_z)

    # Top Robin coupling + beam source (face at z=0, dz_half_top from node 0)
    # Combined series: k_Si conduction over dz_half_top THEN h_rad to T_rad_equiv,
    # in parallel with q_beam source.
    # For Robin BC q = h_rad (T_inf - T_face) and conduction in solid
    # q = k_Si (T_face - T_node0) / dz_half_top, eliminate T_face:
    #   q = (T_inf - T_node0) / (1/h_rad + dz_half_top/k_Si)
    # so the effective "top conductance" is:
    U_top = 1.0 / (1.0/h_rad + dz_half_top/k_Si)      # W/m^2/K
    K_top_rad = U_top * A_z                            # (N_r,)
    S_beam    = q_top_profile * A_z                    # (N_r,) -- the beam
                                                       # is absorbed at the wafer top surface

    # Bottom Dirichlet coupling: face at z=t_stack, distance dz_half_bottom
    # from node N_z-1, pure conduction through k_AlN.
    K_bot_dir = (k_AlN / dz_half_bottom) * A_z         # (N_r,)

    N_unk = N_r * N_z
    def idx(i, j):
        return i * N_z + j

    rows = []
    cols = []
    vals = []
    b_const = np.zeros(N_unk)

    for i in range(N_r):
        for j in range(N_z):
            n = idx(i, j)
            d = 0.0

            # Up neighbour (j-1)
            if j > 0:
                c = K_z[i, j - 1]
                rows.append(n); cols.append(idx(i, j - 1)); vals.append(-c)
                d += c
            else:
                # j == 0: top boundary -- combined Robin+conduction + beam source
                d += K_top_rad[i]
                b_const[n] += K_top_rad[i] * T_rad_equiv + S_beam[i]

            # Down neighbour (j+1)
            if j < N_z - 1:
                c = K_z[i, j]
                rows.append(n); cols.append(idx(i, j + 1)); vals.append(-c)
                d += c
            else:
                # j == N_z-1: bottom Dirichlet -- diagonal gets K_bot_dir;
                # b += K_bot_dir * T_bottom[i] (added per-case)
                d += K_bot_dir[i]

            # Inner radial neighbour (i-1)
            if i > 0:
                c = K_r_plus[i - 1, j]
                rows.append(n); cols.append(idx(i - 1, j)); vals.append(-c)
                d += c
            # Outer radial neighbour (i+1)
            if i < N_r - 1:
                c = K_r_plus[i, j]
                rows.append(n); cols.append(idx(i + 1, j)); vals.append(-c)
                d += c

            rows.append(n); cols.append(n); vals.append(d)

    A = sp.csr_matrix((vals, (rows, cols)), shape=(N_unk, N_unk))

    # Per-radius coefficient that multiplies T_bottom[i] into the RHS of cell
    # (i, N_z-1): equals K_bot_dir[i].
    b_bottom_coef = K_bot_dir

    geom = dict(A_z=A_z, dz_node=dz_node, A_r_plus=A_r_plus,
                K_z=K_z, K_r_plus=K_r_plus, K_top_rad=K_top_rad,
                K_bot_dir=K_bot_dir, S_beam=S_beam,
                U_top=U_top)
    return A.tocsc(), b_const, b_bottom_coef, geom


def solve_steady(case_label, delta_TEC, A, b_const, b_bottom_coef):
    """Solve A T = b for one TEC residual pattern; return (N_r, N_z) field.

    The chuck-back Dirichlet pattern T_bottom(r) = 295 K + delta_TEC * pattern
    is applied at z = t_stack (below the bottommost AlN node) via the
    half-cell conductance K_bot_dir.
    """
    TEC_pattern = delta_TEC * (
          0.7 * np.cos(np.pi * r / R)              # bulk inlet->outlet half-cosine
        + 0.3 * np.cos(2 * np.pi * r / 0.050)      # 36-zone hex ripple
    )
    T_bottom = T_setpoint + TEC_pattern

    b = b_const.copy()
    # cell (i, N_z-1) gets b += K_bot_dir[i] * T_bottom[i]
    for i in range(N_r):
        n = i * N_z + (N_z - 1)
        b[n] += b_bottom_coef[i] * T_bottom[i]

    t0 = time.time()
    x = spla.spsolve(A, b)
    t1 = time.time()
    res = np.max(np.abs(A @ x - b))
    print(f"[{case_label}] direct sparse solve: {(t1-t0)*1e3:.0f} ms, "
          f"residual ||Ax-b||_inf = {res:.3e}")
    T = x.reshape((N_r, N_z))
    return T, T_bottom


# --- Run -------------------------------------------------------------------

print("\nBuilding sparse FV systems ...")
t0 = time.time()
A_stat,  b_const_stat,  b_bot_coef, _ = build_system(q_stationary)
A_scan,  b_const_scan,  _,          _ = build_system(q_scanned)
print(f"  built in {time.time()-t0:.2f} s, nnz = {A_stat.nnz}")

print("\n" + "="*72)
print("Case 1a: STATIONARY column (Gaussian sigma=10 mm), TEC trim ACTIVE")
print("         -- worst-case spec stress; v4 6.5 admits this case is")
print("         catastrophic without stage motion or wider column")
print("="*72)
T_stat_on,  T_bot_on  = solve_steady("STAT TEC-ON ", delta_TEC=delta_TEC_on,
                                     A=A_stat, b_const=b_const_stat,
                                     b_bottom_coef=b_bot_coef)
print("\n" + "="*72)
print("Case 1b: STATIONARY column,  TEC trim DISABLED")
print("="*72)
T_stat_off, T_bot_off = solve_steady("STAT TEC-OFF", delta_TEC=delta_TEC_off,
                                     A=A_stat, b_const=b_const_stat,
                                     b_bottom_coef=b_bot_coef)

print("\n" + "="*72)
print("Case 2a: SCANNED uniform 920 W/m^2 (= 65 W / wafer area),")
print("         TEC trim ACTIVE  -- the v4 nominal operating mode that")
print("         the +/-8 mK across-wafer claim refers to")
print("="*72)
T_scan_on,  _ = solve_steady("SCAN TEC-ON ", delta_TEC=delta_TEC_on,
                             A=A_scan, b_const=b_const_scan,
                             b_bottom_coef=b_bot_coef)
print("\n" + "="*72)
print("Case 2b: SCANNED uniform load, TEC trim DISABLED")
print("="*72)
T_scan_off, _ = solve_steady("SCAN TEC-OFF", delta_TEC=delta_TEC_off,
                             A=A_scan, b_const=b_const_scan,
                             b_bottom_coef=b_bot_coef)

# Aliases for the legacy "TEC ON / OFF" labels used by the figure block:
# the ±8 mK SPEC applies to the scanned (stage-averaged) case.
T_on  = T_scan_on
T_off = T_scan_off


# --- Diagnostics -----------------------------------------------------------

def report(T, label):
    # Wafer-top SURFACE temperature: extrapolate from node-0 (at z=dz_Si/2)
    # through the dz_half_top distance to z=0 using the radiative-Robin BC,
    # giving the actual top-face temperature.
    # Net flux into top face = K_top_rad/A_z * (T_face - T_rad_equiv) + q_beam
    # = q_into_node = k_Si/dz_half_top * (T_node0 - T_face)
    # Solve for T_face: not strictly needed; T_node0 is a fine proxy
    # since Bi << 1 across dz_half_top. We report the node-0 value.
    T_wafer_top  = T[:, i_Si_top]
    T_wafer_back = T[:, i_Si_bot]
    T_chuck_top  = T[:, i_AlN_top]
    T_chuck_back = T[:, i_AlN_bot]
    dT_top = T_wafer_top.max() - T_wafer_top.min()
    dT_chk = T_chuck_top.max() - T_chuck_top.min()
    print(f"\n--- {label} ---")
    print(f"  Wafer-top T  : min={T_wafer_top.min():.5f} K  "
          f"max={T_wafer_top.max():.5f} K  ΔT={dT_top*1e3:.4f} mK")
    print(f"  Wafer-back T : min={T_wafer_back.min():.5f} K  "
          f"max={T_wafer_back.max():.5f} K  ΔT={(T_wafer_back.max()-T_wafer_back.min())*1e3:.4f} mK")
    print(f"  Chuck-top T  : min={T_chuck_top.min():.5f} K  "
          f"max={T_chuck_top.max():.5f} K  ΔT={dT_chk*1e3:.4f} mK")
    print(f"  Chuck-bot T  : min={T_chuck_back.min():.5f} K  "
          f"max={T_chuck_back.max():.5f} K (Dirichlet face at z=t_stack: 295 K + TEC pattern)")
    print(f"  He-gap drop  : "
          f"{np.mean(T_wafer_back - T_chuck_top)*1e3:.2f} mK   "
          f"(analytic 65W/(h_He*A_w) = {P_beam/(h_He*np.pi*R**2)*1e3:.1f} mK -- bulk offset)")
    placement_nm = alpha_Si * dT_top * 2 * R * 1e9
    print(f"  -> α_Si * ΔT * 300 mm = {placement_nm:.3f} nm  "
          f"({'PASS' if placement_nm < 6 else 'FAIL'} 6 nm placement budget)")
    return dT_top, placement_nm

print("\n" + "#"*72)
print("# STATIONARY column (worst-case stress test, not the spec mode)")
print("#"*72)
dT_stat_on,  pl_stat_on  = report(T_stat_on,  "STATIONARY  TEC ON")
dT_stat_off, pl_stat_off = report(T_stat_off, "STATIONARY  TEC OFF")

print("\n" + "#"*72)
print("# SCANNED uniform load (the v4 +/-8 mK spec applies HERE)")
print("#"*72)
dT_on,  pl_on  = report(T_on,  "SCANNED  TEC ON")
dT_off, pl_off = report(T_off, "SCANNED  TEC OFF")

print()
print(f"v4 spec (applies to SCANNED, stage-averaged): ΔT_wafer < ±7.7 mK")
print(f"  (=> alpha_Si * ΔT * 300 mm < 6 nm placement budget)")
spec_pass_on  = dT_on  * 1e3 < 7.7
spec_pass_off = dT_off * 1e3 < 7.7
print(f"  SCANNED  TEC ON  : ΔT = {dT_on*1e3:.4f} mK   -->  {'PASS' if spec_pass_on else 'FAIL'}")
print(f"  SCANNED  TEC OFF : ΔT = {dT_off*1e3:.4f} mK  -->  {'PASS' if spec_pass_off else 'FAIL'}")
print(f"  STATIONARY TEC ON: ΔT = {dT_stat_on*1e3:.1f} mK  --  catastrophic, "
      f"as v4 6.5 admits (requires stage motion or 50 mm column geometry)")

# Decompose the TEC-ON residual in the spec-relevant (scanned) case
T_on_top = T_on[:, 0]
print(f"\nResidual decomposition (SCANNED, TEC ON):")
print(f"  Wafer-top centre - edge      = {(T_on_top[0]-T_on_top[-1])*1e3:.4f} mK")
print(f"  Wafer-top centre - mean      = {(T_on_top[0]-T_on_top.mean())*1e3:.4f} mK")
T_He_drop = T_on[:, i_Si_bot] - T_on[:, i_AlN_top]
print(f"  He-gap drop spread (max-min) : {(T_He_drop.max()-T_He_drop.min())*1e3:.4f} mK")
print(f"  He-gap drop mean             : {T_He_drop.mean()*1e3:.2f} mK")


# --- Figure ----------------------------------------------------------------

fig = plt.figure(figsize=(13.5, 10.0))
gs = fig.add_gridspec(3, 2, height_ratios=[1.1, 1.0, 1.0], hspace=0.50, wspace=0.32)

z_mm = z * 1e3
r_mm = r * 1e3
R_grid, Z_grid = np.meshgrid(r_mm, z_mm, indexing='ij')

# (a) 2D heat map: STATIONARY case (worst-case), TEC ON
ax = fig.add_subplot(gs[0, 0])
im = ax.pcolormesh(R_grid, Z_grid, T_stat_on, shading='auto', cmap='inferno')
ax.invert_yaxis()
ax.set_xlabel("radius r  (mm)")
ax.set_ylabel("depth z  (mm)  [wafer top -> chuck back]")
ax.set_title(f"(a) T(r,z) -- STATIONARY column (Gaussian σ=10 mm), TEC ON\n"
             f"ΔT_wafer = {dT_stat_on*1e3:.1f} mK  (catastrophic, see v4 §6.5)")
cb = plt.colorbar(im, ax=ax); cb.set_label("T (K)")
ax.axhline(t_Si*1e3, color='cyan', lw=0.6, ls='--', alpha=0.7)
ax.axhline((t_Si+t_He)*1e3, color='cyan', lw=0.6, ls='--', alpha=0.7)
ax.text(R*1e3*0.97, t_Si*1e3*0.5, "Si", color='cyan', ha='right',
        va='center', fontsize=8, alpha=0.8)
ax.text(R*1e3*0.97, (t_Si+t_He)*1e3*1.5, "AlN", color='cyan', ha='right',
        va='top', fontsize=8, alpha=0.8)

# (b) 2D heat map: SCANNED uniform load, TEC ON
ax = fig.add_subplot(gs[0, 1])
im = ax.pcolormesh(R_grid, Z_grid, T_on, shading='auto', cmap='inferno')
ax.invert_yaxis()
ax.set_xlabel("radius r  (mm)")
ax.set_ylabel("depth z  (mm)")
ax.set_title(f"(b) T(r,z) -- SCANNED uniform 920 W/m² (spec mode), TEC ON\n"
             f"ΔT_wafer = {dT_on*1e3:.3f} mK")
cb = plt.colorbar(im, ax=ax); cb.set_label("T (K)")
ax.axhline(t_Si*1e3, color='cyan', lw=0.6, ls='--', alpha=0.7)
ax.axhline((t_Si+t_He)*1e3, color='cyan', lw=0.6, ls='--', alpha=0.7)

# (c) 1D radial wafer-top profile -- SCANNED (spec) case, TEC ON vs OFF
ax = fig.add_subplot(gs[1, 0])
ax.plot(r_mm, (T_on[:, 0]  - T_setpoint) * 1e3, lw=2,
        label=f"TEC ON   (ΔT={dT_on*1e3:.3f} mK, {pl_on:.3f} nm)")
ax.plot(r_mm, (T_off[:, 0] - T_setpoint) * 1e3, lw=2,
        label=f"TEC OFF  (ΔT={dT_off*1e3:.3f} mK, {pl_off:.3f} nm)")
ax.axhspan(-7.7, 7.7, color='green', alpha=0.10,
           label="v4 spec ±7.7 mK (6 nm budget)")
ax.set_xlabel("radius r  (mm)")
ax.set_ylabel("T(r, z=0) - 295 K   (mK)")
ax.set_title("(c) SCANNED case -- wafer-top profile (the spec)")
ax.grid(alpha=0.3)
ax.legend(loc='best', fontsize=9)

# (d) 1D radial wafer-top profile -- STATIONARY (worst-case)
ax = fig.add_subplot(gs[1, 1])
ax.plot(r_mm, T_stat_on[:, 0]  - T_setpoint, lw=2,
        label=f"TEC ON   (ΔT={dT_stat_on*1e3:.1f} mK = {dT_stat_on:.1f} K, {pl_stat_on:.0f} nm)")
ax.plot(r_mm, T_stat_off[:, 0] - T_setpoint, lw=2, ls='--',
        label=f"TEC OFF  (ΔT={dT_stat_off*1e3:.1f} mK, {pl_stat_off:.0f} nm)")
ax.set_xlabel("radius r  (mm)")
ax.set_ylabel("T(r, z=0) - 295 K   (K)")
ax.set_title("(d) STATIONARY case -- wafer-top profile (worst-case)")
ax.grid(alpha=0.3)
ax.legend(loc='best', fontsize=9)

# (e) Beam profiles
ax = fig.add_subplot(gs[2, 0])
ax.plot(r_mm, q_stationary / 1e3, color='crimson', lw=2,
        label=f"STATIONARY Gaussian (σ={sigma_beam*1e3:.0f} mm, peak {q_stationary.max()/1e3:.1f} kW/m²)")
ax.plot(r_mm, q_scanned / 1e3, color='gray', lw=2, ls='--',
        label=f"SCANNED uniform ({q_scanned[0]:.0f} W/m² = 0.92 kW/m²)")
ax.set_yscale('log')
ax.set_xlabel("radius r  (mm)")
ax.set_ylabel("areal heat flux  (kW/m²)")
ax.set_title("(e) Beam-deposition profiles, 65 W total each")
ax.grid(alpha=0.3, which='both')
ax.legend(loc='best', fontsize=9)

# (f) Chuck-top temperature for SCANNED case
ax = fig.add_subplot(gs[2, 1])
ax.plot(r_mm, (T_on[:,  i_AlN_top] - T_setpoint) * 1e3, color='navy',
        lw=1.8, label="TEC ON")
ax.plot(r_mm, (T_off[:, i_AlN_top] - T_setpoint) * 1e3, color='steelblue',
        lw=1.8, ls='--', label="TEC OFF")
ax.set_xlabel("radius r  (mm)")
ax.set_ylabel("T_chuck-top - 295 K  (mK)")
ax.set_title("(f) SCANNED case -- chuck-top temperature (Dirichlet-driven)")
ax.grid(alpha=0.3)
ax.legend(loc='best', fontsize=9)

plt.suptitle("v4 wafer chuck -- 2D axisymmetric FV thermal FEA, 65 W steady beam",
             fontsize=13, fontweight='bold')

plt.savefig("/home/thedoctor/mbm_spacecharge/figure_phase3_wafer_fea.pdf",
            bbox_inches='tight')
plt.savefig("/home/thedoctor/mbm_spacecharge/figure_phase3_wafer_fea.png",
            bbox_inches='tight', dpi=150)
print("\nFigure written: figure_phase3_wafer_fea.{pdf,png}")


# --- Summary ---------------------------------------------------------------

print()
print("="*72)
print("SUMMARY")
print("="*72)
print(f"  Beam power deposited            : {P_beam:.1f} W total")
print(f"  He-gap bulk offset (SCANNED)    : "
      f"{(T_on[:, i_Si_bot]-T_on[:, i_AlN_top]).mean()*1e3:.1f} mK  "
      f"(analytic 65 W / (h_He*A_w) = "
      f"{P_beam/(h_He*np.pi*R**2)*1e3:.1f} mK -- bulk, not spatial)")
print()
print(f"  STATIONARY column (Gaussian σ={sigma_beam*1e3:.0f} mm), worst-case test:")
print(f"    Wafer ΔT_max TEC ON       : {dT_stat_on*1e3:.1f} mK ({pl_stat_on:.0f} nm)  "
      f"-- CATASTROPHIC, as v4 §6.5 admits")
print(f"    Wafer ΔT_max TEC OFF      : {dT_stat_off*1e3:.1f} mK ({pl_stat_off:.0f} nm)")
print()
print(f"  SCANNED uniform 920 W/m² (the v4 ±8 mK spec mode):")
print(f"    Wafer ΔT_max TEC ON       : {dT_on*1e3:.4f} mK  "
      f"(placement {pl_on:.4f} nm)")
print(f"    Wafer ΔT_max TEC OFF      : {dT_off*1e3:.4f} mK "
      f"(placement {pl_off:.4f} nm)")
print(f"    v4 spec (ΔT < ±7.7 mK)    : "
      f"TEC ON  {'PASS' if spec_pass_on else 'FAIL'},   "
      f"TEC OFF {'PASS' if spec_pass_off else 'FAIL'}")
print(f"    TEC suppression ratio     : {dT_off/max(dT_on,1e-9):.1f}× "
      f"(the 36-zone trim suppresses the microchannel pattern)")

# Diagnose dominant residual gradient in SCANNED TEC ON
top_grad     = T_on[:, 0].max() - T_on[:, 0].min()
He_drop_var  = (T_on[:, i_Si_bot] - T_on[:, i_AlN_top]).max() \
             - (T_on[:, i_Si_bot] - T_on[:, i_AlN_top]).min()
chuck_grad   = T_on[:, i_AlN_top].max() - T_on[:, i_AlN_top].min()
print()
print(f"  Dominant residual gradient sources (SCANNED, TEC ON):")
print(f"    He-gap drop variation across r  = {He_drop_var*1e3:.4f} mK")
print(f"    Chuck-top T variation across r  = {chuck_grad*1e3:.4f} mK")
print(f"    -> Wafer-top spread             = {top_grad*1e3:.4f} mK")
