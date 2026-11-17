# Issue #268 — Matrix Rev.4 FPC/ZIF conversion — plan

## Goal
Matrix Rev.3 (GH Wing-link) → Rev.4 with Hirose FH12-14S-0.5SH(55) bottom-contact ZIF,
same arriving-order pin assignment as Wing Rev.5 J_WING, so the stock Molex 152660149
FFC connects Matrix Rev.4 ↔ Main Rev.8 on the bench.

## Inputs to locate
- Matrix Rev.3 sources + manufacturing pkg: hardware/kicad/qualification/issue-182-matrix-rev3/
- Corrected FH12 footprint (.kicad_mod, signal land 1.3mm, Hirose CL586-0533-0):
  issue-263-implementation tree (connector/ dir)
- Wing Rev.5 J_WING assignment (arriving order) + D-024 signal content: issue-263 tree / docs/decisions.md
- KiCad runtime: sibling worktrees' .issueXXX-runtime/ stores

## Stages
0. Locate inputs; record Rev.3 baseline (connector ref, pin map from pads, DRC state if runnable).
1. Copy Rev.3 board sources → new tree hardware/kicad/qualification/issue-268-matrix-rev4/.
   Swap connector footprint to corrected FH12; set pin assignment = Wing Rev.5 arriving order.
2. Re-route connector neighbourhood only. Record copper-diff extent.
3. Gates: DRC 0 / unrouted 0; ERC if native schematic exists else state gap;
   via-pad audit ≥0.10mm floor; pin-map verification from built pad coordinates vs D-024;
   Vfar-style extraction (reference only).
4. Bench connection check vs Main Rev.8: connector pose + 152660149 cable length geometry.
5. Manufacturing package (gerber/CPL/BOM + FABRICATION.md DRAFT / NOT FOR ORDER).
6. REPORT.md (change summary, assignment verification, gates, copper diff, connection check,
   draft adoption line). NO decisions.md edits. Do NOT push.

## Rules
- Scratch only in .issue268-runtime/. CAD python: ~/workspace/tools/cad-venv/bin/python.
- Checkpoint commit after each stage.
