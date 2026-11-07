# Phase B third-start audit (2026-11-07)

Read both runtime instructions in full before changes. Continue branch
`issue-194-wing-rev2-stage2` in `.issue194-runtime/git`; PMO owns push.
Initial worktree retained four routed candidates, source, D-032 draft,
case CSVs and partly generated CAM. Do not rebuild autorouted boards.

The second run stopped at the WebSocket failure after beginning the south
cut. `cut.log` records cuts only for 16mm right and both 17mm boards;
16mm left still had the Phase A rectangle and old mounting centers. Its
failed routing attempt also left required opens. First fresh DRC on start 3:

| Board | Opens | Other violations |
| --- | ---: | --- |
| 16mm left | 14 | 20 dangling tracks, 2 dangling vias |
| 16mm right | 0 | 1 dangling track |
| 17mm left | 1 | 2 dangling tracks |
| 17mm right | 0 | none |

Preserved every existing candidate. Applied the missing 16mm-left cut to
saved input/main PCB and moved its south holes and keepouts. All four
contours now match `wing.rev2`; the regenerated case inputs retain the
fixed frame. Actual bounds replace the stale Phase A height metadata.

Continued local two-layer automatic repair, with a bounded service search
and no-rip passes after blocked service-pad escapes. `pad-escape.json`,
`plane-repairs.json`, `cut-route-removal.json`, `cleanup.json` and
`redundant-tails.json` record edits to each candidate. Power/GND necks use
0.30mm and ordinary vias stay 0.60/0.30mm. Plane repair no longer blindly
deletes whole DRC-dangling tracks: a mid-segment T may carry a required
connection. Tail removal checks required-pad physical connectivity, then
uses fresh DRC and independent final qualification.

Panel tab setback reservations follow the new bounds. Panel generation
transfers the actual five-vertex polygons, retaining both chamfers and
all source hole transforms. CAM verification independently parses emitted
profile segments, drill hits and all BOM/CPL rows against final saved CAD.
Final numeric acceptance is in qualification-summary.json,
mechanical-verification.json and cam-verification.json, with PCB hashes.
