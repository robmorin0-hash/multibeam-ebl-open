# v5 — Tool Operating System & Calibration Database

*Specification for the system-level software stack that operators and process
engineers use to run the Morin v4 multi-beam EBL tool. Hard real-time
firmware is out of scope (separate `v5_firmware.md`); this document covers
the soft-real-time supervisory layer, calibration archive, recipe/lot
management, operator GUI, telemetry pipeline, alarm system, and external
integration. All choices are vendor-listed and pinned. License of the
reference implementation: MIT (code), CC BY 4.0 (spec). Targets the same
open-source rigor as `v4_INTEGRATION.md`.*

---

## 0. Architecture overview

The tool OS is a five-plane stack:

| Plane | Responsibility | Latency budget | Tech |
|---|---|---:|---|
| **Field plane** | Per-beam DAC, blanker, source TIA, ZMI counter | 1 µs – 100 µs | FPGA + cryo-CMOS (firmware doc) |
| **Cell controller** | Per-tile (1024 beams) closed loops, BSE fiducial reads | 100 µs – 10 ms | RTOS on ARM Cortex-R52 (firmware doc) |
| **Supervisory** | Calibration apply, recipe dispatch, alarm aggregation, telemetry sink | 10 ms – 1 s | **Linux + Rust services, this doc** |
| **Operator/Process** | GUI, recipe edit, lot dispatch, diagnostic playback | 100 ms – human | **Next.js 15 SPA, this doc** |
| **Enterprise** | MES SECS/GEM, customer API, analytics warehouse | seconds – days | **Postgres 18 + VictoriaMetrics + MinIO + Grafana, this doc** |

