# Issue #292 EDGE-FIX round plan (worktree he-piantor-wmain-fix, branch issue-292-edgefix)

Defect: adopted board (SHA 509e52a7..., D-058) has copper reaching/crossing the
Edge.Cuts outline. PO review caught it visually; completion round's DRC JSON
(other worktree) lists 114 copper_edge_clearance violations vs the 0.5mm edge
constraint, incl. 0.0000mm at the west dent vertex (71.064, 122.387).

Stages:
- S0 Setup: plan (this file), checkpoint commit. Locate KiCad tooling used by
  prior rounds (kicad-cli / pcbnew python), board file, Rev.10 tree board.
- S1 Reproduce + enumerate: exact-geometry enumeration of every copper item
  (track/via/pad/zone-fill, all layers) CROSSING / TOUCHING / CLOSE (<0.5mm)
  vs Edge.Cuts. Cross-check against completion DRC JSON (114 items). Classify
  inherited-from-Rev.10 vs wireless-introduced. -> edge-items.md. Commit.
- S2 Case margin: measure case-side margin west of the dent from the case
  production tree record; decide dent-fill feasibility (antenna band south
  must not be eaten). Record numbers. Commit.
- S3 Fix: preference (i) re-route/pull-in to >=0.5mm; (ii) dent fill if
  case-compatible and it clears a cluster; (iii) item-level disposition only
  for items that cannot move (no class waivers). Commit per cluster.
- S4 Gates: new checks/copper_containment.py in the issue-292 tree (fails on
  any crossing/touching) -> must be ZERO on final board. Re-run full gate set:
  ERC, DRC severity-all w/ item-level copper_edge review, unconnected=0,
  via-pad audit, antenna/trackpad keep-outs, Wing census, in-field minima,
  outline delta vs Rev.10 exact. Commit.
- S5 Records + outputs: REPORT.md new deviation entry + dispositions + new
  SHA + D-058 amendment note; regenerate manufacturing package; regenerate 3
  PO drawings with annotation overlays CLIPPED to the board outline. Commit.
- S6 Final report to PMO.

Invariants: reproduce before fixing; containment gate runs on the FINAL file
with a generated item list; never /tmp; small segments.

## S2 result (case margin, measured in the #275 fitted frame; method validated by reproducing seam 0.5593 / overlap 0 exactly)
- West of Main's dent sits the left Wing Rev.6 (fitted pose). Free gap: A-B segment 0.559mm (the fitted seam itself), B-C segment 1.99-2.11mm.
- Copper needs the edge >=2.41mm further west at the USB corridor -> dent fill CANNOT clear the cluster (would consume the seam and hit the Wing). Partial fill gains ~0 on A-B, <=1.4mm on B-C: insufficient.
- DECISION: west cluster fixed by RE-ROUTING (preference i). Outline stays Rev.10-identical (delta 0). Recorded in REPORT deviation entry.
- (Note: the #198 dimensions.json wing transform is a different frame and gives a false overlap for Rev.6; do not use it for Rev.6 - the #275 fitted frame above is authoritative.)
