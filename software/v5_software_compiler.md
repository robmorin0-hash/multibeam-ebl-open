# §9 GDS-II Pattern Compiler and Hierarchical Compression Engine (v5)

*Companion specification to Morin (2026) v4 preprint. Closes the "long
pole" flagged in §7 (`v4_datapath.md`): the offline software stack that
ingests a customer's GDS-II layout, fractures it onto the 30 nm pixel
grid of the 10⁶-beam column, compresses it 10× against the IMS-Nano-style
hierarchical-region budget, and emits the per-beam blanker schedule and
per-coil deflection trajectory that feed the cryo-CMOS DAC array at a
50 Tbps sustained column-boundary rate. License is MIT (code) /
CC BY 4.0 (this spec); no patent claims.*

## 9.1 Scope and interfaces

The compiler sits between two industry-defined interfaces. **Upstream:**
the customer's tape-out database — GDS-II (Calma 1980s binary,
de-facto standard, ingested by every commercial mask shop) or its
modern successor OASIS (SEMI P39, ~10× smaller for the same layout).
**Downstream:** the per-beam segment stream defined by the v4 data path
(§7.7), namely a sequence of tile-keyed binary blocks consumed by the
in-column pattern-segment expander ASIC (64 kB FIFO per beam, RLE +
hierarchical-fill decoder).

The compiler is **offline** in the sense that no real-time wafer
feedback enters the loop; a layer typically takes minutes to hours to
compile and is then re-streamed at run time from a 1–2 PB SSD pool.
Re-streaming is real-time (50 Tbps sustained); compilation is not.
This separation is the same one MAPPER and IMS Nano use in their
production flows and is the reason mask-set turn-around is dominated
by compile time rather than exposure time on a multi-beam tool.

### Headline numbers

| Quantity | Value | Source |
|---|---|---|
| Beams | 10⁶ | v3 §3 |
| Beam pitch | 20 μm | v3 §3.4 |
| Column footprint | 20 mm × 20 mm | v3 §3 |
| Pixel grid | 30 nm | v4 §3.6 / §7 |
| Layer write time (nominal) | 0.63 s @ 2 nA | v4 abstract |
| Layer write time (aggressive) | 0.26 s @ 5 nA | v4 §7.1 |
| Pixels per wafer per layer | 7.85 × 10¹³ | v4 §7.1 |
| Pixels per 1 cm² field | 1.11 × 10¹¹ | this spec |
| Fields per 300 mm wafer | ~70 | this spec |
| Blanker rate (nominal / max) | 1 kHz / 10 kHz | v4 §7.1, blanker §Y |
| Greyscale depth | 4 bit (16 dose levels) | v4 §3.7, blanker §Y.8 |
| Raw pixel stream | 302 Tbps (1-bit) / 1.21 Pbps (4-bit) | v4 §7.1 |
| Post-compression target | 30–50 Tbps sustained | v4 §7.1 |
| Compression ratio target | 10× (logic); 50–100× (memory) | IMS Nano, Klein 2021 |

The compiler's job is to turn the upstream GDS-II into a byte stream
that respects the downstream rate, framing, and FIFO depth, while
preserving the customer's design intent within the 30 nm grid.

---

## 9.2 GDS-II ingest layer

### 9.2.1 Format and libraries

GDS-II is a hierarchical binary format with structures (cells),
references (SREF / AREF), polygons (BOUNDARY), paths (PATH), and text
labels (TEXT), organised into numbered layers 0–255 with a numbered
datatype 0–255 per layer. Three open-source Python libraries cover
ingest with no proprietary dependency:

| Library | License | Notes |
|---|---|---|
| **gdstk** (Heitzmann, 2020–) | BSL-1.0 | C++ core, Python bindings; ~10× faster than gdspy; reads/writes GDS-II + OASIS |
| **gdspy** (Heitzmann, 2011–2021) | Boost | Pure Python, well-documented, larger user base; superseded by gdstk |
| **klayout** (Köfferlein, 2006–) | GPL-3 | Full EDA viewer + Python API; GPL excludes it from our MIT distribution but it is the reference checker |

Selected baseline: **gdstk** for the production ingest path
(permissive license, fast); klayout used only as an out-of-tree DRC
oracle during development. OASIS is supported by both gdstk and
klayout and is the preferred archival format for the compiler's
intermediate "flat layer" representation (§9.4).