The supervisory plane is the seam: it converts firmware telemetry
(Cap'n Proto over 10 GbE TSN, ~30 MB/s aggregate) into durable records,
and converts operator/MES intent (REST + WebSocket) into compiled recipe
artefacts that the cell controllers can execute. Everything above the
field plane runs on commodity Linux (Ubuntu 24.04 LTS pinned) on
x86_64-v3 control-room servers (2× Dell R760 or equivalent, dual Xeon
Gold 6526Y, 256 GB ECC RAM, 8× 3.84 TB NVMe in RAID-10).

---

## 1. Calibration database

### 1.1 Storage backends

| Data class | Volume | Backend | Pinned version |
|---|---|---|---|
| Structured calibration metadata (snapshots, who/when/recipe-id) | ~10 MB/snapshot | **PostgreSQL 18** | 18.0 |
| Per-beam coefficient blobs (deflection offset, blanker delay, emission profile) | ~100 MB/snapshot | **MinIO** (S3-compatible) | RELEASE.2025-10-15 |
| Time-series telemetry (thermal, registration, source emission) | ~100 GB/day | **VictoriaMetrics** cluster | 1.110.0 |
| Per-wafer exposure traces (raw firmware logs) | ~100 MB/wafer | **MinIO** + Parquet | as above |
| Recipe artefacts (GDS, dose maps, compiled firmware blobs) | ~1–10 GB/recipe | **MinIO** + content-addressed by SHA-256 | as above |
| Recipe source (versioned) | KB scale | **Gitea 1.22** (self-hosted) | 1.22.3 |

PostgreSQL is the index of record. MinIO holds large binary objects.
VictoriaMetrics absorbs the 100 GB/day telemetry firehose with ~10×
compression (typical of float64 deltas) → ~10 GB/day on disk →
3.6 TB/year, easily 5 years on an 80 TB pool. PostgreSQL itself stays
under 1 TB even at multi-year archive: only metadata, no blobs.

Choice rationale: VictoriaMetrics over InfluxDB because (a) Apache-2.0
not the post-3.0 commercial Influx model, (b) single binary, no
clustering license tier, (c) PromQL-compatible so Grafana works out of
the box.

### 1.2 Schema (structured side)

Five logical groups: **global**, **column**, **tile**
(per-column-subarray, 1024 beams), **beam**, and **snapshot**. A
*snapshot* is the atomic unit: it pins one row in every coefficient
table to a single `snapshot_id` UUID v7, signed by the process engineer
who took it. Snapshots are immutable; the active calibration is selected
by a pointer table (`active_snapshot`) that supports instant rollback.

A 50-line skeleton appears in §11.2.

### 1.3 Calibration procedures

| Procedure | Frequency | Operator role | Tool downtime | Output |
|---|---|---|---:|---|
| Deflection-coil offset (per beam) | Weekly + on cryo-cycle | Process engineer | 4 h | 10⁶ × 2 int16 |
| Blanker delay correction | Monthly | Process engineer | 1 h | 10⁶ × 1 int8 |
| Tip emission profile (extractor V vs I) | Daily startup | Operator | 15 min | 10⁶ × 8 float16 |
| Thermal correction map | Per-cryo-cycle | Process engineer | 2 h | 1000 × float32 (per subarray) |
| Registration zero (3-tier loop bias) | Per shift | Operator | 5 min | 10⁶ × 2 float32 |
| Source uniformity verification (BSE pattern) | Weekly | Process engineer | 30 min | 10⁶ × float32 + image |
| Full PM calibration (everything) | Quarterly + on hardware change | Process engineer + service | 24 h | full snapshot |

Each procedure is a versioned recipe in `recipes/calibration/` and runs
under the same dispatcher as production lots. The output is written
into a *pending* snapshot, validated against acceptance bands
(`acceptance.yaml`), then either *promoted* to active or rejected.

### 1.4 Snapshot/restore

Snapshots are MinIO objects under
`s3://mbm-cal/snapshots/{snapshot_id}/`. Each contains the coefficient
blobs, a manifest JSON, and a Cosign signature. Restore is
`mbm-cal restore --snapshot <uuid>` — atomic swap of `active_snapshot`,
push to cell controllers over the TSN fabric, ~30 s end-to-end.
Snapshots replicate to a secondary MinIO site (different building or
S3-compatible cloud — Backblaze B2, Wasabi, or AWS) via MinIO
site-replication. Retention: hot 1 year, warm 5 years, cold (Glacier
tier or LTO-9 tape via `restic`) indefinitely.

---

## 2. Recipe + lot management

### 2.1 Recipe model

A recipe is a directory in the recipe Git repo:

```
recipes/cust_abc/asic_v3/
├── recipe.yaml          # dose, layer count, exposure sequence, alignment
├── layer_01.gds         # or DXF/OASIS; content-addressed via Git-LFS
├── layer_02.gds
├── dose_map_01.png      # optional per-pixel dose modulation
├── drc_report.json      # output of mbm-drc, must be present + clean
└── compiled/            # cached firmware blobs, keyed by snapshot+recipe SHA
```

Recipes are versioned in Gitea. Edits go through a pull request with
mandatory review by a second process engineer (branch protection).
Dispatch is by Git commit SHA, never by branch name — production lots
always reference an immutable hash.

### 2.2 Lot model (Postgres)

```
lots
  lot_id UUID PRIMARY KEY
  customer_id UUID REFERENCES customers
  recipe_sha CHAR(40) NOT NULL  -- Git commit
  wafer_count INT
  deadline TIMESTAMPTZ
  state lot_state_enum  -- queued / dispatched / running / done / aborted
  dispatched_by user_id
  dispatched_at TIMESTAMPTZ
  snapshot_id UUID REFERENCES calibration_snapshots  -- calibration in effect
```

Per-wafer rows (`wafers`) hold start/end timestamps, yield, and a
pointer to the MinIO telemetry blob.

### 2.3 SECS/GEM integration

Industry-standard fab MES protocol (SEMI E5/E30/E37). Open
implementations:

- **secsgem** (Python, BSD-3) — pinned 0.3.0, used as the host driver.
- **OpenAS** — reference equipment driver for HSMS over TCP/IP.

The MES (typically Camstar, Critical Manufacturing, or open-source
FabMon) sends `S2F41` Host Command (e.g. `START_LOT`) → our adapter
translates to `POST /lots/{id}/dispatch` → recipe is fetched, validated,
compiled, sent to firmware. Status events (`S6F11` Event Report) are
emitted on lot start, wafer complete, lot complete, alarm.

The SECS/GEM adapter is a Rust service `mbm-secsgem` (≈ 2000 LOC)
that brokers between the binary HSMS wire format and the supervisory
REST API. It runs in its own systemd unit with an isolated NIC for fab
network compliance.

---

## 3. Operator GUI

### 3.1 Stack

- **Next.js 15** (App Router, RSC)
- **React 19**
- **Tailwind v4**
- **shadcn/ui** components
- **TanStack Query** for REST cache
- **native WebSocket** for tool status push (wrapped by a thin hook)
- **uPlot** for high-rate diagnostic plots (1 Mpts smoothly)
- **deck.gl** for the 10⁶-beam wafer map heatmap
- TypeScript 5.6 strict

Versions pinned to match niki-os. Renders on any cleanroom workstation
running Firefox ESR 128 or Chromium 129; no native install required.

### 3.2 Page set

| Route | Purpose | Real-time |
|---|---|---|
| `/` | Tool overview: state, current lot, alarms, vacuum, cryo, source health | yes (1 Hz WS) |
| `/lots` | Queue, dispatch, abort | yes |
| `/lots/[id]` | Per-wafer progress, exposure trace replay | yes |
| `/recipes` | Browse, diff, request edit (links to Gitea PR) | no |
| `/calibration` | Snapshot list, run procedure, promote/rollback | yes during run |
| `/diagnostics` | Custom plot builder over VictoriaMetrics | yes |
| `/manual` | Jog stage, manual blanker, abort — gated by hardware key | yes (10 Hz) |
| `/admin` | Users, roles, audit log, firmware version | no |

The 50-line tool-status page skeleton appears in §11.1.

### 3.3 Real-time channel

Supervisory plane runs an Axum (Rust) server exposing
`wss://tool/ws/status`. The server fans out a 1 Hz aggregated tool-state
struct (~4 kB JSON) and an event-driven alarm channel. Backpressure is
handled by dropping intermediate state frames (alarms never drop). Auth
is a short-lived JWT bound to the operator's Keycloak session.

### 3.4 Manual control safety

The `/manual` page is locked behind a physical YubiKey + a hardware
e-stop interlock on the workstation. Any manual command is logged to
the audit trail (`audit_log` table, append-only via Postgres trigger).
Stage jog speed is firmware-clamped; the GUI cannot exceed it.

---

## 4. Telemetry pipeline

### 4.1 Sources

| Source | Rate | Format | Sink |
|---|---:|---|---|
| Per-beam exposure events | 10⁶ × ~10 kHz aggregated | Cap'n Proto frames | Parquet rollup → MinIO |
| Thermal sensors (chuck + column) | 1 kHz × 100 ch | Prom remote write | VictoriaMetrics |
| Registration error (3-tier loop) | 10 kHz (level 0), 100 Hz (1), 1 Hz (2) | Prom remote write | VictoriaMetrics |
| Source emission | 1 kHz × 10⁶ tips, decimated to 1 Hz × subarray means | Prom remote write | VictoriaMetrics |
| Vacuum, cryo, ZMI sync | 10 Hz | Prom remote write | VictoriaMetrics |
| Stage trajectory | 1 kHz | Parquet | MinIO |

### 4.2 Ingest path

Firmware → `mbm-telemetry-collector` (Rust, ~3 kLOC) →
- numeric streams: VictoriaMetrics via `vmagent` (HA pair)
- event/blob streams: Apache Arrow → Parquet → MinIO, partitioned by
  `lot_id/wafer_id/`

Compression: VictoriaMetrics built-in (~10× on float64 telemetry);
Parquet zstd-3 (~5–8× on event traces). End-to-end: 100 GB/day raw →
~15 GB/day on disk.

### 4.3 Analytics surface

- **Grafana 11.2** for live dashboards (operator + process engineer views,
  pre-built JSON definitions in repo).
- **Apache Superset 4.0** for cross-lot yield analytics over a Trino
  federation that unions Postgres (lot metadata) with Parquet on MinIO
  (per-wafer traces).
- Jupyter-on-K8s for ad-hoc analysis; notebook server has read-only
  Postgres + MinIO + VictoriaMetrics tokens via Keycloak OIDC.

---

## 5. Process recipe server

### 5.1 Validation pipeline

A recipe must pass before dispatch is allowed:

1. **DRC** — `mbm-drc` (built on KLayout 0.29, pinned) checks GDS
   geometry against node-rule deck (`rules/50nm.drc` etc.). Output
   `drc_report.json` must show zero blocking violations.
2. **Dose validation** — total deposited energy, peak dose,
   integrated peak flux per mm² checked against
   `v4_wafer_thermal.md` limits (≤ 0.5 W/cm² peak).
3. **Stochastic placement budget check** — sum-of-squares against the
   `v4_INTEGRATION.md` σ_total table; reject if requested node <
   validated envelope for current snapshot's calibration quality.
4. **Throughput estimate** — feeds back to lot scheduler for deadline
   feasibility.

Steps 1–4 run in a sandboxed `mbm-validate` worker (containerised,
no network), produce a signed validation receipt stored alongside the
recipe in Gitea.

### 5.2 Compilation cache

Compiled firmware artefacts are keyed by
`SHA256(recipe_sha || snapshot_id || firmware_version)`. Hits return
in ms; misses run the compiler (≈ 1–5 min for a full reticle on a
dedicated 64-core compile node). Cache lives in MinIO under
`s3://mbm-compiled/`. Eviction: LRU over 30 days, except pinned
artefacts for in-flight lots.

The Python interface to the compiler is sketched in §11.3.

---

## 6. Authentication / multi-tenancy

### 6.1 Roles (Keycloak realm `mbm-tool`)

| Role | Permissions |
|---|---|
| `operator` | Dispatch queued lots, monitor, run daily calibration, abort |
| `process_engineer` | All operator + edit recipes (via Gitea PR), run/promote/rollback calibration snapshots, define alarm thresholds |
| `sysadmin` | Firmware updates, schema migrations, user management, vault access |
| `customer` | Read-only access to own lots, their telemetry summaries, status webhooks |
| `service` | M2M tokens for SECS/GEM, vmagent, compile workers |

### 6.2 Identity stack

- **Keycloak 26** as the SSO authority. OIDC for GUI, OAuth2
  client-credentials for service-to-service.
- **Hardware second factor** mandatory for `process_engineer` and
  `sysadmin` (YubiKey FIDO2).
- **HashiCorp Vault 1.18 OSS** (BSL-but-OSS for ≤1.14; pin to that or
  switch to OpenBao 2.0 if Hashicorp licensing concerns persist) holds
  Postgres creds, MinIO root keys, customer API webhook secrets,
  signing keys for recipe artefacts.
- Customer tenancy is row-level-security in Postgres: every customer-
  visible table has `customer_id`; RLS policies use the JWT claim.

---

## 7. Alarm + diagnostic system

### 7.1 Alarm classes

**Hard alarms** — trigger E-stop in firmware, supervisory only records
and notifies:

| Alarm | Source | Action |
|---|---|---|
| Coil quench (HTS bridge V > 1 mV) | column controller | E-stop, beam off, isolate quench heater |
| Vacuum leak (chamber > 10⁻⁴ Pa) | ion pump current jump | E-stop, close gate valves |
| Cryocooler trip | Sumitomo controller | E-stop, ramp-up timer to next cycle |
| ZMI sync loss > 1 ms | Zygo controller | E-stop, abort lot, mark wafer for re-expose |
| Cold-warm interface He leak | RGA partial pressure | E-stop, hot pad alert |

**Soft alarms** — supervisory-only, surfaced to operator and logged:

| Alarm | Detector | Threshold |
|---|---|---|
| Registration error trending up | EWMA over 10 min of 3-tier residual | > 1.5× snapshot baseline |
| Dose deviation | per-tile dose vs setpoint | > 2% over 100 wafers |
| Source emission drift | per-tip current EWMA | > 5% from calibration |
| Beam outage > N tips | per-tile dead-beam map | tile-N dependent |

### 7.2 Detection engine

A Rust service `mbm-alarm` subscribes to VictoriaMetrics via PromQL
queries on a 1 s tick. Rules live in `alarms/*.yaml`, version-
controlled, peer-reviewed. Notification fan-out is via
**Alertmanager 0.28** → email, Slack webhook, PagerDuty.

### 7.3 Diagnostic playback

Every wafer's full telemetry is replayable. The diagnostic GUI loads
the Parquet trace from MinIO, scrubs it through `uPlot` (timeline) and
`deck.gl` (per-beam heatmap), and overlays the registration loop's
internal state. Engineers can synchronise N wafers side-by-side to
correlate a yield event with a calibration drift. Replay is read-only,
sandboxed (no firmware contact).

---

## 8. Reproducible build / deploy

### 8.1 Build

- **Nix flakes** as the source of truth. `flake.nix` pins nixpkgs,
  Rust toolchain (1.83), Node 22.11, Python 3.13, Postgres 18,
  VictoriaMetrics 1.110, MinIO RELEASE.2025-10-15.
- Per-service Docker images built via `dockerTools.buildLayeredImage`
  (Nix → OCI), so images are bit-reproducible.
- Container registry: self-hosted **Harbor 2.12** with Cosign image
  signing.

### 8.2 Deploy

- **Kubernetes 1.31** (K3s for the tool itself, full upstream for fab
  data centre).
- **FluxCD 2.4** for GitOps; the cluster state is a Git repo
  (`mbm-tool-cluster`) and Flux reconciles. Promotions go through
  Renovate-generated PRs.
- **Sealed Secrets** (Bitnami) for in-repo encrypted secrets;
  unsealed inside the cluster via the Vault-CSI driver.

### 8.3 HIL / integration test

A Hardware-in-the-Loop test harness `mbm-hil` simulates the firmware
boundary: it speaks the same Cap'n Proto over a UDS socket, replays
canned telemetry, accepts compiled recipe blobs and asserts byte-exact
match against fixtures. CI (GitHub Actions, self-hosted runners on the
build farm) runs the full supervisory stack against `mbm-hil` on every
PR. End-to-end test wall-time budget: 20 min per PR.

---

## 9. External integration

### 9.1 MES

SECS/GEM as in §2.3. The host also publishes:

- **SEMI E142** XML schema for lot-by-lot history.
- **EDA Freeze 3** trace data feed (optional, for fab-wide trace
  consumers).

### 9.2 Customer-facing REST API

OpenAPI 3.1 spec auto-generated from Rust types via `utoipa`. Base:
`https://tool.example.com/api/v1/`.

| Endpoint | Method | Purpose |
|---|---|---|
| `/lots` | GET | List own lots (RLS-filtered) |
| `/lots/{id}` | GET | Status + per-wafer summary |
| `/lots/{id}/telemetry` | GET | Pre-signed MinIO URL for Parquet trace |
| `/lots/{id}/webhook` | POST | Register status webhook |
| `/health` | GET | Liveness for monitoring |

Rate-limited (Traefik middleware), all responses signed with the tool's
identity key so customers can verify provenance.

### 9.3 Alert integrations

- PagerDuty for hard alarms (24/7 on-call).
- Slack/Mattermost webhook for soft alarms.
- Email digest for daily yield reports.
- Optional: Microsoft Teams via incoming-webhook.

---

## 10. Open-source release structure

```
multibeam-ebl-tool-os/
├── LICENSE                 # MIT
├── LICENSE-SPEC            # CC BY 4.0
├── flake.nix
├── README.md
├── docs/                   # MkDocs Material site
│   ├── operator/
│   ├── process-engineer/
│   ├── sysadmin/
│   └── architecture/       # this spec, rendered
├── services/
│   ├── mbm-supervisor/     # Rust + Axum (REST + WS)
│   ├── mbm-telemetry/      # Rust ingest
│   ├── mbm-secsgem/        # Rust + secsgem-py FFI
│   ├── mbm-alarm/          # Rust + PromQL client
│   ├── mbm-compiler/       # Python recipe → firmware
│   ├── mbm-drc/            # KLayout wrapper
│   └── mbm-hil/            # HIL simulator
├── gui/                    # Next.js 15 monorepo
├── db/
│   ├── migrations/         # sqlx migrations
│   └── schema/             # source-of-truth SQL
├── recipes/                # example recipes incl. calibration
├── alarms/                 # rule YAMLs
├── deploy/
│   ├── k8s/                # Flux manifests
│   └── nix/                # NixOS modules for bare-metal
├── tests/
│   ├── hil/                # HIL integration suite
│   └── property/           # proptest / hypothesis
└── .github/workflows/      # CI pipelines
```

Branches: `main` (stable, signed tags `v0.1.0` …), `next` (integration),
short-lived feature branches. Merge gating: CI green + 2 reviews +
HIL pass. Releases are SemVer; firmware compat matrix in
`docs/compat.md`.

---

## 11. Buildable code skeletons

### 11.1 Next.js tool-status page (≤ 50 LOC)

```tsx
// gui/app/page.tsx
"use client";
import { useEffect, useState } from "react";
import useSWR from "swr";
import { Card } from "@/components/ui/card";

type Status = {
  state: "idle" | "exposing" | "calibrating" | "alarm";
  lotId?: string;
  waferIdx?: number;
  vacuumPa: number;
  cryoK: number;
  sourceUa: number;
  regErrNm: number;
  alarms: { level: "hard" | "soft"; msg: string }[];
};

export default function Home() {
  const { data: init } = useSWR<Status>("/api/v1/status", (u) =>
    fetch(u).then((r) => r.json())
  );
  const [s, setS] = useState<Status | undefined>(init);

  useEffect(() => {
    const ws = new WebSocket(`wss://${location.host}/ws/status`);
    ws.onmessage = (e) => setS(JSON.parse(e.data));
    return () => ws.close();
  }, []);
  if (!s) return <div className="p-8">connecting…</div>;

  return (
    <main className="grid grid-cols-3 gap-4 p-8">
      <Card className="col-span-3 text-2xl">
        State: <b>{s.state}</b>{s.lotId && ` — lot ${s.lotId} wafer ${s.waferIdx}`}
      </Card>
      <Card>Vacuum {s.vacuumPa.toExponential(1)} Pa</Card>
      <Card>Cryo {s.cryoK.toFixed(1)} K</Card>
      <Card>Source Σ {s.sourceUa.toFixed(2)} µA</Card>
      <Card className="col-span-3">Reg err RMS {s.regErrNm.toFixed(2)} nm</Card>
      {s.alarms.map((a, i) => (
        <Card
          key={i}
          className={`col-span-3 ${a.level === "hard" ? "bg-red-700" : "bg-amber-500"} text-white`}
        >
          {a.level.toUpperCase()}: {a.msg}
        </Card>
      ))}
    </main>
  );
}
```

### 11.2 PostgreSQL 18 calibration schema (≤ 50 LOC)

```sql
-- db/schema/010_calibration.sql
CREATE TYPE snapshot_state AS ENUM ('pending','active','retired','rejected');

