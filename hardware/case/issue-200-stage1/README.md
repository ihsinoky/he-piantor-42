# Issue #200 Stage 1 geometry study

Review report: [docs/issue-200-wing-rev3-stage1.md](../../../docs/issue-200-wing-rev3-stage1.md).

Run `python3 hardware/case/issue-200-stage1/generate.py` from the repository root,
with Python 3, Shapely 2.2.0 and sexpdata 1.0.2. This parses the native Rev.2
boards and the final Main Phase B board; it does not modify PCB/CAM/case files.
The generator asserts input hashes, geometric feasibility and source invariants,
and invokes `report.py` to render the numeric report.

- `geometry.json`: complete proposed polygons, transforms, connector pads,
  rounded harness paths, lengths, clearances, affected components/mounts,
  hole candidates, source invariant snapshots and SHA-256 provenance.
- `trim-inventory.csv`: every native pad, finite-width track, via, zone boundary
  and filled polygon intersecting removed substrate. UUID/index identify source
  entities. Non-net zone boundaries include mounting rule areas.
- `review-16mm.svg`, `review-17mm.svg`: assembly XY review drawings.
- `inputs/issue198/`: byte copies of generate.py and the two dimensions.json
  files from local Git ref `origin/issue-198-case-stage1`, commit
  `6a596e237d60e5054fb8bfdaf8d39b642b5574a0`. No case regeneration is performed.

All nominal XY dimensions are millimetres. The geometry proposal reserves
space; actual rerouting, service-component placement, GND continuity, physical
mating access, cable bundle/radius and case changes remain Stage 2 work.
The GH reference drawing is [JST GH](https://www.jst-mfg.com/product/pdf/jpn/GH.pdf),
pp. 2–3, consulted 2026-11-07. Finger access and harness envelopes are explicitly
planning assumptions, not manufacturer specifications.
