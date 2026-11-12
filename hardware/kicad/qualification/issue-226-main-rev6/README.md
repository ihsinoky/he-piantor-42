# Issue #226 — Main Rev.6 vertex chamfers (proposed)

Rev.5 plus three equal-leg 4 mm chamfers. All footprints, tracks, vias, nets,
mounts and project rules are inherited. The only copper edit is the In1.Cu GND
plane setback at the corners. The 0.55 mm design setback exceeds the 0.5 mm
requirement. This package is a PO review candidate; no manufacturing release.

- `inspection/final/main.kicad_pcb` and `.kicad_pro`: final board/rules.
- `geometry-plan.json`, `rev5-diff-and-clearance.json`: measured angles, legs,
  exact outline subset, per-edge copper/hole distances and parsed design diff.
- `outline-comparison.png`: Rev.5 dashed orange / Rev.6 solid teal, full board
  and three enlarged corners; dotted circles show preserved Ø5 mm mount supports.
- `inspection/final/{drc,connectivity,assessment}.json`: native DRC and physical
  four-layer union-find (same predicates as Rev.5, no net-name unions).
- `inspection/final/audit/via-pad/`: complete rerun of 130 × 232 via/pad pairs.
- `schematic/erc-final.json`: fresh native ERC on byte-identical Rev.5 schematic.
- `power-*`, `ground-*`, `resistance-summary.json`: fresh Rev.6 extraction using
  Rev.5 methods, identical material/corner/load assumptions, hash-linked comparison.
- `manufacturing/`: regenerated fabrication ZIP, BOM, CPL, absolute Gerber-frame
  CPL, native positions, paste and drill files. `cam-check.json` independently
  reads all manufacturing geometry; `cpl-frame-check.json` rederives translation
  from PCB/55 placements and verifies it against native positions and Edge.Cuts.
- `processes/`: final calls and exit status only. Failed implementation trials
  remain under `.issue226-runtime/debug-runs/`, outside the qualified package.
- `manifest.json` and `verify.py`: offline acceptance and input/output hashes.
- [Implementation report](../../../../.issue226-runtime/REPORT.md).

The three corner plane cuts are made by half-plane clipping both the native zone
boundary and its inherited fill. Preserving the original fractured hole bridges
avoids wholesale plane regeneration. On sloping filled boundaries, new endpoints
must land on KiCad's 1 nm grid; the independent diff separately reports the raw
remote sliver area and requires it to lie within a 2 nm envelope of the original
boundary (Rev.5's numeric tolerance, 500 times finer than Gerber precision).
No routing edits or zone rule edits are permitted. Actual edge distances are
checked without subtracting this diff tolerance and must be >=0.5 mm.

Reproduce from the repository root, using `bash .../env.sh <script> [args]`:
`build.py` → `native-checks.py` → `check-geometry.py` → `connectivity.py final` →
`assess.py` → `run-audit.py` → `extract-power.py final` / `extract-ground.py final`
→ `summarize-resistance.py` / `verify-ground-model.py` → `power-budget.py` /
`power-impact.py` → `assembly.py` → `export-final.py` → `cam-source.py` →
`check-cam.py` → `gerber-frame-cpl.py`. Use `common.py <name> <command ...>` to
record each external call. `/usr/bin/python3 plot-outline.py` generates the PNG.
Use a fresh isolated output directory for reruns: process/export overwrites are
intentionally refused. Run `python3 .../verify.py` for offline acceptance.

The original Rev.5 footprint libraries are read-only dependencies referenced by
`fp-lib-table`. The schematic and net XML are inherited unchanged, with fresh
ERC. BOM choices and the original CPL datum are retained; the Gerber translation
is derived again, not copied. J4/Fly polarity measurement and existing first-power,
assembly and supplier acceptance gates from D-035 still apply.
