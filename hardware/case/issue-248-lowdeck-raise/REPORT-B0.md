# Issue #248 — B0 exact-solid clearance study (partial)

2026-11-14, 17 mm pitch. **B0 remains open: the repository has no detailed
Main Rev.7 mated GH housing/plug solids.** Exact south-hardware and Fly screens,
the roof study, and an exact terminal-wire screen are delivered. The inherited
GH reservation is explicitly labelled as a reservation throughout; its numbers
are not an exact housing/plug result. No Phase B or production CAD is started.
All Z remain provisional on unmeasured Junana q=1.50.

The newest PO comment was read first using `gh issue view 248 --comments`:
B0 must replace boxes with real solids for GH, south cover hardware and Fly.
Consequently this package does **not** claim to have completed that decision.

[Placed study STEP](b0/roof-obstacles-b0.step), [roof STEP](b0/roof-b0.step),
[GH wire section PNG](b0/section-gh-b0.png),
[Fly section PNG](b0/section-fly-b0.png),
[raw clearance results](b0/clearances-b0.json),
[redress results](b0/fly-redress-b0.json),
[independent STEP verification](b0/verification-b0.json).

## Roof and calculation definition

The eight-solid roof set uses only A4 GeoJSON features marked `current surface
footprint`: central plateau, slope and low south surface, plus both north strips.
The `trimmed_*` features are removed-material references and are excluded.
All wells are already subtracted in those masks. The straight X-parallel start
is Y1.9355925495834185, toe Y38.514430874469895. Top is
`24.65 - 11.10*clamp((Y-start)/(toe-start),0,1)`; low top is Z13.55.
North strips end at start. Skin is **2.00 mm vertical**, as specified by A4;
the corresponding normal thickness on the slope is 1.913824 mm. No fastener,
joint, new pocket or opening is cut into the delivered baseline roof.

The exact solids follow A4's supplied polygon boundaries. Duplicate coordinates
and collinear zero-area backtracking edges are removed before OCCT extrusion.
The latter otherwise create invalid slope side faces. Assertions bound each
region's symmetric-difference area below 1e-6 mm²; no material fragment is
dropped. The roof contains eight valid solids, volume **32001.277514 mm³**.
Separate solids meet at the height breaks; internal seam edges in sections are
not openings.

OCCT Common measures intersection volumes. For comparison with A2–A4,
**raw signed gap is the minimum vertical underside-minus-obstacle gap** over
the actual solid inside each roof footprint. Negative denotes the vertical
interference/required lift, not a general 3D penetration-distance algorithm.
Each obstacle is clipped by the actual region; a rotation and OCCT optimal
support bound evaluate its support against that region's affine underside.
This does not substitute the obstacle's unrotated AABB for its shape.
Numbers are reported to 1e-6 mm, with OCCT tolerance about 1e-7 mm.

Unsigned 3D solid distance is also saved: zero for the intersecting groups.
For nonintersecting terminal wires the reported clearance is the true minimum
Euclidean BRep distance. Outer-surface vertical gaps are the signed underside
gaps plus the unchanged 2 mm skin. The JSON includes regional slope-normal
plane gaps as additional information; these differ from vertical lift.

## Every obstacle's provenance and datum

All source paths below are relative to `hardware/`.

| Obstacle | Most exact available source used | Qualification |
|---|---|---|
| South screws `cover-screw-2/3` | `case/issue-246-delta6-tuning/packed/delta-6/17mm/assembly-with-cover.step`, named leaves | Actual adopted study BReps: Ø1.60 shaft and 1 mm conical Ø1.60→4.00 head, reconstructed/exported by #246 `study.py` lines 133–145; no replacement boxes |
| South POM spacers `cover-Main-spacer-2/3` | Same STEP, named leaves | Actual adopted annular cylinders Ø4.50, bore Ø2.20, height 3.00 mm |
| Fly cable | Same tree, `fly-170mm.step` | Exact connected OD2/R5 sweep, one solid, centreline 170.000000 mm; measured solid volume agrees with 170π to <0.001 mm³ |
| Main GH housing/plug | Same assembly, `Main-GH-left/right` | **Reservation only.** #246 `study.py` lines 77–82 extrudes a rotated 20.75×7.15 rectangle by 4.55 mm; no housing cavities, latch or separate plug exists |
| Main first wire bends | Same tree, `measurements.json`, `wings[].conductor_waypoints_mm` | Exact terminal approach, first R5 bend and terminal straight reconstructed from each of fourteen complete OD1 wire paths per side, using #246/#232 rounded-line/arc sweep method. Earlier traverse/rise/storage excluded; no route changed |

