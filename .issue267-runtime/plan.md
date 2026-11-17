# Issue #267 — JLCPCB package conversion plan

## Sources of truth (verified by reading the files)
- Format exemplar: `issue-226-main-rev6/manufacturing/` — BOM.csv header
  `Comment,Designator,Footprint,LCSC Part #` (per-designator rows, real LCSC codes,
  NO mounting-hole / testpoint rows), `CPL-jlcpcb-gerber-frame.csv` header
  `Designator,Mid X,Mid Y,Layer,Rotation`, coordinates with `mm` suffix,
  `quote-handoff.md`. PR #220 method: gerber-frame = native + per-board frame offset,
  verified to ~1e-6 mm.
- Main parts: Rev.6 BOM (Rev.7 = Rev.6 + J2/J3 connector swap only; no separate
  Rev.7 manufacturing package exists in the tree). Overrides:
  - C26/C27/C28: Rev.6 LCSC blank → adopted substitute TDK C3225X7R1C226MT000N
    = **C342699** (docs/issue-175-main-dual-wing-final2.md, PR #177/#189).
  - R17: Rev.6 LCSC blank → adopted substitute Yageo RT0603BRD0754K9L = **C728593** (same doc).
  - L1: C3033018 (order-time rule, stock 19,053 on 2026-11-16). J4: C588524.
  - J2/J3: FH12-14S-0.5SH(55) → placeholder C-HIROSE-FH12-14S (never invent a code).
- Wing parts: Matrix Rev.3 BOM (`issue-182-matrix-rev3/manufacturing/BOM.csv`) —
  same part set as Wing: DRV5055A3QDBZR=C266128, GRM188R71C104KA01D=C45000,
  TMUX1208PWR=C494728. J_WING → FH12 placeholder.
- Non-orderable (excluded from BOM-jlcpcb, as Rev.6/Matrix packages exclude them):
  NPTH mounting holes, test points / PCB pads.
- Source boards (per make-packages.py): Main = `issue-263-implementation/inspection/final/main.kicad_pcb`;
  Wing = each variant's `main.kicad_pcb`. CPL.csv + gerbers both came from kicad-cli
  default exports → frames expected identical; MUST be proven per board, not assumed.

## Method per board
1. BOM-jlcpcb.csv: Rev.6 4-column format, grouped rows as in native BOM,
   LCSC filled from the maps above; unmapped designators listed, never invented.
2. CPL frame derivation: parse Edge.Cuts geometry from the source .kicad_pcb
   (KiCad frame, y-down) and from gerber/main-Edge_Cuts.gm1 (gerber frame);
   fit translation (tx, ty) with gerber = (kx+tx, -ky+ty); verify EVERY outline
   vertex maps within 0.001 mm.
3. CPL-jlcpcb-gerber-frame.csv: native CPL + (tx, ty); cross-check every point
   against the source board's footprint origins through the same transform;
   report max deviation. Orderable designators only (Rev.6 practice).
4. quote-handoff.md per package (Rev.6 model): upload files, FH12 placeholder,
   unmapped parts, DRAFT status.
5. `.issue267-runtime/conversion-report.md` summary. Checkpoint commit per board.

## Boards
main-rev8, wing-rev5-17mm-left, wing-rev5-17mm-right,
wing-rev5-16mm-left, wing-rev5-16mm-right.
