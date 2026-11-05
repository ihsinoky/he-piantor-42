# Issue #157 Stage 1 evidence

Read-only feasibility / interface proposal. No PCB, schematic, route, project,
Gerber, drill or assembly input is created or changed here. `placement.svg` is
a review drawing, not a board source. The proposed interface is not adopted.

The [report](../../../../docs/issue-157-main-dual-wing-stage1.md) contains the
recommended design, unresolved gates and D-017 extension draft.

| File | Purpose |
| --- | --- |
| `instructions.md`, `issue.json`, `pr156-input.json`, `start.json` | Full user runtime instructions, retrieved issue and merged PR input, base / deadline |
| `inputs.json`, `sources.json` | Repository source hashes; primary datasheet URLs, versions and downloaded PDF hashes. Third-party PDFs stay in runtime |
| `analyze.py`, `geometry.json`, `placement.svg` | Actual #155 PCB parsed read-only; three placement cases and exact pad template; provisional service envelopes are labeled |
| `signal-inventory.json` | Actual GH14 pinout / MCU and power pads; separate proposed second enable |
| `native-check.py`, `native-check.json` | KiCad read-only check of actual pads, NPTHs, outline and reservation polygons; no board insertion or save |
| `dual-wing-dc.csv`, `power-model.json` | 768 cases: 16 saved #141 Wing cases, component/envelope and rounded allowance loads, 1/2 Wings, 30/50mΩ contacts, 6/1 returns, 0/0.25/0.5Ω Main sensitivity |
| `main-resistance.py`, `main-resistance.json` | Verbatim #141 model reused on actual existing Main rails, native layer membership; 8 resistance cases and 64 old-J2 power sensitivities |
| `verify.py`, `analysis-runs.json`, `verification.json` | Repeatable analyses, run times, preservation, physics identities, local document links |
| `protected-start.json.gz` | SHA256 of all 10,678 pre-existing non-runtime files, including unrelated untracked outputs. No existing file is modified |
| `draft-pr-body.md`, `publication.json` | Prepared review text and actual push / Draft PR outcome |
| `manifest.json` | SHA256 of final added artifacts except itself; publication attempt records are separate from engineering conclusions |

Reproduce from the repository root with Python 3:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-157-main-dual-wing-stage1/verify.py
```

The runner reads the already installed KiCad 9 and NumPy/Shapely from
`.issue129-runtime/`, and writes temporary files only into
`.issue157-runtime/`. It does not bootstrap/install/download dependencies.
`analyze.py` alone is stdlib-only. `native-check.py` and `main-resistance.py`
need the KiCad Python bindings; the latter also needs the existing geometry
environment. The runtime git directory is necessary for the existing-worktree
check; it is local metadata and is not committed. On another checkout, perform
the equivalent clean-tree / base comparison with that checkout's git metadata.

`verify.py` rewrites only this issue's new analysis outputs and verification
records. Refresh `manifest.json` after a deliberate regeneration. Power results
are supplementary estimates, not manufactured worst-case bounds: current,
contact sharing, foil/barrel, Main GND, inrush and actual source voltage remain
subject to the report's limits. In the Main model, the test injection is 1 A
only to obtain ohms; it is not a load-current requirement.

The timebox uses host UTC (start 2026-11-05 20:47:22, deadline 22:47:22).
The PO task date is 2026-11-06. No order, charge or merge is performed.

Publication `stdout`/`stderr` are raw command output, including GitHub's remote
trailing spaces. Whitespace lint checks authored content and JSON; it excludes
only those raw stdout/stderr records rather than altering the evidence.