CREATE TABLE calibration_snapshots (
  snapshot_id   UUID PRIMARY KEY DEFAULT uuidv7(),
  taken_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  taken_by      UUID        NOT NULL REFERENCES users(user_id),
  procedure     TEXT        NOT NULL,            -- recipe SHA of cal proc
  firmware_ver  TEXT        NOT NULL,
  state         snapshot_state NOT NULL DEFAULT 'pending',
  notes         TEXT,
  signed_by     TEXT,                            -- cosign identity
  acceptance    JSONB       NOT NULL DEFAULT '{}'::jsonb
);
CREATE UNIQUE INDEX one_active ON calibration_snapshots(state)
  WHERE state = 'active';

CREATE TABLE beam_calibration (
  snapshot_id   UUID NOT NULL REFERENCES calibration_snapshots ON DELETE CASCADE,
  column_id     SMALLINT NOT NULL,    -- 0..99 (10x10 columns)
  tile_id       SMALLINT NOT NULL,    -- 0..15 (16 tiles/col)
  beam_id       INT      NOT NULL,    -- 0..1023 within tile
  defl_x_off    SMALLINT NOT NULL,    -- int16 DAC bias
  defl_y_off    SMALLINT NOT NULL,
  blanker_delay SMALLINT NOT NULL,    -- ps, signed
  emission_a    REAL NOT NULL,        -- I-V curve fit coeffs
  emission_b    REAL NOT NULL,
  emission_c    REAL NOT NULL,
  dead          BOOLEAN NOT NULL DEFAULT false,
  PRIMARY KEY (snapshot_id, column_id, tile_id, beam_id)
) PARTITION BY HASH (snapshot_id);

