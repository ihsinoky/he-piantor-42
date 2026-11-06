# Issue #182 Matrix Rev.3 evidence

Qualified deliverable: `board/m1-matrix18.kicad_pcb` and its frozen project.
Read [the report](../../../../docs/issue-182-matrix-rev3.md) and
[manufacturing/FABRICATION.md](manufacturing/FABRICATION.md) first.

- `verification.json`: final qualification, dimensions and manufacturing summary.
- `inspection/final/`: independent all-net graph, KiCad DRC, transfer and width
  audits, native/analytic all-via pad audit. Every acceptance condition passes.
- `all-vias.csv`: all 158 vias, nearest pad and signed annulus-to-pad gap.
- `design-preservation.json`: exact nonrouting AST and project identity to Rev.2.
- `assembly-identity.json`: regenerated BOM/CPL are byte-identical to Rev.2.
- `manufacturing/`: CAM, paste, BOM/CPL, assembly drawing, parsed checks, previews
  and artwork review ZIP. Read the Rev.3 process note with that data.
- `runs/`, `cell-inputs/`, `inspection/`, `processes/`: retained candidates,
  inputs, output project metadata, commands, timestamps, stdout/stderr and
  independent acceptance results. Failed candidates are not manufacturing data.
- `baseline.json`, `git-base.json`, `resume-state.json`: immutable Rev.2 source,
  private git branch and interrupted-run continuation state.
- `final-cleanup.json`: one exact redundant WING_EN segment removed.
- `*.nonroute-preservation.json`: original nonrouting AST restored after native
  numeric reserialization; route AST verified unchanged.
- `preservation-audit.json`: hashes of existing files; only authorized D-029 append.
- `manifest.json`: hashes of the evidence files except the manifest itself and
  publication metadata, which is recorded after pushing.

Acceptance code is separate from generation: `inspect-cell.py`,
`audit-via-pads.py`, `physical-audit.py`, `check-cam.py`, `verify-final.py`.
It reads saved files and does not use router acceptance predicates.
`repair-grid*.py` only generate bounded local routing candidates.

Runtime setup inherits the local KiCad 9.0.9 / KRT 0.23.8 / Python 3.12 tools
from Issues #129/#178; `common.py` records paths and constructs a headless
isolated environment. CAM/assembly rendering uses
`.issue147-runtime/viewer-venv/bin/python` (Gerbonara 1.5.0, CairoSVG, Pillow).
Tool versions and source hashes are in `runtime-toolchain.json`.

All recorded `argv` in `processes/*/record.json` are reproducible with that
runtime environment. Use a new process/output directory when rechecking:
`run()` deliberately refuses to replace existing evidence. For example,
import `common` from this directory and call `run('recheck-vias',
['/usr/bin/python3', E/'audit-via-pads.py', E/'board/m1-matrix18.kicad_pcb',
T/'recheck-vias'])`. Original acceptance results stay intact.

No order, charge, manufacturer preview or merge. This is a Draft PR review
package. Rev.2's inherited ISSUE178 silk label remains unchanged by design;
identify Rev.3 using its directory, board hash and fabrication note.
