# Issue #270 Stage 2a plan — C revised: 60° trapezoid tabs + matched Wing notches (2D only)

## PO decision
Candidate C, revised together with the Wing: Main tab walls ~60°,
Wing notches reworked in the same pass so the seam reads as ONE
designed joint (parallel faces, uniform gap). This stage = 2D design
+ checks + figures only. NO board/case file edits.

## Angle definition (to state in the deliverable)
60° = angle between the tab side wall and the board's slanted edge
line (the tab front edge is parallel to that edge). Equivalently:
tab interior angle at the base = 60°, at the front corners = 120°.
Wall run per side = D / tan60° = 2.735mm at D = 4.738.

## Design
- Main: trapezoid tabs, identical spec both sites (D = 4.738,
  front length Lf scanned, centred on each site's current tab
  centre), walls at 60° per above. New outline = Rev.7 ∪ tab blobs
  (same construction as stage 1). Must be a superset of Rev.8 in the
  tab zones (no copper cut possible) — verify removed area = 0.
- Wing: new notch = old Wing outline minus buffer(new Main, g),
  g = 0.55 nominal → floor parallel to tab front + walls at uniform
  0.55 (≥0.52 target, ≥0.50 floor), R0.55 arcs at front corners,
  mouth blends where the offset exits the old outline; R≤1.0 mouth
  fillets noted as implementation allowance for stage 2b.

## Checks (17mm primary; 16mm reported with same construction)
- seam L/R (target ≥0.52, floor 0.50); pad-corner clearance
  (≥0.82 class, floor 0.70); silk containment.
- Wing: removed-area delta vs current notch (63.5 L / 62.6 R mm² at
  17mm); new notch region ∩ Wing copper (tracks/vias/pads, all 4
  variants, case frame) = must be empty; also report min distance
  from notch region to copper.
- Main: edge vs copper near tabs (stage-1 item set).
- Case: both outlines inside D-037 silhouette; Main growth ∩ tray
  delta vs current tabs (stage-1 harness, CUR_TRAY 3.284/3.004 mm²).

## Validation anchors
- Current seam reproduces 0.5215/0.5221 at BOTH pitches.
- Stage-1 harness numbers for current/C re-run as control.

## Figures (system python3 + matplotlib, phone-legible)
- fig-s2a-layout.png — full layout, new outlines bold, current dashed.
- fig-s2a-zoom-j2.png / fig-s2a-zoom-j3.png — tight seam zooms:
  panels current / new + overlay.

## Deliverable
stage2a-design.md + figures + stage2a.json, committed. No push.