CREATE TABLE tile_thermal (
  snapshot_id   UUID NOT NULL REFERENCES calibration_snapshots ON DELETE CASCADE,
  column_id     SMALLINT NOT NULL,
  tile_id       SMALLINT NOT NULL,
  k_xx REAL, k_xy REAL, k_yy REAL,   -- 2x2 thermal coupling
  PRIMARY KEY (snapshot_id, column_id, tile_id)
);

CREATE TABLE column_drift (
  snapshot_id   UUID NOT NULL REFERENCES calibration_snapshots ON DELETE CASCADE,
  column_id     SMALLINT NOT NULL,
  drift_nm_per_h REAL NOT NULL,
  PRIMARY KEY (snapshot_id, column_id)
);

CREATE TABLE active_snapshot (
  singleton BOOLEAN PRIMARY KEY DEFAULT TRUE CHECK (singleton),
  snapshot_id UUID NOT NULL REFERENCES calibration_snapshots
);
```

### 11.3 Python recipe-to-firmware compiler interface (≤ 50 LOC)

```python
# services/mbm-compiler/mbm_compiler/api.py
from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path
import json, subprocess, boto3

@dataclass(frozen=True)
class CompileRequest:
    recipe_sha: str          # 40-char hex
    snapshot_id: str         # uuid
    firmware_ver: str        # semver
    target_node_nm: int

    @property
    def cache_key(self) -> str:
        h = sha256()
        for f in (self.recipe_sha, self.snapshot_id, self.firmware_ver,
                  str(self.target_node_nm)):
            h.update(f.encode()); h.update(b"\0")
        return h.hexdigest()

