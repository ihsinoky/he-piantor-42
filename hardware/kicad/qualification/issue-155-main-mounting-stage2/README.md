# Issue 155 evidence

The reviewed board is **inspection/final/main.kicad_pcb**, with the corresponding original input-side `main.kicad_pro`. See [the report](../../../../docs/issue-155-main-mounting-stage2.md). This is a qualified routing/manufacturing review candidate, not an order release.

## Artifact map

- `issue.json`, `instructions.md`, `continuation-instructions.md`, `start.json`: scope, original timebox and attempt limits.
- `inputs.json`, `input-hashes.json`, `runtime-revalidation.json`: baseline and pinned KRT identities.
- `inputs/revised`: #121 qualified board plus four holes and keepouts. This still has the three directly conflicting old segments; do not fabricate it.
- `inputs/local`, `runs/local`, `inspection/local`: single local attempt. Connectivity/material checks passed, but 68 retained segments were not covered: local scope rejected.
- `global-scope.json`, `inputs/global`, `runs/global`, `inspection/global`: single scoped full reroute. Three .20mm original seed segments retained; 537 .10mm tracks and 66 vias removed before routing. Independent metrics all zero.
- `reservation-quantization-guard.json`, `inputs/final`, `runs/final`: deterministic 4nm outward guard on only four keepout polygons to ensure the ideal 5mm disk is fully reserved despite integer coordinate rounding. No extra routing and no copper edits.
- `inspection/final`: independent refill with original project, DRC, four-layer actual copper graph for all 37 nets, exact nonroute AST/retained-copper coverage and physical readback. Four metrics all zero.
- `mechanical-readback.json`, `support-screening.json`: final holes/reservations and limited planar support screening; physical/3D/load tests explicitly open.
- `pofv-reclassification.json`, `pofv-sites.csv`: rescan of all 66 vias; 25 candidates, including 23 mounted-pad drill overlaps. D-022 retained.
- `assembly-review.json`: original BOM ledger match, J1 all-terminal Economic intent and explicit CPL origin transform.
- `manufacturing/gerber`: four copper, two mask, two silk, outline, separated PTH/NPTH drill. `main-stage2-fabrication-review.zip` contains these **11 fabrication files only**, excluding gbrjob.
- `manufacturing/paste`: faithful original paste shapes, including four J1 shell strokes on each side and four bare TP circles on top. Manufacturer process/stencil review remains required.
- `manufacturing/BOM.csv`, `CPL.csv`: 45 assembled parts. Excludes four bare TP and four mounting holes. CPL X=KiCadX−76, Y=122−KiCadY, all top. Gerber/drill/native-pos use absolute origin. Library-specific rotation/polarity preview still required.
- `cam-native-zones.json`, `cam-check.json`, `export-provenance.json`: independent parsed CAM comparison. Gerbonara cannot directly parse inline KiCad G85; four slot commands are parsed strictly with active tool diameter, leaving export bytes unchanged. Round-only commands are passed to Gerbonara in memory. G90-after-header warnings are recorded and coordinates match.
- `manufacturing/cam-review.png`: offline CAM rendering, visually inspected. `verification.json`: acceptance/source/runtime preservation audit. `manifest.json`: file hashes. `publication.json`: commit/push/Draft PR results.

## Reproduction and runtime

All scripts run from the repository root. `common.py` sets KiCad, geometry and cache paths; all temporary writes are under `.issue155-runtime/`. The existing `.issue129-runtime/` KiCad 9.0.9, Python venv/geometry packages and `.issue147-runtime/viewer-venv` are read-only dependency sources. KRT v0.23.8 is copied under `.issue155-runtime/KiCadRoutingTools` and checked against #131's 2,055-source manifest and the pinned Rust binary hash. Runtime binaries/caches are not committed.

Do not blindly replay authoring/routing into this evidence tree: creation guards intentionally prevent overwriting frozen inputs and route attempts. For a fresh reproduction, provision the exact dependencies and replay in an isolated checkout/evidence tree. The authoring/routing sequence is `prepare.py`, `gate.py`, `route-local.py`, `inspect-board.py local`, `prepare-global.py`, `route-global.py`, `inspect-board.py global`, `finalize-reservations.py`, `inspect-board.py final`. The local result is intentionally rejected, not silently repaired. Only one local and one global routing invocation are authorized by this run.

Recorded standalone inspection example (does not route):

```sh
python3 hardware/kicad/qualification/issue-155-main-mounting-stage2/common.py unique-review-name /usr/bin/python3 hardware/kicad/qualification/issue-155-main-mounting-stage2/verify-final.py
```

Use a new process name so earlier logs cannot be overwritten. `review-final.py` reads the qualified final board, writes the mechanical/POFV/assembly review and BOM/CPL; `check-support.py` performs planar screening. `export-final.py` exports exact refilled bytes and refuses an existing export runtime directory. `cam-source.py` reads native zone/paste shape coordinates; `check-cam.py` parses and compares exported geometry, drills, masks, paste and CPL and packages the fabrication-only ZIP. `render-cam.py` produces the contact sheet from exported files. CAM scripts use the existing viewer Python.

`processes/` preserves actual argv, stdout/stderr and return status. Inherited `local-connectivity-geometry` has launch only because runtime restart interrupted it; exit status is unknown. The resumed geometry inspection completed separately. The initial native connectivity API call, global input API removal, refill width readback, and inspector/parser assumption failures are retained. Fixing inspection/serialization code did not add routing attempts or relax acceptance. The final method sources are committed alongside the successful records.

`verify-final.py` depends on the original runtime protection snapshot to compare all pre-existing tracked and non-runtime untracked files. It checks D-023 append-only, strict reservation radii, exact source-to-final nonroute additions, unchanged routed copper across finishing, original .20mm coverage, all 37 nets, identical inherited printing violations, all-via geometry equality and source/runtime preservation. `manifest.json` excludes itself, Git metadata, Python caches and transient KiCad `.kicad_prl` files.

No orders, payments, manufacturer contacts or merge were performed. Real mechanical loads, fastening/3D access, underside solder clearance, USB/noise/ADC behavior and manufacturer process acceptance remain open as documented in the report.