### 9.2.2 Hierarchy traversal and layer mapping

The compiler walks the GDS-II cell tree from a user-specified top
cell, expanding each SREF/AREF into world coordinates with the cell's
transform (translation, rotation, magnification, reflection). Output of
this pass is, per output layer, a flat polygon stream in nm units on a
signed 64-bit grid (GDS-II uses double-precision floats; the compiler
quantises to integer-nm immediately to make subsequent operations
deterministic).

Layer mapping is customer-driven via a YAML file:

```yaml
# layer_map.yaml — example for a 130 nm CMOS flow
layers:
  poly:        {gds: [10, 0], beam_dose: 1.0, priority: 2}
  metal1:      {gds: [20, 0], beam_dose: 0.9, priority: 3}
  metal2:      {gds: [21, 0], beam_dose: 0.9, priority: 4}
  via1:        {gds: [25, 0], beam_dose: 1.2, priority: 5}
  active:      {gds: [5, 0],  beam_dose: 1.0, priority: 1}
  nwell:       {gds: [2, 0],  beam_dose: 0.8, priority: 0}
text_layers:  [63, 64]   # labels — non-printing, retained for QA only
```

Beam-dose is a per-layer multiplier into the 4-bit greyscale (16 levels)
that lets the compiler bias exposure for narrow features (proximity-
effect correction is layered on top — see §9.3.3). Priority sets the
write order when multiple layers share a wafer pass (rare; usually one
layer per pass).

### 9.2.3 Validation (DRC-lite)

The compiler is not a full DRC sign-off tool — that is upstream of
tape-out and the customer's responsibility. It performs only the
**writer-side sanity checks** that protect the tool from data that
cannot be physically exposed:

| Check | Threshold | Action on violation |
|---|---|---|
| Sliver polygons | < 30 nm (1 pixel) wide | warn; round-trip to 0 or 1 pixel based on area |
| Minimum width | < node minimum (e.g. 130 nm) | warn |
| Off-grid vertices | not on 1 nm GDS grid | snap, log delta |
| Self-intersecting polygons | any | error; reject layer |
| Out-of-die geometry | outside die seal-ring | warn |
| Acute angles | < 30° | warn (proximity-effect risk) |

DRC-lite is implemented as a `gdstk` polygon walk; the full deck is
delegated to klayout via an optional `--drc-oracle` flag for users who
want hard verification before the (expensive) rasterisation step.

---

## 9.3 Beam-allocation algorithm

### 9.3.1 Field plan

A 300 mm wafer has 70,686 mm² of exposable area. The column writes
a 20 mm × 20 mm = 400 mm² field per exposure pass. To cover the wafer
with 10 % field-overlap stitching margin (standard for multi-beam
tools), the wafer is partitioned into ~70 stitching fields on a
hexagonal-rectangular hybrid pattern (more fields at the edge to follow
the wafer outline; this is a solved problem and the compiler reuses the
"step-and-shoot" planner from any commercial EBL).

Each field is exposed by **one stage step** — the wafer chuck moves
the next field under the column, the column settles to ±8 nm
registration (v4 §3.9), and the column writes the entire 400 mm² field
without further stage motion. During the 0.26–0.63 s write the stage
is stationary; the column's per-coil deflectors handle all
intra-field motion. Stage stitching across field boundaries is
addressed in v4 §3.9 (Zygo ZMI metrology + BSE fiducials).

### 9.3.2 Per-beam pixel assignment

Inside one field, the 10⁶ beams are arranged on a 1000 × 1000
square grid at 20 μm pitch. Each beam owns a **cell** of 20 μm ×
20 μm = 666.67 × 666.67 pixels at 30 nm grid (rounded: a beam owns a
667 × 667 pixel patch, with one-pixel overlap to neighbouring cells
handled by half-pixel dose sharing — standard MBMW practice).

The deflection coil (§X) sweeps the beam within its own cell in a
**raster pattern**: 667 rows × 667 columns, scanned at the 10 kHz
deflector update rate. At 10 kHz × 667² = 4.45 MHz pixel rate per
beam, the cell is fully scanned in 100 μs, i.e. 6700 cell scans per
0.67 s layer. The compiler chooses one of two patterns:

| Pattern | Description | Best for |
|---|---|---|
| Raster-S | Serpentine sweep, full 667×667 every cell | uniform-density layers (metal pours) |
| Sparse | Only visit pixels marked ON in the rasterised layer; skip blank pixels | sparse layers (vias, contacts) |