class Compiler:
    def __init__(self, s3, bucket="mbm-compiled"):
        self.s3, self.bucket = s3, bucket

    def compile(self, req: CompileRequest) -> str:
        """Returns the s3 URI of the compiled firmware blob."""
        key = f"{req.cache_key}/firmware.bin"
        if self._exists(key):
            return f"s3://{self.bucket}/{key}"
        with TemporaryDirectory() as tmp:
            gds = self._fetch_recipe(req.recipe_sha, tmp)
            cal = self._fetch_snapshot(req.snapshot_id, tmp)
            out = Path(tmp) / "firmware.bin"
            subprocess.run(
                ["mbm-compile-core",
                 "--gds", gds, "--cal", cal,
                 "--node", str(req.target_node_nm),
                 "--firmware-ver", req.firmware_ver,
                 "--out", str(out)],
                check=True, timeout=600,
            )
            self.s3.upload_file(str(out), self.bucket, key)
            manifest = {"req": req.__dict__, "size": out.stat().st_size}
            self.s3.put_object(Bucket=self.bucket,
                               Key=f"{req.cache_key}/manifest.json",
                               Body=json.dumps(manifest).encode())
        return f"s3://{self.bucket}/{key}"

    def _exists(self, key):
        try: self.s3.head_object(Bucket=self.bucket, Key=key); return True
        except self.s3.exceptions.ClientError: return False
