# Issue #273 — Wing Rev.6 notch simplification (Stage 2e): plan

PO complaint (2026-11-18): in fig-2d-wing-notch.png the Wing side
"does not look fixed" — the notch mouths carry an S-wiggle and the
simplification is not legible. Main Rev.9 is ADOPTED (D-044); Wing
Rev.6 adoption waits on this round. Worktree branch
issue-273-wing-notch from origin/main 06efd9a18 (contains the 2d
boards). All work in place in `issue-270-wing-rev6/` (x4 variants).

## Verification extract — what is actually saved in the Rev.6 boards

Method: `extract.py` (this dir) parses the saved `.kicad_pcb`
Edge.Cuts drawings, orders them into the outline chain, transforms to
case frame (fitted pose, wing_xf_factory), and lists the notch span.
Counts use the Stage 2d counting rule (item midpoint within
removed-vs-Rev.5 region buffered 1.0 mm). Shape codes: 0 = line,
2 = arc.

Zone counts as saved: 17L 16 (15 lines + 1 arc), 17R 23 (21 + 2),
16L 16 (15 + 1), 16R 23 (21 + 2). (2d REPORT quoted L 17 / R 23 for
17 mm under the same rule; my recount of the merged boards gives
16 / 23 — the before/after comparison in the 2e REPORT will use this
script's counts on both board generations, one rule throughout.)

Notch span as saved (17L, case frame, dive mouth -> rise mouth):
- DIVE mouth: FOUR ~0.26 mm facet segments (-22.98,32.49) ->
  (-23.85,32.99) — a faceted Rev.5 mouth arc surviving the 2d
  keepout difference. This is the U-dip: it bottoms at case
  y ~= 32.43-32.49, BELOW the dive-straight line (y ~= 32.8), then
  the boundary jumps onto the front straight at (-23.85,32.99).
  The 2d design's dive straight itself is NOT in the saved boundary.
- Front: 2 lines (-23.85,32.99) -> (-28.16,40.48) -> (-33.62,44.75),
  1 arc (R0.55 corner fillet), rise: 1 line -> (-32.39,47.86).
- RISE mouth: SIX ~0.26 mm facet segments (-32.43,48.12) ->
  (-31.62,49.17) — a faceted Rev.5 mouth arc bulging Wing-side of
  the rise line, then the Wing edge continues.
17R is worse: dive mouth = 7 facet segments + 1 arc + a kink pair
((20.92,33.45) -> (20.20,32.78) -> (19.61,32.64)); rise mouth =
6 facet segments. Dip bottoms at case y ~= 32.43 in both panels —
exactly the dips the PO flagged at case Y~32-34.

Root cause: 2d built wing_new = Rev.5 outline MINUS a keepout
(chain + closure toward Main). Wherever the Rev.5 boundary lay on
the Wing side of the chain (both mouths), the old faceted mouth
arcs survived verbatim. The fix must REPLACE the boundary chain
between two anchors, not subtract a keepout.

## Design (per variant, case frame; design-notch-2e.py)

- Floor lines: reuse the 2d offset lines (dive / front / rise at
  GAP 0.55 + per-variant delta from notch2d.json; saved offsets
  0.56) and the R0.55 corner fillets between them (one fillet per
  floor corner, as 2d).
- Wing edge lines E1 (dive side) / E2 (rise side): taken from the
  Rev.5 board's own long Edge.Cuts line elements adjacent to the
  notch (exact lines, not fits).
- Extend the dive straight to intersect E1 (point A) and the rise
  straight to intersect E2 (point B). ONE fillet at each
  intersection joins the straight to the existing edge. Fillet
  radius: largest of {1.0, 0.9, ..., 0.3} whose tangent points fit
  the available runs on both lines (the dive run is short: tab
  dive wall ~2.3 mm; corner-fillet tangent ~1.18 mm at R0.55 —
  expect RM ~0.5 on the dive side; the search records what was
  chosen and why). If no radius >= 0.3 fits a variant, report the
  geometric reason instead of forcing it.
- New outline = Rev.5 outline with the boundary arc between the
  E1-side and E2-side fillet tangent points REPLACED by the new
  chain (constructed via symmetric difference with the lobe region
  enclosed between the new chain and the old arc, so deeper old
  stretches are overridden, not preserved). Verify: single valid
  polygon; dense-sample seam vs the FINAL Rev.9 outline (this
  worktree, D-044) >= 0.550 at the variant's fitted pose; overlap
  0; inside D-037 silhouette.
- Copper: removed region (Rev.5 - new) — routed-copper hits abort
  (fills only, as 2b/2d); added region (new - Rev.5, the cut-off
  mouth bulges) — must intersect NO copper item of any kind
  (it was void in Rev.5; verify, incl. pads/vias/tracks; zone
  polygons reported separately).

## Build (build-wing-rev6-2e.py, adapted from the 2d build)

Base = Rev.5 boards (this worktree's issue-263 tree), splice the
new chain as ONE replacement span (exact lines + true arcs from
notch2e.json), refill zones, fill delta confined to the
removed/added band + 0.75 mm. Checkpoint after the Wing set.

## Gates (gates-2e.py, 2b/2d yardsticks)

Per variant: material DRC 0 (comparative invocation), unconnected
0, wrong-net 0, via-pad minima unchanged. Seam from the FINAL
SAVED boards: min >= 0.550, overlap 0 (17 + 16 mm poses).
Case: Wing outline changed -> check the tray pocket wall delta in
the production case tree; if it moves, update the tree and re-run
the #264 fitted-audit bundle (report the new result honestly;
byte-identical reproduction NOT expected).

## Packages + figures + REPORT

- Regenerate Wing manufacturing packages x4 (gerbers from final
  boards; BOM/CPL re-verified; DRAFT / NOT FOR ORDER).
- Figures FROM THE SAVED BOARD FILES (parse final .kicad_pcb
  Edge.Cuts): fig-2e-full.png (fitted layout, final outlines) and
  fig-2e-notch.png (notch zooms L/R: Rev.5 grey, 2d red dashed —
  from git HEAD boards — NEW blue; same axes as fig-2d-wing-notch).
  Copy both to the goal files/ dir.
- REPORT.md (Rev.9 tree): Stage 2e section — before/after notch
  element counts AS SAVED (this script's rule, both generations),
  seam minima from saved boards, wiggle-removal approach, gate
  table, updated draft Wing Rev.6 adoption line.
- Do NOT edit docs/decisions.md. Do NOT push.
