# Issue #270 Stage 1 — Main ZIF tab reshape: 2D candidates

Figures: `fig-current.png`, `fig-cand-A.png`, `fig-cand-B.png`,
`fig-cand-C.png` (same framing: full flat layout at the 17mm fitted
poses + zoom on Main's north region; dashed = current Rev.8 outline).
All checks are 2D, in the fitted case frame of the #263/#264 studies.
ZIF poses are unchanged in every candidate (only outline geometry
around the fixed connectors is redrawn).

## Method and harness validation

- Outlines extracted from the adopted board sources (Wing Rev.5
  variants + Main Rev.8 Edge.Cuts); Wings placed with the #263 F2/R3
  fitted-pose method (rotate about the J_WING origin by ±30.5°, anchor
  at (±27, −37.5)); key dots = Hall-sensor footprint centres (the
  switches are plate-mounted and have no board footprints).
- The check harness run on the CURRENT Rev.8 outline reproduces the
  #263 results exactly: seam 0.5215 (L) / 0.5221 (R), overlap 0; tray
  growth intersections 3.284 / 3.004 mm² vs the REPORT-implied
  3.283 / 3.008 mm² (×1.2mm board thickness = the +3.94 / +3.61 mm³
  pocket-relief figures).
- Pad-clearance yardstick = the project's own (pad axis-aligned BBox
  corners vs outline). Note: the #263 REPORT's "0.7241mm" predates the
  FH12 land-length correction (1.50 → 1.30mm, centre-anchored) that the
  follow-up round applied; recomputed on the as-built Rev.8 the same
  yardstick gives **0.8197mm** (worst J3.14). The +0.0956 delta is
  fully explained by that land fix. All candidates are compared
  against 0.8197 and stay far above the 0.70 floor.
- Tray delta = change in (candidate growth beyond the Rev.7 outline)
  ∩ (fitted tray solids), ×1.2mm, i.e. the change to the case pocket
  relief vs the current tabs. Copper check = candidate-removed outline
  region vs Rev.8 tracks/vias/pads in windows around both tabs
  (1,564 items).

## Current (Rev.8, reference)

Minimal rectangular tabs, silk-governed: J2 depth 4.738mm, J3 depth
4.721mm, lengths 16.689 / 16.487mm — hence the asymmetric, "stuck-on"
look PO flagged. Pad clearance 0.8197mm; seam 0.5215 / 0.5221mm;
copper: no cuts, min edge-to-copper clearance 0.226mm.

## Candidate A — filleted tabs (fig-cand-A.png) — PASS, recommended

Same tab footprints as current, with the two front corners rounded
R2.0 and the re-entrant base corners blended with R2.0 fillets, so
each tab reads as a smooth lobe of the outline instead of a pasted
rectangle.

- Pad clearance **0.8194mm** (J3.14) — unchanged class.
- Seam **0.5258 / 0.5263mm** — slightly BETTER than current (the
  rounded front corners remove the closest material).
- Tray relief delta **+0.37 / +0.37 mm³** (total +0.73) — the base
  fillet wedges only.
- Copper: **0 cuts**; min edge-to-copper clearance improves
  0.226 → 0.267mm. Removed outline area 3.50 mm² (the corner rounds).
  No re-route implied.
- Board area −0.01 mm² (unchanged). All invariants pass with margins
  at or above the current board's.

## Candidate C — symmetric trapezoid tabs (fig-cand-C.png) — PASS with a note

Both tabs given ONE identical spec — depth 4.738mm, front length
16.689mm, walls with a 1.0mm run (≈80°), centred on each connector —
so the pair is visibly the same shape mirrored, aligned to the
slanted edges. (A 45° wall was tried first: its base spread
(~26mm at the edge line) reaches the Wing notch boundary and fails
the seam at 0mm; the 1.0mm run is what the notch envelope allows.)

- Pad clearance **0.8364mm** (J3.14) — best of the three (J3 gains
  depth 4.721 → 4.738).
- Seam **0.5219 / 0.5052mm** — passes ≥0.50, but the RIGHT margin
  thins from 0.5221 to 0.5052. Cause is exactly the common depth:
  J3's front moves +0.017mm toward its notch floor. If C is picked,
  stage 2 can hold J3's depth at 4.721 (a 0.017mm spec difference,
  invisible) and restore 0.522 — or accept 0.5052 as-is.
- Tray relief delta **+0.66 / +0.78 mm³** (total +1.45).
- Copper: **0 cuts**; min clearance 0.284mm. Board area +7.89 mm².

## Candidate B — continuous edge (fig-cand-B.png) — FAIL (2D-proven)

Both tab fronts extended toward the apex and joined by a single
R12 fillet arc tangent to both front lines (arc crown 0.94mm north of
the Rev.7 chamfer). Pads, silk and copper all pass, but:

- Seam **0 / 0mm**: the outline OVERLAPS each Wing outline by
  **95.98 (L) / 95.29 (R) mm²** along the whole inter-tab span
  (hatched red in the figure). Root cause: outside the tab zones the
  Wing outlines run only **1.516mm** from the Rev.7 slanted edges,
  while the continuous front needs 4.72–4.74mm — it ploughs ~3.2mm
  into the Wings. The Wing notch voids exist only around the tabs.
- Tray relief delta +17.78 / +17.77 mm³ (total +57.63, incl. growth
  under the FFC corridor); board area +329.88 mm².
- A true continuous edge is therefore impossible without re-notching
  BOTH Wings along the full span (a Wing respin — outside this
  stage's scope and a new fitted-audit/case round). Any ramp that
  stays inside the notch envelope degenerates into candidate A's
  fillets. B is closed at 2D with this evidence.

## Recommendation

**Adopt A** for the Rev.9 outline change: it removes the distorted
look (rounded lobes instead of pasted rectangles), keeps every margin
at or above the adopted board's, implies zero copper re-route, and
costs the case only +0.73 mm³ of pocket relief. Choose **C** instead
only if the strict left/right sameness is worth the thinner right
seam margin (0.5052, or 0.522 with the 0.017mm depth exception
above). Either way stage 2 is outline-only: rebuild the tab region in
the board source, re-run DRC/ERC + extraction + the fitted audit, and
update the case tray relief by the deltas listed here.