```

---

## 12. Open questions for v5.1+

1. **Regulatory compliance for biomedical-grade fabrication.** Tools
   writing masks for medical-device ASICs (FDA 21 CFR Part 11) need
   tamper-evident audit logs, electronic signatures with non-repudiation,
   and validated change control. Postgres `audit_log` with WORM
   replication to a write-once tier (S3 Object Lock in compliance mode)
   is a start; full Part 11 + ISO 13485 needs a process layer the
   software can support but cannot itself satisfy. Open: certified
   identity provider integration (smart-card PIV/CAC), validated build
   chain (CSA Star or equivalent).

2. **Multi-tool farm orchestration.** When a fab runs 4–10 v4 tools,
   the supervisory plane must coordinate load balancing, calibration
   sharing where snapshots are tool-portable (they mostly aren't —
   coil offsets are per-coil), spare-tool failover mid-lot, and
   cross-tool yield analytics. Likely add an `mbm-fleet` service on
   top of single-tool supervisors with a CRDT-backed state model.

3. **Customer-managed encryption (BYOK).** Defence and biomedical
   customers will want recipe IP encrypted at rest with their own KMS
   keys (envelope encryption against AWS KMS / GCP KMS / on-prem HSM).
   Today everything is encrypted with tool-side keys in Vault.

4. **Calibration-quality scoring as a first-class metric.** Today a
   snapshot is either accepted or rejected. A continuous quality score
   (e.g. σ_total achievable on a reference recipe) would let the
   scheduler downgrade nodes when calibration is stale, instead of
   refusing the lot. Requires a calibration-driven physics surrogate.

5. **Federated learning across tools/fabs for drift modelling.**
   Drift signatures correlate across tools of the same vintage. A
   federated update over differential-privacy-protected drift traces
   could give each tool an early-warning model without leaking customer
   process data. Conservative move: ship as opt-in.

6. **Real-time MES write-back.** Today MES → tool is supervisory-only.
   A push of yield/throughput back to MES at sub-second cadence (to
   close the SPC loop) needs a higher-rate variant of S6F11 or a custom
   ECID stream. Negotiate per-fab.

7. **Long-term archive format stability.** A 10-year-old Parquet
   file should still be readable on Niki 4.0. Mitigation: pin Arrow
   format version per snapshot, hold a reference reader binary in MinIO
   alongside the data, document a migration cadence in the spec.

8. **Open hardware for the operator workstation.** The cleanroom
   workstation today is a generic Dell + Firefox. A reference open
   workstation spec (RISC-V SBC + Wayland + minimal browser engine)
   would close the last proprietary gap and align with the recursive-
   bootstrap-compute thesis underneath this whole stack.