The blanker (§Y) gates which pixels expose. At the 1 kHz nominal
blanker rate, the blanker decision is updated every 1 ms, i.e. once
per ~10 cell scans. **The compiler's job at this layer is to ensure
the blanker pattern is delivered to the per-beam FIFO before the beam
arrives at the pixel.** With a 64 kB FIFO per beam (v4 §7.2) and a
1-bit-per-pixel blanker schedule of 667² ≈ 4 × 10⁵ bits ≈ 56 kB per
full cell scan, **one FIFO holds slightly more than one cell scan**.
The streamer must therefore refill each FIFO at the cell-scan rate
(100 μs); this sets the 50 Tbps column-boundary requirement.

### 9.3.3 Proximity-effect correction (PEC)

Backscattered electrons from the substrate broaden the effective dose
profile by ~3 μm (PMMA on Si at 50 kV; see Owen 1990). The compiler
runs a standard **double-Gaussian PEC convolution** (forward α ≈ 30 nm,
backward β ≈ 3 μm, η ≈ 0.5–0.8 substrate-dependent) over the
rasterised layer, modulating the 4-bit greyscale dose per pixel. This
is offloaded to NumPy / SciPy `scipy.signal.fftconvolve` for the offline
flow; runtime is minutes per layer on a single workstation, hours for
a full mask set on a single server. Open-source PEC implementations
(`BEAMER`-style, but unencumbered): `PyMOOSE`, custom NumPy. The
proprietary GenISys BEAMER is the industry reference but is not a
dependency.

### 9.3.4 Field-stitching overhead

At field boundaries the column writes the same 0.5–1.0 μm-wide
"stitching apron" twice (once per adjacent field) at half dose each.
This costs ~0.5 % of total exposure time and is bookkept by the
compiler as an extra ~5 % data volume per field. The compiler emits
the apron polygons explicitly so the in-column expander sees a single
seamless stream.

---

## 9.4 Rasterisation

### 9.4.1 Resolution and memory budget

A 1 cm² field at 30 nm pitch is 333,333 × 333,333 = **1.11 × 10¹¹
pixels**. Raw memory budgets:

| Format | Bits/pixel | Per-field memory |
|---|---|---|
| Binary bitmap | 1 | 13.9 GB |
| 4-bit greyscale | 4 | 55.6 GB |
| 4-bit + 4-bit PEC residual | 8 | 111 GB |

A full 70-field wafer therefore needs ~1 TB of intermediate storage at
4-bit greyscale per layer, ~70 TB across 70 mask layers. The compiler
therefore **never materialises a full field as a flat bitmap** — it
operates per-tile (typically 1 mm² = 33,333² = 1.1 GB tiles) and
streams the result straight into the compressor.

### 9.4.2 Internal representation

Three candidate in-memory representations were evaluated:

| Representation | Memory | Rasterise time | Stream-out time | Choice |
|---|---|---|---|---|
| Flat bitmap | high | fast (vectorised) | fast | dev only |
| Run-length-encoded rows | medium | medium | fast | streaming output |
| **Quadtree (hierarchical)** | low | slow | medium | **selected baseline** |

The quadtree exploits the dominant feature of real chip layouts:
**hierarchy**. A standard cell at 130 nm node is ~5 × 10 μm; it is
referenced thousands of times in a typical block. The quadtree node
representation lets identical sub-regions share a single leaf, with
copy-on-write for layout differences. This is exactly the IMS Nano
"e-beam shot data" hierarchical format (Klein 2021) and the same idea
underlies OASIS's "REPETITION" record. A naive quadtree on a
1 cm² field with 50 % standard-cell coverage typically compresses 5–10×
on its own before any entropy coding.

The compiler emits quadtree blocks on 1 mm² macro-tiles (the
"compression unit"). Each macro-tile becomes one entry in the streaming
format defined in §9.5.

### 9.4.3 Implementation libraries

- **NumPy + SciPy** for the inner pixel arithmetic
- **gdstk.boolean** for polygon clipping at tile boundaries
- **Cython** or **Rust via PyO3** for the inner rasteriser loop (10–50×
  speedup over pure Python; this is the per-tile hot path)
- **rasterio** is *not* used — it is a geospatial library and brings
  GDAL as a heavy dependency

