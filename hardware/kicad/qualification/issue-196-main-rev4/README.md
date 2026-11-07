# Issue #196 Phase A evidence

Report: [docs/issue-196-main-rev4.md](../../../../docs/issue-196-main-rev4.md).
No routed PCB or manufacturing release is produced.

- `geometry-plan.json`: proposed outline, all 66 footprint before/after poses and pin nets, all four NPTHs and all-layer reservation polygons. Dimensions in absolute KiCad mm, X right / Y down. Connector body-centre datum is explicitly distinguished from native `at`.
- `analysis.json`: pad and hole cut limits, secondary placement checks, original routing intersections identified by UUID/net/layer, old filled copper conflicts and maximum-cut comparison witness (hole fill checks are in `geometry-plan.json`). No qualification claim for a new routed board.
- `layout-proposal.svg`: proposed outline, hole reservations and selected pad bounds for review, not a Gerber or physical body certification.
- `analyze.py`: reproducible read-only calculation. Uses KiCad 9.0.9 `pcbnew` and Shapely 2.2.0. Native pad polygon approximation is conservative (ERROR_OUTSIDE, 10nm). Trace capsules / via circles use 256 subdivisions per quadrant; route-only limits are diagnostic, not new routing qualification.
- `run-analysis.sh`: configures the existing read-only runtime and confines settings/scratch to `.issue196-runtime/`.

Run at the repository root:

```bash
hardware/kicad/qualification/issue-196-main-rev4/run-analysis.sh
```

On this worker, the commit repository is itself `.issue196-runtime/git`, so the original scratch root was supplied explicitly:

```bash
ISSUE196_SCRATCH=/home/hatch/workspace/projects/he-piantor-mainrev4/.issue196-runtime \
  hardware/kicad/qualification/issue-196-main-rev4/run-analysis.sh
```

`KICAD_RUNTIME_PARENT` defaults to `/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime`, with `kicad/` and `geometry/` below it. It may point at another equivalent runtime. No packages are installed and no runtime files are modified. Python bytecode is disabled. Results overwrite only the three generated study outputs (JSON×2 and SVG) and are deterministic for the same input/runtime. The script checks the exact Rev.3 source SHA256 and its native connector origins before calculating. It never calls SaveBoard, a router, or a zone filler.

Asserts cover unchanged pad nets/values/orientations; frozen J1; 66 footprints; proposed electrical-part gaps ≥0.10mm; all-pad edge gaps ≥0.20mm; closed/simple/symmetric 48×52mm outline and 2435mm² area; four hole reservations inside the outline; boss-to-edge ≥0.75mm and boss-to-pad ≥0.25mm; and a witness for the larger southern-cut alternative. Future copper exclusion follows from each reservation's minimum inradius ≥2.5mm. Existing GND at the new H3 site is explicitly reported as a conflict requiring Phase B, never silently removed from the source PCB.
