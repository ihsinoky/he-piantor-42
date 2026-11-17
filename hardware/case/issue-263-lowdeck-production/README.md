# Issue #263 — low-deck case production tree (plate top Z10.90)

Production geometry for the D-042 (as amended) low-deck case. The
geometry itself was designed and audited in Issues #261/#264; this
tree is the production record that ties those sources to the
as-routed boards of the implementation round.

## Sources of truth (do not fork the geometry here)

- Case bodies, formed FPC channel, shells, slope, Fly seat:
  `hardware/case/issue-261-lowdeck-full/` (REPORT.md + preview.step +
  sources/audit_static.py body set). Datum: tray floor 1.60 ribbed,
  Wing PCB underside B=4.70, plate top 10.90, plateau/keytop 22.00
  PROVISIONAL (Junana caps unmeasured — gate 6 OPEN; shell heights
  stay at the study datum until the measurement lands).
- Folded stock FFC + folding jig: `hardware/case/issue-264-stockffc/`
  (REPORT.md, plan-view.png, path-vertices.csv, sources/preview264.step,
  sources/jig-right.step/.stl, sources/jig-slider.step). Cable:
  Molex Premo-Flex 152660149, five folds, S1 slider detents keyed to
  the measured cable length (148–156 mm).
- Boards: `hardware/kicad/qualification/issue-263-implementation/`
  (Wing Rev.5 ×4, Main Rev.8). As-built connector envelopes verified
  against the audited spec in
  `issue-263-implementation/pose-verification.json`: Wing envelope
  centres (±27.0, −37.5) exact, mouths (±27.0, −34.3) vs slot −34.2;
  Main envelope centres/yaws per spec (J2 (−23.09, 40.97) yaw +38°,
  J3 (+23.30, 40.80) yaw −43°, case frame).

## Fitted audit (re-run for this round)

The #264 nominal fitted audit was re-run unchanged for this
production record (script: issue-264 runtime `run_final.py`;
log + result copied to `audit-rerun/` when complete): gate 1 =
0 unexpected contacts for both folded cables against all non-tray
bodies at pitch 17, cable-vs-cable 0; tray pairs dispositioned by
the formed channel (corridor census 51.07 mm³, all on route-corridor
boxes); gate 3 service PASS with the one named residual from #264
(unplugged drape end resting on the Main top face, 0.499 mm³ model
overlap at 0.07 mm penetration); gates 4/5 PASS by inheritance;
gate 7 print envelopes PASS (footprint unchanged from the #248
case, 2.65 mm lower; jig 42×98×11 mm prints on the Ender-3 Pro).

The as-routed boards change no audited solid: board outlines,
connector envelope positions and the cable model are the audited
ones (pose verification above). Copper-level changes are inside
the board solids.

## Follow-up round (2026-11-17) — extended Main outline fit

The Main Rev.8 outline grew two connector tabs (PO option (a);
depths 4.738 mm (J2) / 4.721 mm (J3) past the Rev.7 slanted edges,
silkscreen-governed). Fit was re-checked against the #261 audit
body set with an exact board->case transform (H1/H2/H3 washer
anchors, residuals 0.000 mm):

- Tray pockets: the tab corners enter tray material by
  3.94 mm³ (left; case X −28.96..−26.44, Y 46.57..49.92,
  Z 4.70..5.90) and 3.61 mm³ (right; X 26.44..28.82,
  Y 46.57..49.68). CASE DELTA: add a local pocket relief of
  exactly those two volumes to tray-left / tray-right. The relief
  cuts into existing tray material only — the D-037 silhouette
  is NOT exceeded.
- Wing/Main seam — CONFLICT: the tabs also overlap the Wing
  boards' inner corners. Verified against the TRUE Wing Rev.5
  outlines placed at the fitted poses (J_WING anchor + ±30.5°
  fit, section symdiff 2.9%): plan overlap 47.5 mm² (left) /
  46.7 mm² (right), bite up to 1.95 mm into the Wing outline.
  The Rev.7 edge-to-Wing seam gap is 1.516 mm, and the FH12 pad
  corners themselves reach ~4.0 mm past the Rev.7 edge — tab
  shrinking cannot clear this; the #261 Main ZIF poses are
  inconsistent with the Wing outlines at board level (the #261
  audit checked above-board envelopes, never board-vs-board at
  the seam). DISPOSITION IS A PO DECISION (see Issue #263
  REPORT follow-up §F2); the case delta above is necessary but
  not sufficient while the seam conflict stands.

## Print / production notes

- Trays + shells: PETG, per #261/#248 production settings; formed
  channel is part of the tray toolpath (see #264 REPORT §3).
- Jig: PETG former 42×98×11 mm (~15 g) + slider; R2.0 former pins;
  print from `issue-264-stockffc/sources/jig-right.stl` (+ slider
  STEP; mirror for the left hand — the #264 tree carries the right;
  generate the left by mirroring the STL at print time and record
  the mirror in the build log).
- FFC: buy 152660149 (152 mm nominal); measure every lane's
  resistance BEFORE folding (acceptance ≤1.30 Ω/lane, expected
  0.075–0.10 Ω); set the S1 detent from the measured cable length;
  fold on the jig; do not crease (R2.0 formers).