The `issue-246`, `issue-244`, `issue-242`, `issue-240`, `issue-238`,
`issue-232`, and Wing `issue-235` study sources were traced. The Wing
`actual-GH-exit-*.step` files are wire fanouts, not Main Rev.7 housing/plug
models. Wing mating studies also use drawing envelopes. The Rev.7 PCB references
a KiCad header WRL path, but supplies no mated GHR plug solid or exact assembly
model. Connector source notes give reference mated dimensions, not sufficient
solid geometry to infer an exact clearance. No detailed connector was invented.
The missing input is a detailed, correctly posed **SM14B-GHS-TB + GHR-14V-S**
assembly for J2/J3, registered to the Rev.7 PCB and actual wire outlet.

The #246 STEP is in the **final +6 mm frame**. Its actual `main` PCB leaf has
underside Z16.000000, top Z17.200000. Translation **−8.65 Z** yields underside
**Z7.35**, top Z8.55, exactly A4. All placed obstacle STEP leaves receive −8.65.
The hardware then has spacer Z9.05…12.05 and screw head Z12.55…13.55.

The Fly STEP includes +6: its upper bound is Z21.60, becoming Z12.95 after
−8.65. Its saved waypoints/samples **precede** +6: high axis Z14.60 becomes
Z11.95 with **−2.65**. Thus −2.65 is correct for rebuilding from samples, but
would be wrong for translating the saved STEP. Terminal wire waypoints likewise
receive −2.65. Source SHA256 hashes are included in the results and manifest.

## Clearances, volumes and AABB conservatism

| Conflict | Raw underside gap mm | Outer-surface gap mm | Roof intersection mm³ | Improvement over A4 AABB mm |
|---|---:|---:|---:|---:|
| GH housing/plug | **Unresolved** | Unresolved | Unresolved | **Unknown**; cannot quantify from a reservation |
| GH reservation, each side, reference only | −1.550000 | +0.450000 | 180.577764 | 0 for the reservation; not evidence about the actual connector |
| GH terminal wires, left | **+0.796077 Euclidean** | — | 0 | Not comparable to the housing/plug AABB |
| GH terminal wires, right | **+0.900000 Euclidean** | — | 0 | Not comparable to the housing/plug AABB |
| South screw, each | **−2.000000** | 0.000000 | **8.545132** | **0.000000** |
| South spacer, each | **−0.500000** | +1.500000 | **6.051493** | **0.000000** |
| Fly 170 cable | **−1.400000** | +0.600000 | **151.911506** | **0.000000** |

The real screw rim, spacer annulus and cable top all occupy the low south roof
footprint, so their AABBs happened to give the exact worst vertical values.
Exact shapes reduce occupied/intersection volume but do not improve these minima.

Representative worst points, in assembly XYZ mm:

- Screw 2: (−29.892683, 64.400000, 13.550000); screw 3:
  (33.892682, 64.400000, 13.550000). Low underside Z11.55.
- Spacer 2: (−29.642683, 64.400000, 12.050000); spacer 3:
  (34.142682, 64.400000, 12.050000). Low underside Z11.55.
- Fly: entire high horizontal storage lengths south of toe share Z12.95 top.
  The section at X−14.60/Y56 has the full −1.40 mm interference; the minimum
  is not confined to one isolated point. The result JSON also records a
  mathematically equivalent witness on the slope/toe boundary.
- Left terminal wire: (−32.838842, 38.490683, 10.754277), nearest roof
  (−32.838842, 38.514431, 11.550000). Right: (25.258841, 42.417545, 10.650000),
  roof point directly above at Z11.55. These gaps exceed +0.30 without a measure.

## Minimum local measures against 2.00 mm skin / +0.30 mm gap

These are dimensional clearance screens, not adopted retention or roof designs.
Closed flat local ceilings quoted below require their transition walls to remain
outside the obstacle's +0.30 clearance envelope.

| Conflict | Pocket screen | Measure retaining the yardsticks |
|---|---|---|
| GH actual housing/plug | Cannot size exactly without missing solids | **Keep unresolved.** Do not commit a local dimension from the proxy. The reservation-only upper design screen is 1.85 mm relief: pocket skin 0.15 mm fails; closed ceiling Z13.40 / top Z15.40, maximum +1.85 above low/toe surface, would retain 2 mm. This is not a minimal exact connector measure. Terminal wires need no relief. |
| Screw head | 2.30 mm required removal; −0.30 mm remaining skin, impossible closed pocket | Head alone needs **Ø4.60** coaxial through-opening for 0.30 radial gap; screw+spacer together need **Ø5.10** at each adopted screw axis. Closed alternative: local underside Z13.85, top Z15.85, +2.30 height. |
| POM spacer | 0.80 mm depth, only 1.20 mm skin: fails | Shared **Ø5.10** opening above; or closed underside Z12.35, top Z14.35, +0.80 height. |
| Fly | 1.70 mm depth, only 0.30 mm skin: fails | A closed local blister needs underside **Z13.25**, top **Z15.25**, maximum **+1.70 mm** above the existing low/toe surface. Above the slope its required rise reduces with increasing base height. This retains full 2 mm skin and 0.30 cable gap. The tested redress below does not eliminate this need. |

