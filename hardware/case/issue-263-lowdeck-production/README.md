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

## Respin round (2026-11-17) — seam closed by the Wing notch; tray relief adopted

PO disposition (i): the Wing boards' inner corners are notched in
the tab zones and the Wing fanout was respun in the same round
(Issue #263 REPORT, respin section). The notch (slanted floor
fitted to the tab + 0.50 mm region, R1.0 fillets) removes
62.6–63.5 mm² of bare corner per Wing board; it touches no
footprint, pad, track or via in any variant.

- Seam verification (final notched Wing outlines vs the as-built
  extended Main Rev.8 outline, fitted poses, both pitches):
  **overlap 0.000 mm²; board-to-board distance 0.5215 mm (L) /
  0.5221 mm (R) ≥ 0.50 mm — PASS.**
- Tray pocket relief: the two local reliefs quantified in the
  follow-up round (**+3.94 mm³ left**, case X −28.96..−26.44,
  Y 46.57..49.92, Z 4.70..5.90; **+3.61 mm³ right**, X 26.44..28.82,
  Y 46.57..49.68, Z 4.70..5.90) are ADOPTED into this production
  record: cut exactly those volumes from tray-left / tray-right
  when the trays are next generated. They cut into existing tray
  material only; the D-037 silhouette is not exceeded. The tray
  geometry itself stays sourced from the #261 tree — this README
  is the delta record, per the sources-of-truth rule above.
- Fitted audit with the final boards: the #264 verification
  bundle re-run reproduces the recorded audit byte-for-byte
  (`audit-rerun/audit264-rerun-respin.log`; gate 1 = 0 unexpected,
  service PASS with the one named #264 residual). The Wing notch
  only removes material from the audited Wing solid; the Main
  tabs' only body-set hits were the tray pockets relieved above.

## Issue #270 round (2026-11-17) — trapezoid tabs + matched Wing re-notch

PO aesthetic direction on Issue #270: the Rev.8 connector tabs
looked distorted; the pair was reshaped together (Stage 2a shape
approved by the PO before board work). Main Rev.9 carries
trapezoid tabs identical at both sites (depth 4.738 mm, front
16.689 mm, base 22.160 mm, walls at 60 degrees to the slanted
edges — the design record's true-60-degree spec; see the #270
REPORT for the Stage 2a script discrepancy disclosure). Wing
Rev.6 (all four variants) re-cuts the notch floor as the exact
0.55 mm offset of the new tab. Rev.9 and Rev.6 are a MATCHED PAIR:
the Rev.9 tabs overlap the Rev.5 notch mouths, and the Rev.8 tabs
do not respect the Rev.6 floor — do not mix revisions.

- Seam verification (final Rev.9 / Rev.6 outlines from the saved
  board files, fitted poses, both pitches, both sides):
  **overlap 0.000 mm²; board-to-board distance 0.550 mm ≥ 0.52 mm
  target — PASS** (was 0.5215 / 0.5221 for the Rev.8/Rev.5 pair).
- Tray pocket relief: the Rev.9 tab solid (Z 4.70..5.90) enters
  tray material by **6.52 mm³ (left)** and **6.31 mm³ (right)**
  in total — i.e. **+2.58 mm³ / +2.70 mm³** beyond the Rev.8
  reliefs adopted above (3.94 / 3.61 mm³). The Stage 2a estimate
  for this delta (+1.81 / +1.94 mm³) was computed on the
  superseded 67.9-degree script geometry; the implemented
  true-60-degree trapezoid is wider at the base. ADOPTED into
  this production record as the new totals: cut 6.52 mm³ (left)
  / 6.31 mm³ (right) of local pocket relief from tray-left /
  tray-right when the trays are next generated. The growth
  solid's only body-set intersections are the two trays and the
  (un-notched, audited) Wing solids — the latter dispositioned
  by the Rev.6 notch above; no shell, plate or Fly body is
  touched. Reliefs cut into existing tray material only; the
  D-037 silhouette is not exceeded.
- Fitted audit: the #264 verification bundle re-run with the
  Rev.9/Rev.6 record reproduces the recorded audit EXACTLY
  (`audit-rerun/audit270-rerun.log` + `final_eval.json` — identical
  to the #264 record on every key): gate 1 = 0 unexpected
  contacts, service PASS with the one named #264 residual. The
  outline-specific interactions are dispositioned by the seam
  and tray computations above and the growth-vs-bodies census
  (`audit-rerun/case-delta-270.log`, both pitches, identical
  results).

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

## Issue #275 round (2026-11-18) — symmetric Rev.10 tabs; flipped-installation pocket

Main Rev.10 symmetrizes the connector tabs (the left tab is now the
exact mirror of the right; J2 sits at the mirror of the J3 pose) and
Wing Rev.6's left notch is the exact mirror of the Stage 2e right
chain. Rev.10 / Rev.6-final are a MATCHED PAIR — do not mix with
Rev.9 (whose left tab is not the mirror of its right tab). Seam
re-verified from the saved board files: overlap 0, distance
0.5593 mm at both pitches and both sides (B3 record in the
Issue #275 REPORT).

- Tray pocket relief (Rev.10 tabs, Z 4.70..5.90 vs the audit tray
  bodies): left 6.305 mm3 / right 6.305 mm3 — the right
  reproduces the Rev.9 total (6.31 mm3) since the right tab is
  unchanged; the left becomes the mirror value. ADOPTED as the new
  totals, replacing the Rev.9 figures above, when the trays are
  next generated. Reliefs cut into existing tray material only;
  the D-037 silhouette is not exceeded. (Computation:
  case-delta-275, both pitches, identical results —
  audit-rerun/case-delta-275.log.)
- Flipped-installation pocket (NEW, for the Rev.10 flip
  configuration): the flipped Main's tallest parts (C26/C27/C28,
  2.5 mm) hang to Z2.20 against the tray floor Z1.60 — only
  0.60 mm residual. ADOPTED delta: a 1.0 mm pocket under the
  power-stage field, case X -6..+13, Y 28..48, floor at Z0.60,
  restoring the residual to 1.60 mm. Measured against the audit
  body set (both pitches, identical): the pocket box removes
  exactly 380.00 mm3 of tray material and touches no other body;
  the FPC channel runs north of the field and is not intersected.
  Remaining web under the pocket: the design floor is 1.60 mm
  (the audit body set models it at 2.00, conservative), so the
  pocket leaves a 0.60 mm nominal web in the ribbed floor —
  recorded as a production note for the case-print gate.
  (Computation: case-pocket-275 — audit-rerun/case-pocket-275.log.)
- Flipped J4 / Fly cable: the flipped plug itself fits (hangs to
  Z2.80 over the plain floor, 1.20 mm clear). The cable path from
  the flipped plug to the Fly receptacle is the NAMED RESIDUAL of
  Issue #275 — see the Issue #275 REPORT for the attempted loop
  geometry and the deciding audit. No pocket or channel for the
  Fly cable is adopted in this round.
