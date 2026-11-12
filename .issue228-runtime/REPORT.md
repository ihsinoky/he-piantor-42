# Issue #228 — Phase A outline approval gate

2026-11-12. **Proposal complete; awaiting PO approval. Phase B is not authorized by this report.**

**Rounds 1–3 below are historical. The authoritative ROUND 4 (RETRY) section at the end supersedes the south design, numbers, and handoff notes; the round-2/3 north and USB remain unchanged. Round 4 reports a shelf-limit conflict for PMO/PO resolution.**

The 17mm proposal replaces each Wing's entire stepped thumb-to-pinky south
boundary with one straight segment. Both Wings keep their original PCB,
pocket, and assembly placement. The generator implementation is in
`hardware/case/issue-228-outline/`, forked from Issue #198 final data.

## Approval images and machine-readable evidence

- [Assembled overlay](../hardware/case/issue-228-outline/17mm-outline-overlay.png): red dashed = current #198; teal solid = proposal; blue-gray = unchanged PCB/pocket.
- [South-edge zoom](../hardware/case/issue-228-outline/17mm-south-edge-zoom.png): complete left south run; right is its mirror.
- [Exact polygons and measurements](../hardware/case/issue-228-outline/17mm-outline.json).
- [Measurements](measurements.json), including nearest-point witnesses.

The PNGs are 2D plots, not 3D renders. No 3D regeneration, verify.py runs,
renders, STL/STEP or manufacturing exports were performed in Phase A.

## South edge design and segment replacements

Each Wing starts from a five-line enclosing envelope. The south line is
parallel to the chord from the outermost pinky PCB point to the southernmost
thumb PCB point. Its support is selected from the existing mitered PCB
clearance/wall envelope, including the projecting tips at the thumb steps,
plus a 0.002mm numerical allowance. It meets extensions of the existing
pinky side and inner-thumb side. The result is unioned with the original
outer outline, preserving all existing material and the central structure.

- Left: pinky **(-147.661805, 2.621697)** to thumb **(-47.173443, 84.978749)** mm.
- Right: mirrored across X=0: **(147.661805, 2.621697)** to **(47.173443, 84.978749)** mm.
- Length **129.925343 mm** each, angle **39.336952 degrees** to horizontal (mirrored on the right).
- Exact left supporting line: `-0.633879810498 X + 0.773431565068 Y = 95.627539970517`.
- Straight segment throughout; no intermediate vertex, step, arc or finite radius.
- End corners are sharp miter intersections, with no new fillet radius.

This replaces the finger-column stair/valley, its return toward the thumb,
the intermediate thumb steps and the two-segment convex thumb bulge with
one exposed line. Existing oblique west/east sides and north Wing sides
remain straight; their southern ends extend to meet that line. The inner
thumb side continues into the existing central south bridge.

Retained corners/steps: the two south-line endpoint corners preserve the
side directions; the north Wing corner preserves the PCB clearance; the
central south bridge and X=3.5mm cut preserve the existing center structure.
The north central neck keeps its existing clearance-derived small facets
and short shoulder near X=±10.498mm. The Wing envelope fills a small exterior
wedge where it meets the neck, so the external outline there is a union,
not an assertion that every center-edge coordinate is unchanged. The
interior UDB seat/pocket and original high-wall geometry are unchanged.
These neck features are deliberately retained to avoid redesigning the
seat or USB region. No step remains on either thumb-to-pinky run.

## Vertex counts and footprint

Counts are for complete tray XY silhouettes after the unchanged floor
splice reinforcements and split at X=3.5mm; closure points are excluded.

| Tray | Current raw vertices | Proposed raw vertices | Current/proposed after removing collinear splits | Proposed XY mm | With 5mm brim, XY mm |
|---|---:|---:|---:|---|---|
| Left | 37 | 19 | 37 / 17 | 151.162 × 149.345 | 161.162 × 159.345 |
| Right | 37 | 19 | 37 / 17 | 144.162 × 149.345 | 154.162 × 159.345 |
| Total | 74 | 38 | 74 / 34 | assembled 295.324 × 149.345 | — |

The two additional raw vertices per proposed tray are Boolean-operation
splits on straight lines, not corners. Collinear normalization uses
1e-8mm topology-preserving simplification. Existing neck curve facets are
counted as vertices in both versions; no favorable curve-sampling change
is used in the comparison.

Assembled bounds: X=[-147.661805,147.661805], Y=[-64.366600,84.978749] mm.
Each half is comfortably within a 220×220mm bed, including the baseline
5mm brim. The old assembled bounds were X=±145.662125mm and
Y=[-64.366600,80.802680]mm. Overall width grows 3.999359mm; depth grows
4.176069mm. Added XY material area is 2273.461163mm² across both halves.

## Minimum wall and continuous 2D containment proof

The unchanged pocket is reconstructed by the same arithmetic as base.py:
union of all board polygons buffered **0.502mm**, plus the original
`box(-11,-24,11,12)`, then topology-preserving simplification at 0.002mm.
The extra 0.002mm in the clearance is the existing #198 numerical allowance.
Main/UDB geometry comes from the existing #198 17mm dimensions file
(SHA256 `6aa22662e6e17bd797de505303033fa1a2f729e74169e32c2a6355ff39ead086`).
Both Wing boundaries are independently rebuilt from the unchanged Rev.3
CSVs with their recorded transforms and match to 1e-9mm.

The reported wall is the exact GEOS polygon-boundary distance, not a grid
or vertex sample. The minimum is **2.000000mm** (floating-point result
1.9999999999999882mm), at the left pinky-side wall:

- Pocket witness **(-142.930074499, -1.573899846)** mm.
- Outline witness **(-144.662125307, -2.573899846)** mm.
- The right Wing has the mirrored minimum (2.000000mm).

Distances use the real external boundary. The intentional split seam cuts
through the open pocket; it is not treated as an enclosing 2mm perimeter wall.
The floor-only splice pads are included in footprint/vertex counts; they
cannot reduce the wall distance.

| Wing | Bare PCB minimum to outline | PCB witness → outline witness (mm) | Existing clearance envelope minimum to outline |
|---|---:|---|---:|
| Left | 2.502000mm | (-13,-45) → (-12.567985,-47.464420) | 2.000000mm |
| Right | 2.502000mm | (13,-45) → (12.567985,-47.464420) | 2.000000mm |

For each Wing the proposal `covers(PCB.buffer(0.502, join_style=2))` is
**true**, and the clearance-envelope area outside the proposal is exactly
**0mm²**. The entire unchanged pocket is covered, also with **0mm²** outside.
The original full case silhouette has **0mm²** outside the proposal. These
are continuous polygon-set containment operations over every edge and
interior point, not checks at selected PCB vertices. Both complete south
segments are also asserted to lie on the exposed proposed boundary (1e-8mm
numerical tolerance), ruling out a residual step from the legacy union.

## Palm flush behavior and interior invariants

**Vertical behavior is preserved by construction.** `base.py` derives the
upper wall from the legacy ring with precisely the original palm, keycap
and USB exclusions. The new ring uses the new outer boundary and unchanged
pocket. All added material stops at the existing flush level, Z=11.2mm
(default PCB top); the existing --palm-offset=-0.5 option remains available.
No new palm wall rises above the PCB top.

**Explicit lateral deviation:** the south edge no longer follows the PCB
at a constant offset. It bridges the old recesses, creating a wider flush
palm shelf. Its location is the straight line specified above; this added
shelf and the larger footprint are part of the PO approval decision.
There is no claimed preservation of the old lateral staircase relation.
The original pocket south boundary remains exactly where it was.

No PCB inputs, pocket, mounting coordinates, 15 fixing points, bosses,
harness path, cable rack, split position, heights or daughterboard seat
were edited. `details.py` and `verify.py` are byte-identical baseline copies.
The upper-wall expression was changed only to reference the legacy ring,
so added XY material cannot introduce new raised walls. These are source
and 2D construction statements, not a claim of completed 3D validation.

## Implementation and Phase B handoff

`outline.py` is a pure Shapely module, consumed directly by the variant's
`base.generate`; this is not a one-off drawing. `phase_a.py` consumes the
same module and builds only 2D evidence. `generate.py` defaults to the
unchanged #198 inputs. The new module participates in cache keys and input
provenance hashes; future STEP caches stay under `.issue228-runtime/`.
Reproduction instructions and pinned 2D dependencies are in the working
folder README. The implementation files parse successfully without running
CAD. The 17mm 2D script passes its containment, wall, full south-boundary
and bed assertions. No verify.py suite was run.

After explicit PO approval and a separate Phase B dispatch:

1. Regenerate with this variant for 17mm and 16mm; run the full verification
   suite on both, then renders and required exports. Phase A evaluates only
   17mm. The line direction/support are computed from the chosen PCB, not
   hard-coded 17mm coordinates; the envelope's retained neck landmark
   assumes assembly Y=-45mm and should be checked on the 16mm inputs.
2. Check BRep topology and meshing around Boolean joins, the sharp thumb
   and pinky endpoints, neck facets and X=3.5mm split. Repeat actual 3D
   print-envelope checks, with the existing brim allowance.
3. Confirm the added flush shelf meets palm comfort expectations and the
   old upper-wall masks still give zero palm high-wall overlap. The wider
   shelf and sharp endpoint corners are intentional PO design choices.
4. Verify all 15 bosses/pilots, mounting alignment, feet, splice plates,
   seat and USB access, rack fit and harness/keycap/component clearances
   against actual regenerated solids. Existing material is preserved and
   no added material is above PCB top, but this does not replace 3D checks.
5. Preserve unchanged PCB input hashes. The copied #198 schema/source
   labels in details.py/verify.py are historical; make any Issue #228
   release metadata adjustment consistently during Phase B.
6. CAD packages are not installed by the 2D dependency command. Use the
   documented CAD venv with the existing requirements.txt supplied for
   Phase B, keeping any local dependency installation/scratch in runtime.

## Git and stop condition