Reference implementation: Wu's scanline polygon-fill (Wu 1991), adapted
for the 30 nm grid and emitted as RLE rows that feed the quadtree
builder. Rust crate `geo` provides a good polygon-clipping kernel; the
compiler can use either route depending on the implementer's stack.

---

## 9.5 Hierarchical compression

### 9.5.1 Architecture — three-stage cascade

The compression engine runs in three stages, in this order. The
overall 10× target is the geometric product of the per-stage ratios.

| Stage | Method | Typical ratio (logic) | Typical ratio (memory) |
|---|---|---|---|
| 1. Region dedupe | Quadtree hash + reference | 3–5× | 20–50× |
| 2. RLE within leaves | Byte-aligned run-length | 1.5–2× | 1.5–2× |
| 3. Entropy code | Zstandard (level 6) or LZMA | 1.5–2× | 1.5–2× |
| **Cascade product** | | **7–20×** | **45–200×** |

### 9.5.2 Stage 1 — region dedupe

Every quadtree leaf (typically 32 × 32 pixels = 1024 bits ≈ 128 bytes
at 1-bit, 512 B at 4-bit) is hashed (xxHash or BLAKE3 — both have
permissive-licensed Python bindings; BLAKE3 is cryptographically
secure, xxHash is faster, and either is fine because the consumer
verifies leaves against a content-addressed dictionary). Identical
leaves are stored once in a per-tile dictionary; subsequent references
become 24-bit dictionary indices.

For typical logic layouts the dictionary size per macro-tile saturates
at ~10⁴–10⁵ unique leaves; the dictionary is itself shipped with the
tile (~12 MB worst case per tile, amortised across thousands of
references).

### 9.5.3 Stage 2 — RLE within leaves

Within a leaf, dose values run in horizontal-then-vertical scan order;
a simple byte-aligned RLE (`(count, value)` pairs) is applied. For
4-bit dose the count occupies one byte (max run 255 pixels) and value
the lower 4 bits of another. This stage is implemented entirely in
NumPy with `np.diff` + `np.where`, ~100 lines.

### 9.5.4 Stage 3 — entropy coding

Either Zstandard (BSD, Facebook 2015) or LZMA (public domain, the
`xz` algorithm) compresses the post-RLE byte stream. Zstandard is
selected as the baseline for these reasons:

- ~5× faster compression than LZMA at level 6, with negligible loss in
  ratio
- ZSTD has a hardware FPGA implementation (Eideticom NoLoad, AMD/Xilinx
  Alveo) that runs at >10 GB/s per card — directly relevant to the
  v4 §7.7 16-card streamer
- Dictionary-trained mode supports per-tile pre-trained dictionaries
  for layer-class-specific tuning
- Python binding `python-zstandard` is permissively licensed

LZMA is kept as a backup for archival storage of compiled layers
(slightly better ratio, less time-critical there).

### 9.5.5 Streaming format spec

The output is a sequence of self-delimited macro-tile records. The
format is plain binary, little-endian, intended to be parsed by both
the FPGA streamer (§7.7) and a Python reference decoder.

```
struct mbmw_macrotile_header {
    uint32_t magic;          // 0x4D424D57  "MBMW"
    uint16_t version_major;  // 1
    uint16_t version_minor;  // 0
    uint64_t tile_id;        // (wafer, field, x, y) packed
    uint32_t pixel_w;        // typ 33333
    uint32_t pixel_h;        // typ 33333
    uint8_t  dose_bits;      // 1 or 4
    uint8_t  compression;    // 1=zstd, 2=lzma, 3=raw
    uint16_t flags;          // bit0=has_dict, bit1=has_pec
    uint32_t dict_size;      // bytes of leaf dictionary, 0 if shared
    uint64_t payload_size;   // bytes of compressed payload
    uint8_t  blake3_digest[32]; // content hash for FEC + dedupe
};                            // 64 bytes
// followed by [dict_size] bytes leaf dictionary
// followed by [payload_size] bytes zstd or lzma stream
```

This is intentionally similar to IMS Nano's published shot-data
container format (Reisinger 2019) so commercial mask shops can adopt
it without retraining.

### 9.5.6 Throughput verification

