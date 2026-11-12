# Issue #228 — Phase A outline approval gate

2026-11-12. **Proposal complete; awaiting PO approval. Phase B is not authorized by this report.**

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
