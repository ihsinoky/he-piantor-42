# Issue #270 Stage 1 plan — Main outline tab reshape, 2D candidates

## Goal
Figures + 2D checks only. No board/case modification.

## Deliverables (in this dir)
- fig-current.png — flat layout (Wing Rev.5 L/R + Main Rev.8, fitted poses, 17mm pitch, D-037 silhouette behind)
- fig-cand-A.png / fig-cand-B.png / fig-cand-C.png — same framing/scale, one candidate each
- candidates.md — per candidate: shape, pad clearance, seam distance, tray delta, copper/re-route scope, recommendation

## Steps
1. [ ] Locate sources: #263 board sources (Wing Rev.5 L/R 17mm, Main Rev.8), fitted poses, case silhouette (D-037), extraction scripts to reuse.
2. [ ] Extract geometry to a common assembly frame: board outlines (polygons), key switch positions, ZIF pad corners (28 signal pads + MP lands, Main frame), Main copper near tabs (tracks/vias/pads), Wing notched outlines.
3. [ ] Sanity-check extraction vs #263 REPORT numbers: tab depths J2 4.738 / J3 4.721, pad-corner edge clearance 0.7241, seam 0.5215 (L) / 0.5221 (R).
4. [ ] fig-current.png. Checkpoint.
5. [ ] Candidate A: filleted tabs (generous radii, blend into outline).
6. [ ] Candidate B: continuous smooth convex expansion across connector zone.
7. [ ] Candidate C: symmetric mirrored trapezoid tabs aligned to slanted edges.
   (Substitute a better candidate if geometry demands; note why.)
8. [ ] Per candidate 2D checks:
   - all 28 ZIF pads + MP lands inside; worst pad-corner edge clearance >= 0.70 (target >= 0.7241 class)
   - seam distance to notched Wing outlines >= 0.50
   - inside D-037 silhouette; tray pocket-relief delta vs current tabs (overlap area; volume class vs +3.94/+3.61 mm3)
   - candidate edge vs Rev.8 copper near tabs: min clearance or re-route scope
9. [ ] Candidate figures (same framing). Checkpoint each.
10. [ ] candidates.md + final commit. Report compact summary.

## Invariants
- ZIF poses fixed (fold plan + case slots).
- Figures same scale/framing across current + candidates.
