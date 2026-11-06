# Issue169 evidence — stopped after two whole-board attempts

Issue incomplete; manufacturing release, final PCBA quotation, order, billing and merge are not approved or performed. Read [the report](../../../../docs/issue-169-main-dual-wing-followup.md) and [status.json](status.json) first.

## Candidates and acceptance

- `inputs/seed-a/`, `runs/seed-a/`, `inspection/seed-a/`: first input, raw output and independently refilled inspection. All 44 nets, four independent metrics zero. Uses 0805 output capacitors.
- `inputs/final/`, `runs/final/`, `inspection/final/`: **seed-a only**, after an explicitly declared paste-only correction. No copper edit/reroute. Full 44-net/four-zero reinspection. The directory name is inherited workflow terminology, not acceptance of the selected seed-b components.
- `inputs/seed-b/`, `runs/seed-b/`, `inspection/seed-b/`: independent second input (from seed-a input, never its routed output), 1210 output caps, changed power escape seed and inside_out/backward routing. FAIL: direct observations 2 opens / 2 wrong-net contacts / 4 material violations / 7 retained-route changes. No further routing is authorized under this issue.
- `design-seed-a/`: first component contract and a semantically equivalent native schematic re-export archived before switching to B. Original circuit-check records retain the exact hashes of their earlier exports; the archived re-export has fresh UUIDs and is not asserted byte-identical.
- Root `schematic/`, `logical-contract.json`, `circuit-source.py`, `main-bom.csv`: **seed-b selected parts**. Native schematic netlist and all 245 logical pins independently checked against seed-b.

## Key records

| Record | Purpose |
| --- | --- |
| `instructions-169.md`, `issue.json`, `start.json` | Full instructions, fetched issue, base SHA and 4h deadline |
| `routing-scope.json`, `seed-b-preparation.json`, `preflight-*.json` | Two-run bounds, source placements, source DRC including B's failed preflight |
| `processes/seed-*-effective/`, `runs/*/effective.json` | Official resolver readback before routing; no condition relaxation |
| `processes/seed-*-krt-route/` | The only two actual native routing runs, raw stdout/stderr/argv/timeouts |
| `inspection/*/assessment.json` | Acceptance; conditional metrics remain null if KiCad reports opens |
| `inspection/*/connectivity.json`, `transfer-diff.json`, `drc.json` | Direct observed metrics and all 44 nets; no net-name-only connectivity |
| `paste-correction.json` | Source/output-mirrored 36-aperture correction of A; no copper edits |
| `component-selection.json`, `sources/`, `sources.json` | Exact MPN selection, effective-C/ESR screening, primary authored PDFs and failed HTTP captures |
| `power-extraction-*.json`, `ground-extraction-*.json` | Per-candidate actual copper DC extraction; final GND model uses PGND only |
| `ground-extraction-*-equal-IC-contacts.json` | Superseded diagnostic boundary condition, not used in current budget |
| `ground-model-verification.json`, `resistance-summary.json`, `power-budget.json` | Analytic/numerical checks, resistance and conditional supply budget |
| `connector-current-sensitivity.csv` | 270 design/stress/efficiency/input/rail cases; no efficiency guarantee |
| `pofv-reclassification-seed-b.json`, `pofv-sites-seed-b.csv` | Failed B diagnostic inventory: 127 vias / 40 candidates |
| `pofv-reclassification-seed-a.json`, `pofv-sites-seed-a.csv` | A inventory: 110 vias / 28 candidates |
| `manufacturing-seed-a-review/` | A-only CAM/BOM/CPL and fabrication review ZIP; do not combine with root B BOM |
| `cam-check.json`, `export-provenance.json` | Independent Gerbonara/native geometry match and A export provenance |
| `pcba-update-status.json` | Final B manufacturing/quotation gate not passed; no final amount fabricated |
| `runtime-check.json`, `verification.json`, `manifest.json` | Runtime source integrity, evidence integrity and artifact hashes |
| `publication.json`, `draft-pr-body.md`, `pr-title.txt` | Commit/push/Draft PR outcome and ready-to-submit metadata |

## Execution and limits

Runtime is `.issue169-runtime/`; metadata Git is `.issue169-runtime/git` at the same repository working directory. Ordinary `.git` is preserved. Existing KiCad 9.0.9, KRT and Python dependencies are read from `.issue129-runtime/`, `.issue155-runtime/` and the existing CAM environment `.issue147-runtime/viewer-venv/`. Added Triangle 20250106 is in `.issue169-runtime/python/`; its package version and numerical benchmark are recorded. No dependency installation is committed.

The audited launcher is `.issue169-runtime/run.py NAME PROGRAM ARGS…`; implementation lives in `common.py`. Native tools receive the pinned KiCad/geometry environment, isolated XDG/TMPDIR and process-group timeouts. Every recorded command has `launch.json`, `stdout`, `stderr`, and `record.json`.

**Do not rerun routing.** Two real runs are spent even though B's source preflight failed. `route-before-preflight-guard.py` preserves the runner used for both runs. `route.py` now independently rejects failed input DRC and an exhausted budget; `processes/guard-budget-test/` proves rejection before entering the native router. Fixing the wrapper does not create a third attempt. The failed shell/assertion sequence and all API/preparation/CAM parser failures are kept as failures, not edited to success.

Representative read-only/evidence checks (use fresh process names to preserve existing logs):

```sh
python3 .issue169-runtime/run.py NAME /usr/bin/python3 hardware/kicad/qualification/issue-169-main-dual-wing-followup/verify.py

git --git-dir=.issue169-runtime/git --work-tree=. log -3 --oneline
```

`verify.py` checks evidence consistency. Its pass does not qualify B. Failed B has no final CAM and no confirmed PCBA quotation. D-019 relaxation is not justified by this record; a newly authorized finite scope is needed for further layout/routing, alongside disposition of the unresolved supply/manufacturing gates.