Git state lives only in `.issue228-runtime/git`, using the checkout as the
work tree and the original object store as a read-only alternate. The
implementation commit is on `issue-228-case-outline`, parent `5de75375`
(the checkout's origin/main baseline). The checkout's original `.git` is
untouched. No push, PR or merge was performed.

**STOP: PO approval is required before Phase B.**

## Phase A ROUND 2 — historical rejected proposal, 2026-11-12

**Complete at the 2D gate; awaiting PO review.** The PO rejected the round-1
straight south run and retained north USB notch. This section supersedes
round 1, including the old statements about sharp corners, retained neck
facets, no removed material, footprint and Phase B corner checks. Historical
round-1 geometry is reproducible by `round1_outline()` and is included in
the updated evidence JSON.

### Review evidence

- [Assembled three-way overlay](../hardware/case/issue-228-outline/17mm-outline-overlay.png).
- [Complete south curve and both endpoint junctions](../hardware/case/issue-228-outline/17mm-south-edge-zoom.png).
- [North-center notch removal and USB port](../hardware/case/issue-228-outline/17mm-north-center-zoom.png).
- [Polygons, parameters, counts and continuous-distance witnesses](../hardware/case/issue-228-outline/17mm-outline.json).
- [Round-2 measurement ledger](measurements.json).

Red dashed is #198; faint purple dotted is rejected round 1; teal is round 2.
Blue-gray shows the unchanged boards and pocket. Amber hatching is the plan
projection of the USB wall opening above the intact floor/low rim; it does
not represent a notch cut through the bottom silhouette.

### R1 — one south spline per wing; front angles

Each south edge is **one cubic polynomial Bezier span**, a spline with no
internal knots. Left control points in assembly XY mm, in pinky-to-thumb
order:

| Control | X | Y |
|---|---:|---:|
| P0 | -146.148167075 | 0.000000000 |
| P1 | -166.148167075 | 34.641016151 |
| P2 | -64.298960788 | 114.641016151 |
| P3 | -44.298960788 | 80.000000000 |

`B(t)=(1-t)^3 P0 + 3(1-t)^2 t P1 + 3(1-t)t^2 P2 + t^3 P3`,
`0<=t<=1`. Right is the X-mirror of these controls. Both tangent handles
are **40 mm**. The start derivative follows the unchanged pinky side
(-0.5,+0.866025404); the end derivative follows the unchanged inner-thumb
side (+0.5,-0.866025404). Thus both endpoint joins are analytically tangent,
with **180° limiting interior angle**, eliminating the pointed thumb tip.
The cubic has no cusp (the gate checks its derivative roots).

The same module used by Phase B samples each span into **512 chords**.
The minimum unsigned interior angle on a south curve and its two endpoint
junctions is **179.213593°**, at left **(-47.471317,83.988894)**, mirrored on
the right. The two sampled endpoint joins are **179.641423°** and
**179.640779°**. These are the actual polygon angles, including the finite
sampling effect, not merely ideal spline claims. Every such angle exceeds
120°. The retained straight inner-thumb side joins the unchanged central
south bridge at **120°**, at **(±38.757553,70.402)**. Therefore the minimum
across the complete front, including these further bridge junctions, is
**120°** (floating-point 119.99999999999999°).

A conservative chord deviation bound `max ||B''||/(8*512²)` is
**0.000403007 mm** for each south span. Exact containment and distance
checks below apply to the actual sampled polygon that Phase B consumes.
The sampling vertices must not be mistaken for new design corners.

### R2 — continuous north curve

The entire north run is one quadratic Bezier, from right to left, with
controls **(108.986093174,-64.366600111)**,
**(0,-45.261241305)**, **(-108.986093174,-64.366600111)** mm.
Its endpoint tangents match the original wing north-edge directions.
It crosses X=0 at **Y=-54.813920708 mm**, with a horizontal tangent.
The old center-north rectangular dip and both small neck facet chains are
absent from the silhouette. The new north edge is smooth across both wings
and the USB region. Its 512-chord deviation bound is **0.000036441 mm**.
The original outer north-to-pinky corners remain outside the front run.

### R3 — USB opening and unchanged daughterboard seat

The opening is a **12 mm wide, 4 mm high, open-top U-slot**, at default
**Z=11.2..15.2 mm**, with air above it. It preserves the existing low rim
and floor below Z=11.2 mm, so the bottom plan outline stays continuous.
This follows the baseline open-top access strategy, without adding a roof.

The X center is **-0.002 mm**, derived directly from current C3 J1 relative
to J2 using the exact existing seat transformation. The current connector
front datum is **(-0.002,-34.750) mm**. The slot extends from outside the
new north wall through to **Y=-34 mm**; its plan cut bounds are
**X=[-6.002,5.998], Y=[-65.366600,-34] mm**. It crosses the new wall near
Y=-54.814..-54.843 mm. Both slot edges and the connector-front datum are
shown on the north-center figure. The 12 mm clear width is horizontal X;
the local north curve is almost horizontal across it.

`base.py` now calls shared `usb_access()` rather than the old cut limited
to Y=-50 mm, which would stop short of the new wall. Added north material
outside the original silhouette receives the existing 15.2 mm wall-top
height, subject to the existing palm/keycap masks; the slot cuts that upper
material. Existing high-wall material is clipped to the new silhouette.
No daughterboard seat, mounting datum or board height is redesigned.
**Final connector/plug alignment and fit belong to the pending Fly seat
rework.** This is a provisional aperture using the current seat datum,
not a claim of completed 3D port/plug validation.

### R4 — full containment, wall and material removal

The unchanged #198 pocket arithmetic, authoritative dimensions SHA256
`6aa22662e6e17bd797de505303033fa1a2f729e74169e32c2a6355ff39ead086`,
and independent Wing CSV/transform checks are retained from round 1.
All checks are continuous GEOS polygon operations over whole edges and
areas. **Pocket outside proposal: 0 mm².** For **all four boards**
(Main, both Wings, UDB), the complete **PCB + 0.502 mm mitered clearance**
is covered, with **0 mm² outside**. Both entire south curves lie on the
exposed boundary, so there is no hidden legacy stair or notch.

Minimum pocket-to-outline wall: **2.000000 mm** (floating-point
1.9999999999999625), with witnesses:

- Pocket **(-142.930074499,-1.573899846)** → outline
  **(-144.662125307,-2.573899846)** mm. Right side mirrors this.
- Minimum bare PCB-to-outline distance: **2.502000 mm**. Left PCB
  **(-142.244329746,-1.757644598)** → outline
  **(-144.411125307,-3.008644598)** mm; right mirrors this.
- Main PCB also reaches 2.502000 mm at **(-37.892683,67.9)** →
  **(-37.892683,70.402)**. UDB has 18.563921 mm to the plan perimeter;
  its north access is the opening above the low rim described in R3.

The wall metric is the enclosing XY pocket-to-external-perimeter distance;
it excludes the intentional split seam and the above-rim USB opening.

**Material IS removed relative to #198:** two tiny outer thumb miter-tip
slivers, **0.007410591 mm² each**, **0.014821181 mm² total**. Left bounds:
**X=[-44.782613470,-44.298960788], Y=[80.000000000,80.802680137] mm**;
right bounds are mirrored. Interior removal witnesses:
**(±44.592504772,80.498929867)** mm. The exact removed polygons are in the
JSON. Near these slivers the minimum pocket-to-new-boundary distance
(within a 0.01 mm neighborhood of the removal) is **2.265012154 mm**, with
left witness **(-45.494439189,78.070629329)** →
**(-44.293961532,79.991341034)** mm. These regions are outside the pocket;
all global wall and PCB-clearance constraints continue to hold.

| Assembled footprint area comparison | Added mm² | Removed mm² | Net mm² |
|---|---:|---:|---:|
| Round 2 versus #198 | 8153.807276 | 0.014821 | +8153.792454 |
| Round 2 versus round 1 | 5871.566508 | 4.054889 | +5867.511619 |

This proposal is a broad convex south shelf; it prioritizes smooth tangent
joins and makes the size increase explicit for PO review.

### R5 — counts, bed fit, unchanged interior and palm flush

Counts exclude closure points and include the unchanged splice floor pads
and split at X=3.5 mm. Segment counts equal vertex counts for each closed
polygon. No simplification is used to hide spline sampling vertices.

| Tray | #198 segments/vertices | Round 1 raw (normalized) | Round 2 sampled segments/vertices | Round 2 XY mm | With 5 mm brim XY mm |
|---|---:|---:|---:|---|---|
| Left | 37 | 19 (17) | 781 | 152.236134 × 152.880916 | 162.236134 × 162.880916 |
| Right | 37 | 19 (17) | 764 | 145.236134 × 152.880916 | 155.236134 × 162.880916 |
| Total | 74 | 38 (34) | 1545 | assembled 297.472268 × 152.880916 | — |

The unequal sampled counts arise from the off-center X=3.5 split crossing
the north curve. At design-primitive level, each half has **one south cubic,
one portion of the north quadratic, and four straight segments including
the seam: six segments**, versus 37 straight segments in #198.

Assembled bounds: **X=±148.736134044,
Y=[-64.366600111,88.514315735] mm**. Each tray grows **3.074009 × 7.711636 mm**
versus #198 and **1.074329 × 3.535567 mm** versus round 1. Both fit 220×220 mm,
including a 5 mm brim. Assembly width grows **6.148017 mm** versus #198 and
**2.148659 mm** versus round 1.

Pocket, bosses, all 15 fixing points, harness, rack, split, heights and
DB seat remain unchanged. `details.py` and `verify.py` remain byte-identical
to round 1. The outline and the north wall/USB access handoff in `base.py`
are the only geometric code changes. Added material in the palm span stays
at or below the existing PCB-top flush level **Z=11.2 mm**, subject to the
unchanged palm-offset option. The north-wall addition is restricted to
Y<-45 and has the original palm and keycap exclusions applied, so it cannot
create a raised palm shelf. Source input hashes and pocket reconstruction
are unchanged; no interior generation has been executed in this round.

### Validation, handoff and stop

`phase_a.py` passes full pocket and all-board clearance containment,
minimum wall, local removal wall, front angles, tangent directions, cusp
check, complete south-boundary exposure, USB passage reach, CSV matching,
and both 220 mm bed checks. Source AST parsing and whitespace checks also
pass. All three PNGs were visually inspected. The JSON contains both
comparison baselines and the exact sampled proposal.

`outline.proposed_outline()` is consumed directly by Phase B, and
`usb_access()` supplies the extended opening to both the gate and the
existing generator. Curve datums derive from the selected PCB, original
side supports, and unchanged bridge. Phase A checks **17 mm only**; the
16 mm variant still requires its separate Phase B geometry validation.

After PO approval and a separate Phase B dispatch, check spline-chord BRep
quality, real USB plug passage with the pending Fly seat alignment, all
interior/fastener/harness/rack clearances, palm masks, bed bounds and both
pitches under the normal complete 3D validation process. The round-1 sharp
endpoint and retained-neck handoff assumptions are withdrawn.

**STOPPED at the 2D gate: no 3D generation, verify.py, renders, or CAD/
manufacturing exports.** Only 2D approval figures and JSON were regenerated.
Git uses `.issue228-runtime/git`, branch `issue-228-case-outline`; round 2
builds on round-1 commit `cdecdc89`. No push or PR.

## Phase A ROUND 3 — authoritative proposal, 2026-11-12

**Complete at the 2D gate; awaiting PO review.** This section supersedes
round 2 for the south curve, footprint, area, segment counts and endpoint
joins. The round-2 north quadratic, removed notch, current daughterboard
seat datum and W12 × H4 open-top USB access are unchanged. Rounds 1–2 above
are historical rejected proposals.

### Evidence and construction

- [Assembled overlay](../hardware/case/issue-228-outline/17mm-outline-overlay.png):
  #198 red dashed; round 2 faint purple; round 3 solid teal.
- [South-edge zoom](../hardware/case/issue-228-outline/17mm-south-edge-zoom.png):
  unchanged pocket and bare boards, stepped #198 outline, shallow spline,
  endpoint fillets and valley distance witnesses. Right mirrors left.
- [North-center detail](../hardware/case/issue-228-outline/17mm-north-center-zoom.png).
- [Exact polygon and design controls](../hardware/case/issue-228-outline/17mm-outline.json).
- [Measurement ledger](measurements.json): shelf profile, all junctions,
  removed regions, distance witnesses and primitive/chord counts.

Each wing has **one continuous C1 cubic spline with six polynomial spans**
(no internal corner), terminated by **two circular R5 mm fillets**. It is
not the round-2 single cubic with its long tangent handles. The spline
interpolates three projecting stepped tips shifted 0.8 mm outward along
the original support normal. Two additional valley controls draw it inward
by 12 mm and 2 mm relative to the adjacent shifted-tip chord midpoints.
These are inward reductions of shelf width, not outward bulges. The deep
finger-column recess needs the larger reduction to keep the nearest PCB
distance below 10 mm. The endpoint support corners come from round 1;
R5 fillets trim them back toward the actual PCB tips.

All spline spans share their tangent at each internal knot. The chord-axis
coordinate increases linearly on every span, so its derivative cannot
vanish: there is no cusp. The end derivatives match the circular fillets;
the fillets meet the retained pinky/inner-thumb sides tangentially. Each
cubic uses 512 chords; each fillet uses 128. Phase B consumes exactly this
sampled 2D boundary through `outline.proposed_outline()`.

### S1 — shelf-depth profile and tip tracking

Depth here means **nearest Euclidean distance FROM a point on the south
perimeter TO the bare PCB south-edge chain**, not to the pocket or to #198.
The direction matters: it is not distance from a recessed PCB vertex back
to the curve, nor a normal-ray depth. Stations are placed at chord-axis
projections of the projecting #198 tips; valley centers are midpoint
stations between adjacent tips. The thumb-tip station falls beyond the
trimmed spline domain, so it uses the nearest point on its endpoint fillet.
The first and last intervals are continuous sloping edge groups rather
than deep column recesses; all four interval centers are reported.

Maximum sampled depth: **9.823802 mm**, perimeter **(-102.288038, 18.798274)** → bare PCB **(-97.376137, 10.290612)**.

The complete 20,001-station arclength check has spacing
0.007475218 mm. Distance-to-set is 1-Lipschitz; adding half
the spacing gives a conservative maximum **9.827540 mm**
over the actual consumed polygon. This proves the whole curve is below
10 mm, including all valley centers. The JSON profile records every 100th
sample plus the exact maximum and all specified stations. The largest
analytic-curve/chord bound is 0.000111142 mm
(the endpoint arcs); the bound also leaves the ideal curve below 10 mm.

| Interval center, pinky → thumb | Curve XY mm | Bare-PCB depth mm |
|---|---|---:|
| 1 (tips 0–1) | (-130.443768, 11.802836) | 5.843439 |
| 2 (tips 1–2) | (-97.427400, 19.882778) | 8.332691 |
| 3 (tips 2–3) | (-83.319976, 51.149425) | 5.791803 |
| 4 (tips 3–4) | (-59.377208, 75.847322) | 5.517944 |

| Protruding tip, pinky → thumb | #198 tip XY mm | Curve-to-PCB depth at station mm | Nearest #198-tip-to-curve distance mm |
|---|---|---:|---:|
| 0 | (-145.662125, -0.841849) | 3.129503 | 0.197484 |
| 1 | (-110.969533, 19.187929) | 4.058853 | 0.692574 |
| 2 | (-97.999898, 38.021079) | 4.214784 | 0.630872 |
| 3 | (-70.150723, 66.144718) | 4.212160 | 0.796730 |
| 4 | (-44.762388, 80.802680) | 3.471145 | 0.082127 |

The three internal projecting tips remain outside #198 and within 0.8 mm
of it. The two endpoint fillets clip the old miter tips slightly (below),
as permitted by S4; all clearance and wall constraints still hold.

### S2 — every front junction, fillets and minimum angle

Left junctions are listed below; every right junction has X negated with
the same angle/radius. Interior angles exclude the curved arc interiors.
These are tangent joins at the fillets, not the former sharp support
corners. Their hypothetical unfilleted support angles are 85.403871° at
the pinky and 82.201630° at the thumb; those corners are removed entirely.

| Junction | Left XY mm | Interior angle | Adjacent fillet radius mm |
|---|---|---:|---:|
| pinky side / fillet | (-144.952764, -2.070499) | 180° | 5.0 |
| pinky fillet / spline | (-142.767618, 4.946033) | 180° | 5.0 |
| spline knot 1 | (-111.476636, 19.806674) | 180° | — |
| spline knot 2 | (-97.385261, 19.942070) | 180° | — |
| spline knot 3 | (-98.507002, 38.639824) | 180° | — |
| spline knot 4 | (-83.314655, 51.154781) | 180° | — |
| spline knot 5 | (-70.657827, 66.763464) | 180° | — |
| spline / thumb fillet | (-51.702271, 81.466036) | 180° | 5.0 |
| thumb fillet / inner side | (-44.307721, 80.015174) | 180° | 5.0 |
| inner side / south bridge | (-38.757553, 70.402000) | 120° | — |

**Minimum front interior angle: 120°**, at both retained inner-side/bridge
joins; no acute front junction. The spline-only sampled minimum is
**179.411974°**, at
(-97.372672, 19.960555). Including fillet chords and their
endpoint joins, the sampled south minimum is
179.235950°. Sampling vertices
are not design corners. All four endpoint fillets have radius **5 mm**.

### S3 — north and USB unchanged

The gate asserts exact equality of the north controls and of the complete
north boundary (Y ≤ -45 mm) against reproducible round 2. Controls remain
(108.986093174,-64.366600111), (0,-45.261241305),
(-108.986093174,-64.366600111) mm. The notch remains removed.
The USB opening stays W12 × H4 mm, open top, X center -0.002 mm,
Z=11.2..15.2 mm, current connector front (-0.002,-34.750) mm,
plan cut X=[-6.002,5.998], Y=[-65.366600111,-34] mm.
The slot geometry is identical; floor and low rim remain intact. Final
plug alignment still belongs to the pending Fly seat rework.

### S4 — containment, minimum wall and material changes

The unchanged pocket is reconstructed by the same #198 arithmetic and
independent Wing CSV/transform checks as before. The dimension input hash
remains `6aa22662e6e17bd797de505303033fa1a2f729e74169e32c2a6355ff39ead086`.
Continuous GEOS set checks prove pocket outside proposal = **0 mm²**,
and **all four complete PCB + 0.502 mm mitered clearance envelopes are
covered**, each with **0 mm² outside**. These checks cover entire edges
and regions; they are independent of the sampled shelf profile.

Minimum enclosing pocket-to-perimeter wall: **2.000000 mm**,
pocket (-142.930074, -1.573900) → perimeter (-144.662125, -2.573900);
right mirrors left. Floating-point result is 1.9999999999999614 mm.
The intentional split seam and above-rim USB opening are excluded from
this enclosing XY wall metric, as in rounds 1–2.

| Board | Bare PCB minimum to perimeter mm | PCB → perimeter witness XY mm | Clearance-envelope margin mm |
|---|---:|---|---:|
| main | 2.502000 | (-37.892683, 67.900000) → (-37.892683, 70.402000) | 2.000000 |
| wing_left | 2.502000 | (-142.244330, -1.757645) → (-144.411125, -3.008645) | 2.000000 |
| wing_right | 2.502000 | (142.244330, -1.757645) → (144.411125, -3.008645) | 2.000000 |
| udb | 18.563921 | (0.000000, -36.250000) → (0.000000, -54.813921) | 18.061921 |

| Complete silhouette comparison, including unchanged splice pads | Added mm² | Removed mm² | Net mm² |
|---|---:|---:|---:|
| Round 3 versus #198 | 2099.155951 | 0.243454 | +2098.912498 |
| Round 3 versus round 2 | 0.000015 | 6054.879972 | -6054.879957 |
| Round 3 versus round 1 | 877.601481 | 1064.969819 | -187.368338 |

Added area is comfortably below +3,500 mm² and close to round 1's
+2,273 mm², rather than round 2's +8,154 mm². Approximately 6,055 mm² of
the rejected round-2 silhouette disappears. The 0.000015 mm² added versus
round 2 is a negligible near-coincident endpoint sampling sliver, not a
new shelf.

The four removed #198 regions are two pinky miter tips and two thumb
miter tips, total **0.243453532 mm²**. For readable local bounds/witnesses,
the region ledger strips numerical zero-width tails along shared straight
supports by a 0.0000001 mm opening; each area changes by less than 1e-7 mm².
Global and per-region areas, containment, and the exact current/proposed
polygons use the original unmodified geometry. Local wall witnesses below use a 0.01 mm
neighborhood of each cleaned region.

| Removed location | Area mm² | X bounds mm | Y bounds mm | Interior witness XY mm | Local minimum wall mm |
|---|---:|---|---|---|---:|
| Left thumb | 0.025257951 | [-44.834681, -44.307736] | [80.015200, 80.802680] | (-44.564579, 80.434967) | 2.273303 |
| Right thumb | 0.025257951 | [44.307736, 44.834681] | [80.015200, 80.802680] | (44.564579, 80.434967) | 2.273303 |
| Right pinky | 0.096468815 | [144.952779, 145.662125] | [-2.070472, -0.739053] | (145.306352, -1.403058) | 2.079999 |
| Left pinky | 0.096468815 | [-145.662125, -144.952779] | [-2.070472, -0.739053] | (-145.306352, -1.403058) | 2.079999 |

All removal is outside the unchanged pocket. Exact nearest-point pairs
for the local walls and all global PCB/clearance distances are in JSON.

### S5 — footprint, primitive counts and unchanged interior

Assembled bounds: X=±145.622568436 mm,
Y=[-64.366600111,82.515075147] mm. Assembled footprint is
**291.245137 × 146.881675 mm**. Relative to #198, total width changes
**-0.079114 mm**, depth **+1.712395 mm**. Split remains X=3.5 mm.

| Tray | XY mm | With 5 mm brim, XY mm | XY change versus #198 mm | Raw sampled segments (#198 / round 2 / round 3) |
|---|---|---|---|---|
| left | 149.122568 × 146.881675 | 159.122568 × 156.881675 | -0.039557 × 1.712395 | 37 / 781 / 3597 |
| right | 142.122568 × 146.881675 | 152.122568 × 156.881675 | -0.039557 × 1.712395 | 37 / 764 / 3580 |

Both trays, including brim, fit 220 × 220 mm. Primitive counts per tray:
**one south spline (six cubic spans), two circular fillets, one north
quadratic portion, four straight segments including seam** = **8** when
treating the spline as one curve, **13** resolving its spans. Baseline #198
has 37 straight segments per tray. Raw sampled counts are reported without
simplifying away curve chords; closure duplicates are excluded.

`base.py`, `generate.py`, `details.py`, `verify.py`, all PCB inputs and all
interior geometry are unchanged from round 2. The new south material uses
the same flush-level ring (default PCB top Z=11.2 mm); the existing high-wall
masks are unchanged. Mounts, 15 fixings, bosses, harness, cable rack, seat,
heights, splice pads and split are unchanged. This is a source/2D invariant
statement, not completed 3D validation.

### Reproduction, validation and Phase B handoff

Use the README's 2D command. `outline.proposed_outline()` is the active
round-3 implementation consumed directly by Phase B. Historical
`round2_outline.py` is the byte-identical round-2 module from commit
`d720f5e9`; call its `proposed_outline()` to reproduce round 2. Its polygon
is also regenerated into `round2_xy` in the evidence JSON. Round 1 remains
reproducible with `round1_outline()`. The historical full round-2 evidence
and gate script remain available in `d720f5e9`.

The 17 mm gate passes: continuous containment/wall checks for all boards,
both entire south boundary exposures, spline/fillet tangency, front angles,
shelf upper bound, tip tracking, area guideline, north equality, USB reach,
independent Wing CSV matching and both bed checks. All three updated PNGs
were visually inspected. Source parsing and Git whitespace checks pass.

After explicit PO approval and a separate Phase B dispatch, validate both
17 mm and 16 mm generated solids, spline/chord BRep quality (including the
concave valley and R5 joins), component/fastener/rack/harness clearances,
palm masks, bed fit and provisional USB passage with pending Fly seat
alignment. The spline landmarks use the current Wing boundary vertex
ordering; the 16 mm input still requires its separate geometry validation.

**STOPPED at the 2D gate. No 3D, verify.py, renders or CAD/manufacturing
exports.** Git uses `GIT_DIR=./.issue228-runtime/git`, branch
`issue-228-case-outline`, building on `d720f5e9`. Local commit only; no push
or PR. Phase B remains unauthorized until its separate dispatch.


## Phase A ROUND 4 (RETRY) — convex south sweep; supersedes round 3 south

**2D candidate ready for PMO/PO review; T3 conflict, not an all-target pass.**
The active `outline.py` now supplies round 4 to Phase B. One quadratic
Bézier per wing replaces the six-span interpolating round-3 spline. It
bridges the recessed columns without following any valleys or interpolating
column tips. North and USB remain the round-2/3 design. Earlier sections
remain historical; this section is authoritative for the south outline.
No 3D generation, `verify.py`, renders or CAD/manufacturing exports were run.

### T1/T2 — one convex curve family

The curve is a **single quadratic Bézier with a strictly convex control
triangle**, plus tangent R5 endpoint fillets. A minimum-area numerical fit
within this family, constrained by the unchanged pocket and 2 mm wall,
selected the stored envelope-relative offsets. This is a fitted candidate,
not a claim of global optimality across every possible convex curve family.
There are no internal knots, inward controls, inflections or column shoulders.

Left Bézier controls, in assembly XY mm (+Y south):

| Control | XY mm |
| --- | --- |
| 0 | (-143.829403, 4.001145) |
| 1 | (-98.346875, 44.149426) |
| 2 | (-51.230953, 80.654849) |

Signed sampled turns: left **negative**, mirrored right **positive**;
**0 sign changes per wing**, checking all 511 interior triples
of the 512-chord sweep. The exact derivative cross product is constant,
-925.057530303 mm², strictly negative for every parameter.
Thus the continuous polynomial also has no hidden inflections between samples.
All 767 interior triples of the full sweep-plus-fillets path also turn
strictly negative on the left (positive by reflection on the right).

Minimum sweep curvature radius: **1831.186829 mm analytic**,
at t=1.0; sampled circumcircle minimum
1831.356095 mm. Including endpoint fillets, minimum
radius is **5 mm**. Curvature magnitude can jump at the tangent R5 joins;
tangent continuity is exact. It keeps the same sign across those joins.
The requested run from pinky fillet exit to thumb fillet entry is the single
quadratic, not the fillets.

### T3 — shelf profile and unavoidable conflict

Shelf means nearest Euclidean distance **from the perimeter curve to the
bare PCB south chain**, not to the pocket or old case edge. Measured along
the entire south path, including both fillets, with 20001 equally
spaced arclength samples (0.006780882 mm spacing).

Maximum sample **16.801255 mm**, at
(-110.754620, 32.533297); nearest bare PCB witness
(-111.885328, 15.770133), arclength
50.537914 mm from the pinky fillet start.
The 1-Lipschitz sampling upper bound is **16.804645 mm**.
The right wing mirrors this witness. This exceeds 13 mm by
3.801255 mm, and **does not meet T3**.

The oversize shelf is a band, not just one exceptional station. Depth is
above 10 mm from arclength 28.764502 to 58.620725 mm, approximately
X=-127.322392..-104.563131; above 13 mm from arclength 43.682442 to
54.843774 mm, approximately X=-115.988515..-107.459069. Threshold locations
are sampled to within one profile spacing. In particular tip station 1 is
12.462335 mm, so the ordinary 10 mm target also fails outside the single
deep valley-center station. These are explicit conflicts for PMO/PO, not
additional accepted exceptions.

Valley stations use the midpoint of adjacent #198 projecting tips in the
pinky-to-thumb chord projection; the normal ray intersects the new curve.
The same station definition as round 3 is retained. Endpoint rays that miss
the trimmed fillet use the nearest curve point. Tip numbering runs pinky 0
to thumb 4; the deep notch is between tips 1 and 2.

| Valley between tips | Shelf mm | Curve XY mm | Nearest PCB XY mm |
| --- | --- | --- | --- |
| [0, 1] | 8.758378 | (-132.300096, 14.096965) | (-127.920907, 6.511987) |
| [1, 2] | 14.649532 | (-108.916051, 34.080935) | (-94.582102, 37.105284) |
| [2, 3] | 8.751228 | (-85.305832, 53.603629) | (-78.103719, 48.632354) |
| [3, 4] | 4.319602 | (-58.614064, 74.904197) | (-56.454263, 71.163312) |

| Tip station | Shelf mm | Curve XY mm | #198 miter-tip distance to curve mm |
| --- | --- | --- | --- |
| 0 | 3.045455 | (-145.260723, -1.337919) | 0.256861 |
| 1 | 12.462335 | (-117.290291, 26.999388) | 10.045385 |
| 2 | 7.148728 | (-100.501773, 41.113002) | 3.977022 |
| 3 | 3.321882 | (-69.979352, 65.932931) | 0.272428 |
| 4 | 3.241074 | (-44.973852, 80.548502) | 0.330641 |

All 20,001 profile rows and nearest-point witnesses are saved in
`17mm-shelf-profile.csv`. JSON includes a 201-row overview, max, tip and
valley stations, and the >10/>13 mm bands. The smooth perimeter lies outside
the bare PCB tips with required clearance/wall; tiny old miter protrusions
can be trimmed without violating containment (T7 ledger below).

**Independent convexity lower bound:** take the unchanged pocket convex-hull
support edge from (-142.930074,-1.573900) to (-67.418672,65.412668).
The 2 mm wall requires both endpoints translated by 2 mm along outward
normal (-0.663618,0.748071) to be inside or on the case. A convex south
boundary must also enclose their connecting chord. At chord witness
**(-109.050119,31.154730)**, nearest bare PCB distance is
**15.643664 mm**, to (-111.885328,15.770133). All PCB points lie on the
north side of this supporting line. Along its outward normal, distance to
every PCB point, hence to the complete bare south chain, cannot decrease.
Any convex south boundary crossing that outward ray therefore has shelf
at least **15.643664 mm**, already **2.643664 mm over 13 mm**.
The opposite endpoint disks and chord lie in the south domain between the
retained sides; the ray meets the south run. This lower bound uses necessary
pocket/wall containment, not the proposed Bézier or optimization result.
It also applies to a non-strict convex hull, so strict convexity cannot
restore the 13 mm allowance. The numerical witness suffices for the bound;
it need not be the exact maximum of the support chord.

### T4 — complete silhouette material changes

Areas include the unchanged splice reinforcement footprints, exactly as
rounds 1–3. Added and removed values are separate set differences.

| Round 4 comparison | Added mm² | Removed mm² | Net mm² |
| --- | --- | --- | --- |
| #198 | 2981.489903 | 1.227967 | 2980.261936 |
| round 2 | 0.000000 | 5173.530519 | -5173.530519 |
| round 3 | 958.902397 | 77.552959 | 881.349438 |

Added area **2,981.489903 mm²** is below the 3,500 mm² guideline by
518.510097 mm², but 882.333951 mm² greater than round 3's added area.
Round-2 added slivers below 3e-12 mm² are floating-point coincidence noise.

### T5/T6 — joins, fillets, unchanged north and USB

| Left junction (right mirrors) | XY mm | Interior angle ° | Radius mm |
| --- | --- | --- | --- |
| pinky side / fillet | (-144.850651, -2.247364) | 180.000000 | 5.0 |
| pinky fillet / sweep | (-143.829403, 4.001145) | 180.000000 | 5.0 |
| sweep / thumb fillet | (-51.230953, 80.654849) | 180.000000 | 5.0 |
| thumb fillet / inner side | (-43.838461, 79.202391) | 180.000000 | 5.0 |
| inner side / south bridge | (-38.757553, 70.402000) | 120.000000 | — |

Analytic tangents at both ends of both R5 fillets are checked against the
Bézier derivative and retained side supports. Entire sampled front has no
acute angles. Each retained inner-side/bridge join is **120°**, and all
curve joins are **180°**. The bridge datum and split X=3.5 mm are unchanged.

North Bézier controls are asserted **exactly equal** to both round 2 and
round 3. Clipped full north boundaries (Y<=-45 mm) have set equality on a
1e-10 mm grid; raw Hausdorff difference is **1.588822e-14 mm**, from GEOS
interpolation of the same analytic side supports at the clip line. This
machine-roundoff difference is explicitly recorded, not a geometric edit.
The USB plan slot is asserted equal as an unrounded GEOS set against both
round 2 and round 3. The north-center PNG is byte-preserved from round 3.
USB remains W12 × H4 mm, open top Z=11.2..15.2 mm, same provisional seat
and connector datum; final alignment belongs to the pending Fly seat rework.

### T7 — unchanged pocket, walls and every board, with witnesses

Authoritative #198 dimension hash remains
`6aa22662e6e17bd797de505303033fa1a2f729e74169e32c2a6355ff39ead086`.
Both Wing CSV polygons are independently rebuilt and matched to the source
transforms. Pocket is reconstructed by the same +0.502 mm mitered union,
connector bay and 0.002 mm simplification arithmetic. **Pocket outside
proposal: 0 mm²**. Every entire PCB +0.502 mm envelope is covered,
**0 mm² outside for each of all four boards**.

Minimum enclosing XY wall **2.000000 mm** (computed
1.9999999999999878 mm), pocket (-142.930074,-1.573900) →
perimeter (-144.662125,-2.573900); right mirrors left. The intentional
tray seam and above-rim USB opening remain excluded from this enclosing
wall metric, as in prior rounds.

| Board | Bare PCB margin mm | PCB → perimeter XY mm | Clearance margin mm | Clearance → perimeter XY mm |
| --- | --- | --- | --- | --- |
| main | 2.502000 | (-37.892683, 67.900000) → (-37.892683, 70.402000) | 2.000000 | (-38.757553, 68.402000) → (-38.757553, 70.402000) |
| wing_left | 2.502000 | (-45.678184, 77.384885) → (-43.511388, 78.635885) | 2.000000 | (-142.930074, -1.573900) → (-144.662125, -2.573900) |
| wing_right | 2.502000 | (45.678184, 77.384885) → (43.511388, 78.635885) | 2.000000 | (142.930074, -1.573900) → (144.662125, -2.573900) |
| udb | 18.563921 | (0.000000, -36.250000) → (0.000000, -54.813921) | 18.061921 | (0.000000, -36.752000) → (0.000000, -54.813921) |

Removed #198 material totals **1.227967075 mm²** in six regions, all outside
the unchanged pocket. These are pinky/thumb miter trims and the adjacent
thumb-column miter tips, not PCB or pocket removal. Raw exact polygons and
nearest local wall witnesses are in JSON. For readable bounds only, the
ledger removes 1e-7 mm floating-point tails, with <1e-7 mm² area effect
per region; areas and global checks use the raw geometry.

| Removed location | Area mm² | X bounds mm | Y bounds mm | Interior witness XY mm | Local wall mm |
| --- | --- | --- | --- | --- | --- |
| left thumb column | 0.254075227 | [-70.150723, -68.551293] | [65.906161, 67.068150] | (-69.439749, 66.473987) | 2.000779 |
| left thumb | 0.214994790 | [-45.069049, -43.838476] | [79.202417, 80.802680] | (-44.345613, 79.987573) | 2.005047 |
| right thumb | 0.214994790 | [43.838476, 45.069049] | [79.202417, 80.802680] | (44.345613, 79.987573) | 2.005047 |
| right thumb column | 0.254075227 | [68.551293, 70.150723] | [65.906161, 67.068150] | (69.439749, 66.473987) | 2.000779 |
| right pinky | 0.144913520 | [144.850669, 145.662125] | [-2.247332, -0.706468] | (145.243980, -1.497258) | 2.033410 |
| left pinky | 0.144913520 | [-145.662125, -144.850669] | [-2.247332, -0.706468] | (-145.243980, -1.497258) | 2.033410 |

### Footprint, primitives, evidence and handoff

Assembled bounds X=±145.520519 mm, Y=[-64.366600,81.702303] mm;
footprint **291.041039 × 146.068903 mm**, versus #198 total width
**-0.283212 mm**, depth **+0.899622 mm**.

| Tray | XY mm | With 5 mm brim XY mm | XY delta vs #198 mm | Raw segments #198 / R2 / R3 / R4 |
| --- | --- | --- | --- | --- |
| left | 149.020519 × 146.068903 | 159.020519 × 156.068903 | -0.141606 × +0.899622 | 37 / 781 / 3597 / 1037 |
| right | 142.020519 × 146.068903 | 152.020519 × 156.068903 | -0.141606 × +0.899622 | 37 / 764 / 3580 / 1020 |

Both trays fit the 220 × 220 mm bed including 5 mm brim. **8 design
primitives per tray**: one south quadratic sweep, two R5 circular fillets,
one unchanged north quadratic portion, four straight segments including
seam. Round 3 required 13 primitives when its six spline spans were counted
separately; #198 used 37 straight segments per tray. Sampling uses 512
chords per quadratic and 128 per R5 fillet. Maximum chord-deviation bounds:
south 0.000003808 mm; north 0.000036441 mm; fillets 0.000111074 mm.
The shelf upper bound is for the consumed sampled perimeter; adding the
maximum chord bound covers its ideal-curve counterpart as well.

Evidence in `hardware/case/issue-228-outline/`:

- `17mm-outline-overlay.png`: assembled #198 dashed, round 3 faint, round 4 solid.
- `17mm-south-edge-zoom.png`: calm sweep against stepped #198 outline and unchanged pocket, with shelf witnesses.
- `17mm-outline.json`: all round polygons, constraints, curvature, shelf and distance witnesses.
- `17mm-shelf-profile.csv`: full 20,001-row dense shelf profile.
- `17mm-north-center-zoom.png`: unchanged round-3 north/USB evidence.

README reproduces the active 2D gate. Historical `round2_outline.py` and
`round3_outline.py` are byte-identical to their respective committed active
modules; round 1 remains available as `round1_outline()`. The gate regenerates
all three historical polygons and writes them beside the round-4 polygon.
Historical complete round-3 evidence/script remain in commit `078b1e35`;
round-2 evidence/script remain in `d720f5e9`.

The active 2D run passes containment, walls, all boards, 0 curvature sign
changes, tangencies, front angles, area guideline, north/USB equality,
CSV/transform consistency and bed fit. **T3 remains a reported conflict**
with a necessary 15.643664 mm convex lower bound; no 13 mm pass is claimed.
Both updated PNGs were visually inspected. Source syntax and Git whitespace
checks pass. `base.py`, `generate.py`, `details.py`, `verify.py`, inputs and
all interior geometry remain unchanged from round 3. Only the active 2D
outline and approval evidence changed.

**STOP at the 2D gate.** Phase B must await separate dispatch after the
PMO/PO resolves the shelf trade-off and approves the silhouette. Phase B
will consume round 4 via `outline.proposed_outline()`. Separate 16 mm and
17 mm solid/clearance checks, sampled BRep quality, front ring masks,
fasteners/harness/rack clearances and provisional USB alignment remain
pending. No push or PR; local commit uses
`GIT_DIR=./.issue228-runtime/git`, branch `issue-228-case-outline`.

## Phase B — completed production case, 2026-11-12

The PO approved ROUND 4 on 2026-11-12 and accepted its 17 mm shelf trade-off. This user dispatch authorizes Phase B and supersedes the historical approval/STOP language above. Production data is `hardware/case/issue-228-final/`. Both pitches pass the complete #198 verification suite and the added 2D/3D audits. No unresolved 3D design blocker was found. No push or PR.

### Scope and unchanged interior

The production tree mirrors #198: inputs, generator, and separate 17mm/16mm output directories. All 13 input files are byte-identical copies. For EACH pitch, the following complete metadata structures compare exactly to its own #198 final data: parameters, Wing transforms, board polygons, mounts, boss checks, joints, feet, Main components, PCB clearances, storage-200mm reservations and fasteners. This checks the unchanged daughterboard seat, all 15 fixing points, harness/rack, X=3.5 mm split, splice plates, heights and hardware. `details.py` differs from #198 only in STL tessellation settings; `verify.py` retains every original assertion and adds BRep counts. The Phase A directory is unchanged.

The pocket remains the original +0.502 mm mitered union and central bay, simplified by 0.002 mm. No Fly seat rework was made. Baseline component envelopes retain their #198 design-reservation qualifications.

### Per-pitch Phase A gates and fitting

17 mm preserves the approved coefficients exactly; its sampled polygon has **0 mm Hausdorff deviation** from the active Phase A module. For 16 mm, the generator reconstructs its own Wing envelope, side supports, cavity, north controls and bridge, then runs the same SLSQP minimum-area quadratic/R5 fitting family, wall/convexity constraints, 128-chord fitting resolution and 512-chord final quadratic sampling as Phase A. The initial coefficients are a warm start in that pitch’s envelope frame, never copied 17 mm XY coordinates. Bounds are local to that seed. Final 16 mm solve: **optimization terminated successfully, 17 iterations**, full fitting polygon area 28,195.155921 mm². Its full-pocket and final dense sampled gates pass independently. USB is derived from each outline and the original seat.

| 2D check | 17 mm | 16 mm |
| --- | --- | --- |
| Pocket outside perimeter (mm²) | 0.0 | 0.0 |
| Each of 4 PCB +0.502 clearance envelopes outside (mm²) | 0 / 0 / 0 / 0 | 0 / 0 / 0 / 0 |
| Minimum enclosing wall (mm) | 2.000000000 | 2.000000000 |
| South curvature sign changes; sign | 0; strictly negative | 0; strictly negative |
| Endpoint fillet radius (mm) | 5 / 5 | 5 / 5 |
| Maximum sampled shelf (mm) | 16.801254538 | 16.844820445 |
| Shelf sampling upper bound (mm) | 16.804644979 | 16.848058845 |
| Profile samples per wing | 20,001 | 20,001 |
| Added raw outline area vs legacy (mm²) | 2994.309578112 | 2593.417082246 |

The 16 mm shelf is 0.043566 mm wider than the accepted 17 mm maximum. Both exceed the historical 13 mm shelf allowance; **no 13 mm pass is claimed**. The requested Phase B report treats shelf as the accepted trade-off, with no hidden geometry adjustment. The raw outline added-area metric above excludes splice-footprint union arithmetic; the historical Phase A final-footprint value is 2,981.489903 mm². Wall values differ from 2 mm only by <3e-14 mm arithmetic roundoff. The intentional seam and above-rim USB opening are excluded from this enclosing-wall metric, as in Phase A.

17 mm shelf maximum witness: perimeter (-110.754619961, 32.533296758) → PCB (-111.885328091, 15.770133180); south-path arclength 50.537913699 mm. Full profiles and fitted controls are in `17mm/shelf-profile.csv` and `outline-check.json`.

16 mm shelf maximum witness: perimeter (-138.323554967, -1.524402888) → PCB (-123.154391545, 5.799834746); south-path arclength 0.375654367 mm. Full profiles and fitted controls are in `16mm/shelf-profile.csv` and `outline-check.json`.

### Full verify.py suite

| Check / baseline limit | 17 mm | 16 mm |
| --- | --- | --- |
| Full suite | PASS | PASS |
| Input SHA and export SHA mismatches | 0 | 0 |
| Printed parts valid after STEP reload; solids each | 5/5; 1 | 5/5; 1 |
| STL binary structure, distinct triangle vertices, closed manifold | 5/5 pass; 0 nonmanifold edges | 5/5 pass; 0 nonmanifold edges |
| STL volume relative error <0.001 (maximum) | 0.000218194 | 0.000241718 |
| Assembly solids | 114 | 114 |
| Broadphase assembly candidate pairs | 207 | 207 |
| Unexpected assembly interference | 0 detected overlaps / 0 detected mm³ | 0 detected overlaps / 0 detected mm³ |
| Designed mating contacts above reporting cutoff | 0 | 0 |
| Mount inverse-transform error (mm) | 1.00485917356e-14 | 7.94410929039e-15 |
| Expected fixing identifiers; bosses with material; open pilots | 15 / 15 / 15 | 15 / 15 / 15 |
| Palm mask ∩ high wall (mm²) | 0.0 | 0.0 |
| Keycap mask → upper wall, >=0.25 mm | 0.250000000 | 0.250000000 |
| Main component pairs / overlap failures | 1711 / 0 | 1711 / 0 |
| Minimum Main gap, >=0.3 mm | C27–C28: 0.300000000 | C27–C28: 0.300000000 |
| Baseline reported Wing underside→floor reservation (mm) | 4.6 | 4.6 |
| Brim envelope <=220×220 and Z<=250 mm | 5/5 pass | 5/5 pass |

The original assembly numerical cutoffs remain unchanged: broadphase separation <=1e-6 mm is skipped; a positive intersection >1e-4 mm³ is reported as interference. Thus “0” is the baseline CAD acceptance result at that resolution, not a stronger exact-arithmetic claim. Keycap/spacing comparisons retain the original 1e-8 mm numerical allowance. The 4.6 mm underside entry is the baseline declared reservation, not a newly measured physical component qualification.

All 15 identifiers checked at BOTH pitches: Main H1/H2/H3; UDB MH1/MH2/MH3/MH4; left Wing H1/H2/H3/H4; right Wing H1/H2/H3/H4. Every boss has material at the specified wall probe and an open pilot. Boss top Z=10, pilot diameter=1.7 mm; Wing/Main bosses Ø4.5, UDB Ø3.5 mm. Parameters remain floor 2, PCB bottom 10, Wing/Main PCB thickness 1.2, UDB thickness 1.6, low rim 11.2, upper wall top 15.2 mm.

### Harness, components, storage and PCB checks

| Pitch | Route | Non-mating Main components checked; minimum gap mm | Keycap gap mm | Case gap mm | PCB gap mm |
| --- | --- | --- | --- | --- | --- |
| 17 | left | 58; U4 2.295776671 | 9.008036199 | 6.582632785 | 7.000000000 |
| 17 | right | 58; C28 3.123040652 | 9.008036199 | 6.582632785 | 7.000000000 |
| 16 | left | 58; U4 2.295776671 | 7.888015920 | 6.317610685 | 7.000000000 |
| 16 | right | 58; C28 3.123040652 | 7.888015920 | 6.317610685 | 7.000000000 |

All harness gaps exceed the original >0.2 mm threshold. Each route is 99.274845254 mm in 3D, with 30 mm service allowance totaling 129.274845254 mm, leaving 100.725154746 mm nominal slack on a 200 mm cable. Radius=5 mm, endpoint Z=18.2, cruise Z=23.2 mm; Wing GH endpoints remain (±27,−41). Full individual component distances are retained in each `dimensions.json`, with no excluded non-mating component.

| Pitch | 200 mm storage side | Loop length after 30 mm allowance mm | Keycap gap mm | Main gap mm |
| --- | --- | --- | --- | --- |
| 17 | left | 70.725154746 | 13.283856512 | 36.761900172 |
| 17 | right | 70.725154746 | 13.283856512 | 36.761900172 |
| 16 | left | 70.725154746 | 12.872091806 | 36.761900172 |
| 16 | right | 70.725154746 | 12.872091806 | 36.761900172 |

The service-loop STEP remains a separate reservation, not another connected cable. The rack and its socket, eight feet, 15 PCB screws/washers and four splice screws are unchanged and present in the assembly interference checks.

| Pitch | PCB A | PCB B | Gap mm | Overlap mm² |
| --- | --- | --- | --- | --- |
| 17 | main | wing_left | 1.999999308 | 0.000000000 |
| 17 | main | wing_right | 1.999999904 | 0.000000000 |
| 17 | main | udb | 22.017949000 | 0.000000000 |
| 17 | wing_left | wing_right | 2.000000000 | 0.000000000 |
| 17 | wing_left | udb | 4.000000000 | 0.000000000 |
| 17 | wing_right | udb | 4.000000000 | 0.000000000 |
| 16 | main | wing_left | 1.999999308 | 0.000000000 |
| 16 | main | wing_right | 1.999999904 | 0.000000000 |
| 16 | main | udb | 22.017949000 | 0.000000000 |
| 16 | wing_left | wing_right | 2.000000000 | 0.000000000 |
| 16 | wing_left | udb | 4.000000000 | 0.000000000 |
| 16 | wing_right | udb | 4.000000000 | 0.000000000 |

### Print envelopes, BRep and STL quality

| Pitch | Printed part | XYZ mm | XY with 5 mm brim mm | Faces / edges | STL triangles | Volume error |
| --- | --- | --- | --- | --- | --- | --- |
| 17 | splice-1 | 28.000000 × 16.000000 × 4.200000 | 38.000000 × 26.000000 | 12 / 24 | 8068 | 0.000019866% |
| 17 | splice-2 | 28.000000 × 16.000000 × 4.200000 | 38.000000 × 26.000000 | 12 / 24 | 8068 | 0.000019871% |
| 17 | tray-left | 149.020524 × 146.068992 × 15.200000 | 159.020524 × 156.068992 | 305 / 824 | 63230 | 0.021819444% |
| 17 | tray-right | 142.020524 × 146.068992 × 15.200000 | 152.020524 × 156.068992 | 301 / 824 | 55970 | 0.021708461% |
| 17 | cable-rack | 64.000000 × 15.000000 × 20.200000 | 74.000000 × 25.000000 | 48 / 135 | 2216 | 0.000443968% |
| 16 | splice-1 | 28.000000 × 16.000000 × 4.200000 | 38.000000 × 26.000000 | 12 / 24 | 8068 | 0.000019866% |
| 16 | splice-2 | 28.000000 × 16.000000 × 4.200000 | 38.000000 × 26.000000 | 12 / 24 | 8068 | 0.000019871% |
| 16 | tray-left | 142.317998 × 139.557564 × 15.200000 | 152.317998 × 149.557564 | 307 / 830 | 63178 | 0.023208506% |
| 16 | tray-right | 135.317998 × 139.557564 × 15.200000 | 145.317998 × 149.557564 | 303 / 830 | 55918 | 0.024171840% |
| 16 | cable-rack | 64.000000 × 15.000000 × 20.200000 | 74.000000 × 25.000000 | 48 / 135 | 2216 | 0.000443968% |

Every printed part is one valid solid on STEP reload and every STL is closed with 0 nonmanifold edges. The right-tray maximum final volume error is 0.024171840% (16 mm), below 0.1%. No wall, height, fixing point or interior part was changed to achieve this.

| Additional STEP | 17 mm faces / edges / solids | 16 mm faces / edges / solids |
| --- | --- | --- |
| assembly | 2037 / 5181 / 114 | 2041 / 5193 / 114 |
| harness | 22 / 38 / 2 | 22 / 38 / 2 |
| storage-200mm | 1168 / 3492 / 2 | 1168 / 3492 / 2 |

All additional STEP compounds reload as valid. Harness contains two cables; storage contains two reservation solids. The complete assembly tessellates successfully for the PNGs.

The original sampled 17 mm integrated base was valid but had **2,545 faces / 7,527 edges**, STEP **10,307,237 bytes**. This was disproportionately heavy for the eight-primitives-per-tray outline. Exact native curves reduce that integrated base to **509 faces / 1,417 edges**, **1,897,179 bytes**. Only outer sampled runs are replaced: exact quadratic Béziers and R5 circular arcs, using the same underlying curves across height layers. Interior straight edges are retained. Clipped outer endpoints are projected by at most the tiny sampled chord error; final manufactured perimeter error is measured below. No sampled-build mesher failure is claimed.

Rejected intermediate results are recorded explicitly: the initial independently approximated B-spline representation yielded a **515-face / 1,429-edge invalid STEP on reload** despite pre-export validity; it was replaced by shared exact curves. At baseline STL tolerance 0.02 mm / angular 0.1 rad, the 16 mm right tray failed volume agreement at **0.001176657098 relative = 0.117665710%**, exceeding 0.1%. Final exports use **0.005 mm / 0.025 rad** and pass the unchanged verifier. These were representation/export failures; no approved silhouette or interior dimensions were tuned to suppress a design interference.

Independent-fit development also rejected infeasible optimizer outputs, including a -2 mm south-distance constraint result, and a poor raw-envelope initialization with 26.864932 mm shelf / 5,953.869064 mm² added area. Neither is used. The delivered 16 mm solution is the converged full-pocket SLSQP fit documented above and re-derived by both the generator and gate. An audit initially used X=0 instead of the existing seat’s X=-0.002 mm and falsely counted 0.023685727 mm² obstruction at the slot shoulder; the corrected audit derives the seat datum and detects zero obstruction.

### Actual 3D USB opening and intact material below

USB remains W12 × H4 mm, open top over **Z=11.2..15.2 mm**, centered at the unchanged seat **X=-0.002 mm** (bounds X=-6.002..5.998). `check_3d.py` sections the exported trays, including inner wires, not a 2D generator surrogate. At Z=13.2 the entire slot corridor to Y=-34 has **0 mm² blocking material** at both pitches. At three wall witnesses per pitch, material is present at Z=1/2.1/10/11.19 and absent at Z=11.21/13.2/15.19. The upper wall is prismatic in this band; the opening has no roof.

| Pitch | Below-slot wall depth at center mm | Below-slot depth across five X stations mm | Intact floor in corridor mm² | Intact low rim at Z10.5 mm² |
| --- | --- | --- | --- | --- |
| 17 | 18.061921000 | 18.061921000–18.090796000 | 249.882859264 | 216.858859264 |
| 16 | 16.690736000 | 16.690736000–16.717014000 | 233.418229773 | 200.394229773 |

17 mm upper-wall shoulder at X=-6.012000: total solid wall crossed 11.842989000 mm; bands Y=[-54.842989,-45.000000], thickness 9.842989000 mm; Y=[-38.752000,-36.752000], thickness 2.000000000 mm.

17 mm upper-wall shoulder at X=6.008000: total solid wall crossed 11.842951000 mm; bands Y=[-54.842951,-45.000000], thickness 9.842951000 mm; Y=[-38.752000,-36.752000], thickness 2.000000000 mm.

16 mm upper-wall shoulder at X=-6.012000: total solid wall crossed 10.469190000 mm; bands Y=[-53.469190,-45.000000], thickness 8.469190000 mm; Y=[-38.752000,-36.752000], thickness 2.000000000 mm.

16 mm upper-wall shoulder at X=6.008000: total solid wall crossed 10.469155000 mm; bands Y=[-53.469155,-45.000000], thickness 8.469155000 mm; Y=[-38.752000,-36.752000], thickness 2.000000000 mm.

The shoulder measurements distinguish the high north band and original UDB wall from the continuous, deeper low rim below. The slot clears both upper-wall bands. The original provisional seat alignment remains a future Fly task.

### Exported 3D silhouette and PNGs

| Pitch | Measured max perimeter deviation mm | Conservative sampling bound mm | Actual assembly top view |
| --- | --- | --- | --- |
| 17 | 0.000111547 | 0.010111547 | `17mm/assembled-top.png` |
| 16 | 0.000111437 | 0.010111437 | `16mm/assembled-top.png` |

The 17 mm reference is the exact approved Phase A sampled perimeter; 16 mm is its own independently derived counterpart. Both include unchanged splice-floor reinforcement footprints. Perimeter checks section actual exported tray STEP at Z=1, use only external floor wires to exclude screw bores, sample edges at <=0.02 mm spacing and snap to a 1e-6 mm grid. The conservative bound is well below **0.05 mm everywhere**. The PNGs tessellate every actual assembly STEP leaf and paint projected triangles in height order; the dashed line is the approval reference. Both PNGs were visually inspected. `review.svg` remains the inherited 2D review drawing and is not substituted for the required 3D PNG.

### Export inventory and reproducibility

`17mm/` (21 files): `3d-check.json`, `assembled-top.png`, `assembly.step`, `cable-rack.step`, `cable-rack.stl`, `dimensions.json`, `exports-sha256.json`, `harness.step`, `outline-check.json`, `review.svg`, `shelf-profile.csv`, `splice-1.step`, `splice-1.stl`, `splice-2.step`, `splice-2.stl`, `storage-200mm.step`, `tray-left.step`, `tray-left.stl`, `tray-right.step`, `tray-right.stl`, `verification.json`.

`16mm/` (21 files): `3d-check.json`, `assembled-top.png`, `assembly.step`, `cable-rack.step`, `cable-rack.stl`, `dimensions.json`, `exports-sha256.json`, `harness.step`, `outline-check.json`, `review.svg`, `shelf-profile.csv`, `splice-1.step`, `splice-1.stl`, `splice-2.step`, `splice-2.stl`, `storage-200mm.step`, `tray-left.step`, `tray-left.stl`, `tray-right.step`, `tray-right.stl`, `verification.json`.

Each pitch has STL+STEP for all five printable parts, plus the baseline assembly/harness/storage STEP compounds. Purchased hardware and electronics are reference solids in assembly STEP, following #198 organization. Export SHA-256 manifests cover STEP, STL, JSON audit/dimension files, CSV shelf profile, SVG and PNG (excluding the manifest itself and verifier output).

Reproduction commands are in `hardware/case/issue-228-final/README.md`. CAD venv is local at `.issue228-runtime/cad-venv/`, reading existing CAD packages and local `.issue228-runtime/pydeps/`; scratch, caches, logs and MPL config remain under `.issue228-runtime/`. No CAD packages or runtime data were written to `/tmp` or shared tool directories. Final source syntax, input identity, source/documentation Git whitespace checks and full verification checks pass. A whole-export whitespace scan reports the native STEP writer’s trailing spaces and preserved input CSV CRLFs; these machine-export bytes are retained, and all 13 authoritative input copies remain byte-identical. Historical Phase A files are untouched.

Remaining deviations: accepted shelf trade-off and unchanged provisional USB/seat qualification only. **No unresolved Phase B 3D blocker.** Local branch is `issue-228-case-outline`, using `GIT_DIR=./.issue228-runtime/git`; commit only, no push/PR.
