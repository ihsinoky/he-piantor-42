# Project Plan: HE Piantor 42 JITX Challenger Backend

## Scope and authority

EDA-002B establishes only a reproducible JITX project and a machine-readable
parity contract. It does not implement, place, route, or make authoritative an
M1 JITX board. The frozen electrical authority remains
`../tscircuit/src/evaluation/m1-four-key.tsx`, verified by
`../tscircuit/scripts/verify-m1-electrical.tsx`.

## Data sources

| Source | Approved use |
| --- | --- |
| `../tscircuit/src/evaluation/m1-four-key.tsx` | Frozen M1 component, net, connectivity, geometry, and board data |
| `../tscircuit/scripts/verify-m1-electrical.tsx` | Independently asserted endpoint and critical-footprint requirements |
| `../sensor-test/design.md` | Project-owned M1 requirements and design-data gaps |
| `../sensor-test/pinmap.csv` | Project-owned RP2040 logical assignments |

`../layout/**` is GPL/QMK-derived and is explicitly out of scope. No component
data or geometry is sourced from it.

## Bootstrap task

### [bootstrap-01] Canonical JITX project

- **Type:** project bootstrap
- **Description:** Scaffold the CLI-owned project layout, pin Python `jitx`
  4.4.3, and retain only source/configuration files needed to repeat the
  authenticated Codespaces bootstrap build.
- **Verification:** `jitx build he_piantor_42_jitx.main.HePiantor42Bootstrap`
- **Status:** accepted

### [parity-01] M1 parity contract

- **Type:** contract
- **Dependencies:** bootstrap-01
- **Description:** Freeze the backend-neutral requirements a future JITX
  implementation must reproduce from the approved project-owned sources.
- **Verification:** `python -m json.tool parity/m1-parity-contract.json`
- **Status:** accepted

## Deferred work

Full M1 JITX electrical parity is the next increment after this bootstrap.
Board placement, routing, DRC, manufacturing artifacts, D-014 changes, and
EVT-002 are not part of EDA-002B.

## Task complete: EDA-002B bootstrap and parity contract

**What was built:** Canonical `hardware/jitx/` CLI project with
`he_piantor_42_jitx.main.HePiantor42Bootstrap` and
`parity/m1-parity-contract.json`.

**Build:** `status: ok` (via
`jitx build he_piantor_42_jitx.main.HePiantor42Bootstrap`)

**Primary source:** JITX CLI scaffold for the bootstrap package; frozen M1
sources listed in the Data Sources table for the parity contract.

**Secondary references:** `../sensor-test/design.md` and
`../sensor-test/pinmap.csv`.

**Footprint source:** not applicable: no M1 footprint or layout was implemented.

**Checks run:**
- `ruff check`: clean
- `ruff format --check`: clean
- `pyright`: not available; not installed in the project environment
- Grep gates (`python scripts/grep_gates.py he_piantor_42_jitx`): hard-fail 0
  hits, review-required 0 hits
- Parity JSON: `python -m json.tool parity/m1-parity-contract.json` passed

**Interface notes:**
- Ports exposed: bootstrap-only seed circuit; no M1 interface is exposed.
- Power requirements: no M1 power tree is implemented.
- Constraints needed at top level: deferred to the M1 parity increment.

**JITX code review (self):** clean
- CRITICAL: 0 — no string-keyed models, reflection, parallel scene graphs,
  framework-boundary bypasses, or dynamic classes in
  `he_piantor_42_jitx/`.
- WARNING: 0
- NOTE: 0

**Outside-voice review (codex):** not applicable: complete-board, task class
not in trigger list.

**Verdict (self):** ready-for-review

**Open issues / deferred:** Full M1 electrical parity, placement, routing, DRC,
and EVT-002 remain deferred.

**Verdict (acceptance):** accept
**Notes:** EDA-002B intentionally supplies a reproducible challenger bootstrap,
not an M1 board implementation.
