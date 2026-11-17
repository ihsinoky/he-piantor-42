# Issue #270 Stage 2b — Board implementation plan

## Goal
Apply ONLY the approved Stage 2a outline changes to the adopted boards:
- Main Rev.8 → **Main Rev.9** (60° trapezoid tabs, identical spec both sites)
- Wing Rev.5 (4 variants) → **Wing Rev.6** (notch floor = exact 0.55mm offset of the new tab)
Matched pair: Rev.9 Main requires Rev.6 Wings and vice versa.

## Steps
1. Read stage2a-design.md + stage2a.json (approved outline geometry source).
2. Locate Rev.8 / Rev.5 board sources in issue-263-implementation tree.
3. Build new trees:
   - `hardware/kicad/qualification/issue-270-main-rev9/` (Main Rev.9 + REPORT + packages)
   - `hardware/kicad/qualification/issue-270-wing-rev6/` (Wing Rev.6 ×4 + packages)
   Method: copy board sources, replace Edge.Cuts geometry with Stage 2a outlines
   (scripted .kicad_pcb edit; no routing/footprint/schematic changes).
4. Gates per board (same yardsticks as #263):
   - DRC errors 0, unconnected 0, wrong-net 0
   - via-pad audit floor 0.10 (expect Main 0.1596 / Wing Rev.5 values, verify)
   - pad-corner edge clearance (expect 0.8364)
   - Main ERC 0
   - Vfar: carried over unless outline touches pour/copper → check, re-run only if touched.
5. Case: update `hardware/case/issue-263-lowdeck-production/` tray pocket relief
   (+1.81 L / +1.94 R mm³ vs current tabs per 2a), re-run fitted audit with
   Rev.9 + Rev.6 at both pitches: gate1 = 0, service check, seam 0.550 L/R.
6. Manufacturing packages (JLCPCB-ready): gerber + BOM-jlcpcb.csv (FH12=C5378715)
   + BOM-jlcpcb-consolidated.csv + CPL-jlcpcb-gerber-frame.csv (frame-verified)
   + FABRICATION.md (DRAFT / NOT FOR ORDER) + quote-handoff.md + native BOM/CPL.
7. REPORT.md in the Rev.9 tree: change summary, gate table, matched-pair note,
   case delta, package inventory, DRAFT D-044 adoption line (do NOT edit decisions.md).

## Rules
- Checkpoint-commit after each board. Do NOT push.
- No silent yardstick relaxation; iterate within approved spec (mouth fillets free).
- Scratch only in .issue270-runtime/.

## Notes (during execution)
- Main DRC via standalone kicad-cli flags 500 clearance items @0.2mm rule on
  BOTH Rev.8 (fresh run) and Rev.9: the #263 tree's Main main.kicad_pro
  carries only a Default netclass at 0.2mm (Wing's carries 0.1). Pre-existing
  baseline-records defect; #263's graph gates are the operative yardstick.
  Comparative DRC (same invocation): clearance 500=500, dangling 5=5,
  copper_edge_clearance 14 -> 6 (4 new at J3 tab wall, actual >=0.2821 =
  the designed 0.284 edge-to-copper). Saved Rev.8 drc.json (448) is stale
  vs a fresh run on the same file (500).
- Main tree must nest the board in main-rev9/ subdir: fp-lib-table uses
  ${KIPRJMOD}/../../ paths (Rev.8 sat 3 levels below qualification/).
  Wing tree depth already matches Rev.5. Move Main after Wing builds end;
  ERC 59 footprint_link_issues in the flat layout were this artefact
  (schematic md5 identical to Rev.8; ERC 0 expected after the move).