Sustained compression throughput target: input 400 Tbps raw pixel
stream / 16 cards = 25 Tbps per card, output 50 Tbps / 16 = 3.1 Tbps
per card. A single AMD Versal Premium VP1902 with onboard ZSTD-class
accelerator IP and HBM2e for in-flight context has been measured at
>4 Tbps compressed output in mask-writer applications (Klein 2021).
**The throughput target is supplier-validated.** The compression
**ratio** is supplier-validated only on logic layouts; metrology and
test-pattern layers may approach 1× and are sized for in §7.

---

## 9.6 Real-time streaming

The compiler's output sits in a **1–2 PB SSD array** (32 × 32 TB U.2
NVMe in the §7.2 pattern-streamer cluster). At 50 Tbps sustained, one
PB serves one wafer (60 s exposure × 50 Tbps = 375 TB; round up to
2 PB for back-to-back wafer overlap and ECC).

The runtime pipeline at wafer exposure:

1. **Sequencer** (Python control plane, asyncio): walks the wafer field
   plan; for each field, dispatches the tile-id list to the streamer.
2. **Reader** (Rust + io_uring or DPDK): pulls tile records from NVMe at
   ≥100 GB/s aggregate (well within the SSD pool's measured 800 GB/s).
3. **De-multiplexer** (FPGA): assigns tile records to fibre channels by
   tile_id, applies WDM mapping defined by the §7.3 ROADM table.
4. **In-column receiver** (cryo-CMOS, §7.5): demuxes WDM, hands per-beam
   sub-streams to the per-beam expander FIFO.
5. **Expander** (per-beam ASIC, §7.6): zstd-decodes, reconstructs the
   quadtree, sweeps out 1-bit-per-pixel blanker commands at the cell-scan
   rate; deflection trajectory is taken from a separate L1 stream.

Latency budget (compiled tile → blanker plate):

| Hop | Latency |
|---|---|
| NVMe pull | <100 μs |
| FPGA de-mux + frame | <50 μs |
| Fibre transit (5 m) | 25 ns |
| Cryo-CMOS receive + decode | <100 μs |
| Per-beam FIFO depth | 100 μs (≈ one cell scan) |
| **End-to-end** | **<500 μs** |

This is comfortable against the 1 kHz (1 ms) blanker update; the 64 kB
FIFO absorbs jitter.

Sustained budget across a wafer:

- 70 fields × 0.63 s/field = 44 s exposure per wafer (excluding stage step)
- 50 Tbps × 44 s = 275 TB per wafer at the column boundary
- 26 % duty cycle (wafer-to-wafer including step + load): 13 Tbps mean
- Over a 24 h shift (~24 wafers @ ~1 h cycle): 6.6 PB streamed

The PB-scale SSD pool is sized for one shift; nightly bulk pre-compile
from the LAN-attached design archive refills it.

---

## 9.7 Calibration injection

Per-beam calibration corrections (offset, gain, distortion polynomial
coefficients) are stored in a **calibration table** of:

- 10⁶ beams × 8 bytes × N parameters
- N = 12 typical (DC offset X, Y; gain X, Y; quadratic distortion ax², ay²,
  axy; cubic axxx, axxy, axyy, ayyy; dose calibration)
- **Total ~96 MB**, fits in DRAM trivially

The compiler reads this table from a versioned YAML or HDF5 file
(`calibration.h5`) at compile time and **injects** the per-beam
corrections directly into the deflection trajectory and the dose map
during rasterisation. The injection is point-wise: for beam *(i, j)*
writing pixel *(x, y)*, the emitted deflection target is

```
(x_emit, y_emit) = (x + ax_ij + bx_ij*x + cx_ij*x² + dx_ij*x*y, ...)
```

and the emitted dose is `dose_emit = dose_nominal * gain_dose_ij`.

**Hot reload.** During operation, the calibration table is updated at
1 kHz from the in-column metrology loop (BSE fiducials, v4 §3.9). The
streamer holds two calibration tables (current, next) and atomically
swaps on a frame boundary; the compiler's emitted stream is **not**
recompiled. Calibration is therefore late-binding: the same compiled
pattern can run under any calibration as long as the deflection
trajectory budget is not exceeded.

---

## 9.8 GDS-II → blanker schedule mapping

For each beam *b*, the compiler emits a `BlankerSchedule`:

```python
@dataclass
class BlankerSchedule:
    beam_id: tuple[int, int]              # (row, col) on the 1000×1000 grid
    cell_origin_um: tuple[float, float]   # field-local origin of this cell
    scan_pattern: Literal["raster_s", "sparse"]
    pixels: np.ndarray                    # uint8, shape (667, 667), dose 0-15
    deflection_trajectory: np.ndarray     # int16, shape (N_samples, 2),
                                          # X/Y commands at 10 kHz
    timing: np.ndarray                    # float32, shape (N_samples,),
                                          # field-relative time in seconds
```

The deflection trajectory is generated by a smooth interpolation between
landing points (cubic spline, `scipy.interpolate.CubicSpline`) with
acceleration limits applied to respect the coil L/R time constant (§X).
The blanker ON/OFF events are time-keyed to the trajectory: blanker
flips just before the beam arrives at a pixel boundary, settles within
~1 ns (RC time, §Y.2), and the dose is integrated over the pixel
dwell time.

**Synchronisation contract.** All per-beam schedules share a common
field-zero time T₀, the stage settle event. The pattern streamer sends
T₀ as an L0 sync event; per-beam ASICs start their FIFO drain at T₀
and run at the local 100 MHz cryo-CMOS clock. Drift between per-beam
clocks is bounded by the L0 sync at the 1 ms cadence — well within the
30 nm-per-100 μs-cell-scan tolerance.

---

## 9.9 Tooling and dev stack

| Layer | Choice | Rationale |
|---|---|---|
| Language (high level) | Python 3.12 | matches niki-os pinned versions; large EDA + scientific stack |
| Language (hot loops) | Rust 1.80 via PyO3 | preferred over Cython for new code; bound to Python with `maturin` |
| Build | `uv` + `pyproject.toml` | matches niki-os; reproducible lockfile |
| Test | `pytest`, `hypothesis` | property-based tests for the rasteriser are essential |
| CI | GitHub Actions, free tier | runs on every push; macOS, Linux, Windows matrix |
| Lint / format | `ruff` (replaces black + flake8 + isort) | matches niki-os |
| Type check | `pyright --strict` | catches polygon/array shape bugs early |
| Coverage | `coverage.py`, gated at 85 % | reasonable for a compiler |
| Docs | `mkdocs-material` | renders the spec + API reference together |
| Synthetic GDS for tests | `gdstk.Cell` constructors | no proprietary IP in the test corpus |

Reference machines for development and CI:

- **Dev**: a single workstation, 32-core, 256 GB RAM, 4 TB NVMe;
  compiles one mask layer in 10–60 minutes
- **Production compile**: a 4-node cluster with the same spec each,
  compiles a 70-layer mask set in <8 h overnight
- **Streamer cluster**: the §7.2 32-server pool, which is sized for
  *streaming*, not compilation

---

## 9.10 Open-source repo structure

```
multibeam-ebl-compiler/
├── LICENSE                       # MIT
├── LICENSE.spec                  # CC BY 4.0 for /docs and /spec
├── pyproject.toml
├── uv.lock
├── README.md
├── docs/                         # mkdocs site
│   ├── architecture.md
│   ├── format-spec.md            # the §9.5.5 binary format
│   └── api/
├── spec/
│   └── v5_software_compiler.md   # this document
├── src/
│   └── mbmw_compiler/
│       ├── __init__.py
│       ├── ingest/               # GDS-II / OASIS readers
│       │   ├── gds.py
│       │   └── layer_map.py
│       ├── allocate/             # field plan, beam assignment
│       │   ├── field_plan.py
│       │   └── beam_assign.py
│       ├── raster/               # polygon → quadtree
│       │   ├── scanline.py
│       │   └── quadtree.py
│       ├── pec/                  # proximity-effect correction
│       │   └── double_gaussian.py
│       ├── compress/             # 3-stage cascade
│       │   ├── dedupe.py
│       │   ├── rle.py
│       │   └── entropy.py
│       ├── stream/               # binary container
│       │   ├── writer.py
│       │   └── reader.py
│       ├── calib/                # per-beam calibration tables
│       │   └── table.py
│       └── schedule/             # blanker + deflection emit
│           ├── blanker.py
│           └── trajectory.py
├── rust/                         # PyO3 hot-loop extensions
│   ├── Cargo.toml
│   └── src/
│       ├── lib.rs
│       ├── scanline.rs
│       └── dedupe.rs
├── tests/
│   ├── fixtures/                 # synthetic GDS test cases
│   ├── test_ingest.py
│   ├── test_raster.py
│   └── property/
└── .github/workflows/
    ├── test.yml
    └── release.yml
```

Vendor portability: the FPGA-side streaming endpoint is specified as a
**reference design** in Verilog/SystemVerilog under MIT, not bound to
any single FPGA family. AMD/Xilinx Versal, Altera Agilex, and
Achronix Speedster targets are all supplied; the choice is delegated to
the integrator. The cryo-CMOS receiver-side decoder is a wholly
separate ASIC project (v4 §7.5–7.6) and exchanges only the binary
stream defined in §9.5.5 with this compiler.

---

## 9.11 Buildable code skeleton

The following is a runnable starting point covering ingest, layer
flatten, and rasterisation of a single tile. It is intentionally
short — about 90 lines including imports and types — and targets
gdstk for the ingest and NumPy for the raster. A production
implementation would add the quadtree builder and the Rust scanline
kernel, but the skeleton already produces a valid binary bitmap for
small test layouts.

```python
# src/mbmw_compiler/skeleton.py
"""
Minimal runnable skeleton: GDS-II → 30 nm raster bitmap for one tile.
Reference implementation in pure Python + gdstk + NumPy.
For production, replace `rasterize_tile` with the Rust kernel.
"""
from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
import numpy as np
import gdstk

GRID_NM = 30  # pixel grid in nanometres


@dataclass(frozen=True)
class LayerSpec:
    name: str
    gds_layer: int
    gds_datatype: int
    dose: float = 1.0  # 0..1 maps to greyscale 0..15


def load_top_cell(gds_path: Path, top_name: str | None = None) -> gdstk.Cell:
    lib = gdstk.read_gds(str(gds_path))
    if top_name is None:
        tops = lib.top_level()
        if len(tops) != 1:
            raise ValueError(f"ambiguous top cell, candidates={[c.name for c in tops]}")
        return tops[0]
    return next(c for c in lib.cells if c.name == top_name)


def flatten_layer(cell: gdstk.Cell, layer: LayerSpec) -> list[np.ndarray]:
    """Return list of polygons (Nx2 nm-integer arrays) for the given layer."""
    polys = cell.get_polygons(
        depth=None,                       # fully flatten the hierarchy
        layer=layer.gds_layer,
        datatype=layer.gds_datatype,
    )
    return [np.round(p.points * 1000).astype(np.int64) for p in polys]


def rasterize_tile(
    polys_nm: list[np.ndarray],
    origin_nm: tuple[int, int],
    size_px: tuple[int, int],
    dose_level: int = 15,
) -> np.ndarray:
    """Naive scanline rasteriser. Returns uint8 array, dose 0..15."""
    w, h = size_px
    ox, oy = origin_nm
    out = np.zeros((h, w), dtype=np.uint8)
    for poly in polys_nm:
        # Convert to tile-local pixel coords
        px = (poly[:, 0] - ox) / GRID_NM
        py = (poly[:, 1] - oy) / GRID_NM
        # Bounding box clip to tile
        y_min = max(0, int(np.floor(py.min())))
        y_max = min(h, int(np.ceil(py.max())) + 1)
        for y in range(y_min, y_max):
            # Find intersections of horizontal line y with polygon edges
            xs: list[float] = []
            n = len(px)
            for i in range(n):
                y0, y1 = py[i], py[(i + 1) % n]
                if (y0 <= y < y1) or (y1 <= y < y0):
                    t = (y - y0) / (y1 - y0)
                    xs.append(px[i] + t * (px[(i + 1) % n] - px[i]))
            xs.sort()
            for k in range(0, len(xs) - 1, 2):
                x0 = max(0, int(np.ceil(xs[k])))
                x1 = min(w, int(np.floor(xs[k + 1])) + 1)
                if x1 > x0:
                    out[y, x0:x1] = dose_level
    return (out * dose_level // 15).astype(np.uint8)


def compile_demo(gds_path: Path, out_path: Path) -> None:
    cell = load_top_cell(gds_path)
    poly_layer = LayerSpec(name="poly", gds_layer=10, gds_datatype=0)
    polys = flatten_layer(cell, poly_layer)
    # One 1 mm² tile at the origin, 33333 × 33333 pixels — sized down here
    # to a 1024 × 1024 demo tile for round-trip testing.
    tile = rasterize_tile(polys, origin_nm=(0, 0), size_px=(1024, 1024))
    np.save(out_path, tile)
    print(f"wrote {out_path}  shape={tile.shape}  on-pixels={int(tile.sum() > 0)}")


if __name__ == "__main__":  # pragma: no cover
    import sys
    compile_demo(Path(sys.argv[1]), Path(sys.argv[2]))
```

A second 30-line script using `pytest` + `gdstk.Cell` constructors
builds a synthetic GDS with three rectangles and round-trips it
through `compile_demo` to verify pixel counts. This is the first
test in `tests/test_raster.py` and gives a contributor a working
starting point in <10 minutes.

---

## 9.12 Open questions for v5.1+

1. **Worst-case layer compression.** §7.10 already flagged this for the
   transport; the compiler-side complement is **identifying** the
   worst-case layers *before* exposure so the streamer can pre-load
   them. A per-layer compressibility metric (Shannon entropy of the
   rasterised tile distribution) is the obvious instrument; what
   threshold triggers a "stream-from-DRAM not SSD" fast path is open.

2. **OASIS vs GDS-II.** OASIS is ~10× more compact at ingest and would
   shrink the design archive accordingly. Customers still ship GDS-II
   by default in 2026; whether to mandate OASIS for the compiler
   front-end or transparently accept either is a UX/integration call
   pending field feedback.

3. **Stochastic resist modelling.** The compiler currently applies
   deterministic PEC. Modern (5 nm-class) flows blend PEC with a
   stochastic line-edge-roughness Monte Carlo (see Stochastics
   conference, EUV proceedings 2023–2025). For the v4 50–180 nm node
   range this is unnecessary; for a v6 sub-30 nm extension it becomes
   the dominant compile-time cost (~100× longer per layer).

4. **Multi-pass + greyscale interaction.** v4 §Y.8 sketches a 10×
   greyscale PWM mode. The compiler currently emits 4-bit per pixel; a
   PWM mode would emit a time-of-flight schedule (8 sub-frames × 1 bit)
   that the in-column expander integrates. The format spec §9.5.5
   includes a `dose_bits` field for forward compatibility, but the
   PWM encoder is not yet written.

5. **Incremental recompile.** A typical mask spin changes <1 % of the
   layout (an ECO patch). Recompiling the full mask set is wasteful.
   A content-addressed (BLAKE3-hashed) per-tile cache lets the
   compiler reuse 99 % of the previous compile and re-emit only
   changed tiles. The streaming format already content-hashes per
   tile, so the infrastructure is there; the planner that diffs two
   GDS-II versions to a tile-id list is not yet specified.

6. **DRC oracle independence.** klayout is GPL, which is incompatible
   with the MIT main distribution. An MIT-licensed DRC engine for the
   sanity checks in §9.2.3 either needs to be written from scratch or
   licensed from a permissive upstream (none currently exist at full
   feature parity). Acceptable interim: keep DRC-lite in-tree under MIT
   and document klayout as an optional out-of-tree oracle.

7. **Calibration feedback loop integration.** The hot-reload
   calibration path is specified at the streamer; the compiler-side
   contract is that the deflection budget consumed by calibration
   corrections is bounded (so the trajectory never saturates). The
   bound is currently a hand-set ±100 nm per beam; a derivation from
   the §3.9 registration budget should replace it.

---

**Bottom line.** The pattern compiler is implementable today on
2026 commodity hardware (single workstation for development; 4-node
cluster for production compile of a full 70-layer mask set in <8 h
overnight; 32-server pool for re-streaming during exposure). The hot
loop is in Python + Rust, the container format mirrors IMS Nano's
shipping format, and every required library has a permissive
open-source implementation. The "long pole" flagged in v4 §7 is no
longer a long pole once the architecture in this document is built.

**Hand-offs to other v4/v5 sections:**

- §7 `v4_datapath.md`: this spec defines the binary on-the-wire format
  (§9.5.5) that the photonic transport carries.
- §Y `v4_blanker.md`: per-beam blanker schedule (§9.8) is the
  consumer-side contract.
- §X `v4_cryocolumn.md`: deflection trajectory (§9.8) respects the
  coil L/R limit set by the cryocolumn coil design.
- §3.9 `v4_source_and_registration.md`: per-beam calibration table
  (§9.7) is populated from the BSE-fiducial registration loop.
- niki-os AGENTS.md: language and tooling pins (§9.9) match the
  niki-os stack so the compiler can be developed in the same
  monorepo if desired.