Exact opening centres are **(−31.892683,64.400000)** and
**(31.892682,64.400000)**, from the exported #246 solids; the ~1e-6 left/right
coordinate asymmetry is retained. Independent replay cuts Ø5.10 through the
unchanged roof and measures **+0.300000** to each spacer and **+0.550000** to
each screw. A smaller concentric opening cannot give 0.30 to the Ø4.50 spacer
at its roof-intersecting height. Removing the screw seat still leaves retention
unresolved; no retention redesign or spacer shortening is performed.

The screw/spacer relief is on the flat low surface, not on the slope. The Fly
maximum also occurs south of the slope toe. Quoting a height only at an arbitrary
slope section would miss the governing clearance.

## One Fly redress variant

The single tested family retains both endpoints, every other #246 waypoint,
OD2 and all R5 bends. Move the south U's two south waypoints north together;
widen the west leg (its two X coordinates) to restore **exactly 170.000000 mm**.
An analytic rounded-segment calculation solves west width for length and then
finds the northern limit imposed by R5 tangent consumption. Only the final
candidate is swept and exact-solid screened.

| Parameter | Baseline | Tested north limit |
|---|---:|---:|
| South U Y mm | 61.120414680 | **59.179085350** |
| Northward shift mm | 0 | **1.941329330** |
| West leg X mm | −14.600000000 | **−16.806395412** |
| Connected centreline mm | 170.000000000 | **170.000000000** |
| Minimum centreline radius mm | 5 | **5** |
| Minimum straight remainder after tangent consumption mm | — | **0.000100000** |
| Exact minimum vertical roof gap mm | −1.400000 | **−1.400000** |
| Roof intersection mm³ | 151.911506 | **151.911506** |

**FAIL for this redress family.** The west leg between the south U and the fixed
Y51 return runs out of straight length between its R5 tangencies. Its south Y
cannot move below approximately 59.179 without moving other return waypoints.
The fixed Y45 return also remains beneath low roof. For comparison, a high
horizontal OD2 segment would need its axis at or north of approximately
**Y32.719364** to give +0.30 true normal free gap to the unmodified slope
(ignoring footprint edges). Moving the south U alone cannot reach this region.

This is a failed screen of one restrained redress variant, **not a proof that
all 170 mm reroutings are impossible**. No broader storage/retention redesign or
clearance audit against other assembly bodies is claimed. The placed PMO STEP
shows the baseline Fly; the tested alternative is separate in
[fly-redress-b0.step](b0/fly-redress-b0.step).

## Verification and reproduction

Independent STEP replay checks all 43 delivered solids valid (eight roof, two
GH reservations, four hardware, one Fly, twenty-eight terminal wires). It
checks roof export volume, both baseline/redress Fly volumes against 170π,
redress R5 segment slack and exact length, and input hashes. Hardware Common
volumes independently match analytic values: screw `2.72π`, spacer
`1.92625π` mm³ each. The Ø5.10 opening clearance check passes. Both PNGs were
visually inspected; they plot actual OCCT X-constant section edges, not AABBs.
The GH PNG expressly shows the exact wire minimum and unresolved housing/plug.

Run from repository root, with build123d/OCP and numpy available in CAD Python:

```bash
export TMPDIR="$PWD/.issue248-runtime"
export MPLCONFIGDIR="$TMPDIR/mpl" XDG_CACHE_HOME="$TMPDIR/cache"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
# One-time study dependencies if absent; scratch stays in this worktree:
/home/hatch/workspace/tools/cad-venv/bin/python -m pip install --target "$TMPDIR/caddeps" shapely sexpdata --no-deps
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/study-b0.py
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/verify-b0.py
/usr/bin/python3 hardware/case/issue-248-lowdeck-raise/plot-b0.py
```

Scripts store scratch BReps, import cache and dependencies only under
`.issue248-runtime/`. [B0 manifest](artifact-sha256-b0.json) binds the report,
scripts, output artifacts and source inputs. No baseline or A–A4 artifact is
changed. To close B0, obtain the missing exact mated GH housing/plug geometry,
substitute it for the labelled reservations, and rerun its exact gap/volume and
minimum-measure calculation. All other Phase B gates remain outside this study.
