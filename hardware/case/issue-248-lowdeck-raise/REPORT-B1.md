# Issue #248 — B1 dimensioned mated GH clearance screen

2026-11-14. **The GH item is closed for the PO-authorized drawing-bounded
B1 screen:** J2/left and J3/right each have **−1.350000 mm** minimum vertical
underside gap against the unmodified B0 roof. The minimum relief for +0.30 mm
is **1.650000 mm**; a pocket leaves **0.350000 mm** skin and fails the 2.00 mm
yardstick. A closed local blister needs **ceiling Z13.200000 / top Z15.200000**,
maximum **+1.650000 mm** above the existing surface. This improves the B0
reservation's −1.55 / +1.85 screen by **0.20 mm**, without changing the verdict.

This is a dimensioned model of the seated header and plug **using drawing
bounds wherever local detail is undimensioned**, as authorized for B1. Exact
numerical results below mean exact calculations on that explicitly bounded
model. In particular, the reported Common volume is an **upper bound on the
physical mouldings' intersection volume**, not a claim to have reconstructed
unpublished latch/cavity geometry. B0 remains a historical partial report;
this report supersedes its GH source blocker only. No Phase B or production
CAD is performed. Boards, plate and baseline roof are unchanged. All Z remain
provisional on Junana **q=1.50 mm**.

Deliverables:

- [Both seated GHs in assembly frame](b1/mated-gh-assembly-frame.step).
- [Named header and plug/latch constituent bounds](b1/mated-gh-component-bounds.step)
  for inspection; these overlap in the seated zone and are not summed for volume.
- [J2 / left model](b1/J2-mated-gh.step), [J3 / right model](b1/J3-mated-gh.step).
- [Unchanged roof with GH models and bounded outlet faces](b1/roof-gh-b1.step).
- [Worst-point sections, both sides](b1/section-gh-worst-b1.png).
- [Dimensions, poses and results](b1/clearances-b1.json),
  [independent exported-STEP verification](b1/verification-b1.json).
- [J2 roof Common](b1/J2-roof-intersection.step),
  [J3 roof Common](b1/J3-roof-intersection.step).

## Official source drawings and dimension register

The issue-235 and issue-240 connector `SOURCES.md` files and their adjacent
source PDFs were inspected first. The following JST documents supply every
connector size. KiCad supplies placement and the footprint datum only.

**D1:** JST, *GH connector*, current manufacturer catalog,
[eGH.pdf](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), existing repository
copy [JST-current-eGH.pdf](../../kicad/qualification/issue-240-main-rev7/connector/JST-current-eGH.pdf).
Figures are identified by page, printed section heading and view below; the
catalog has no numbered figure IDs. The current repository PDF was inspected
visually as well as through the manufacturer's web PDF reader. Local Poppler
omits its Japanese-CMap text; MuPDF renders the dimension labels correctly.

**D2:** JST UK, *GH connector*, archived manufacturer catalog dated 14/7/05,
[manufacturer drawing distributed by DigiKey](https://media.digikey.com/pdf/Data%20Sheets/JST%20PDFs/GH%20Series.pdf),
existing repository copy [eGH-distributor-copy.pdf](../../kicad/qualification/issue-240-main-rev7/connector/eGH-distributor-copy.pdf).
Pages 3 “SMT type header / Side entry type” and 4 “Assembly layout / Side entry
type” corroborate the header and seated assembly bounds. D1 governs this model.
No distributor-created geometry or third-party CAD sizes are used.

| Feature / parameter | Dimension mm | Official document and exact figure | Treatment |
|---|---:|---|---|
| Circuit pitch | 1.25 | D1 p3, Housing front view and Header / Side entry front view | Dimensioned; no individual cavities invented |
| Pin 1–14 span A | 16.25 | D1 p3, Housing and Header fourteen-circuit table rows | Dimensioned; (14−1)×1.25 |
| Header overall width B | 20.75 | D1 p3, Header / Side entry front view and SM14B-GHS-TB row | Drawing-bounded across all local X, including end reinforcement envelope |
| Header body axial depth | 4.05 | D1 p3, Header / Side entry right-hand side view, upper horizontal callout | Drawing-bounded body |
| Header body height | 4.25 | D1 p3, same side view, right vertical callout | Drawing-bounded body |
| Header body stand-off above PCB mounting surface | 0.10 | D1 p3, same side view, lower vertical callout | Body bottom +0.10; body top +4.35 |
| Header solder-tail projection at back | 0.80 | D1 p3, same side view, right horizontal callout | Recorded, not extruded: undimensioned metal cross-section; below roof contact zone |
| Plug overall width B | 18.75 | D1 p3, Housing front view and GHR-14V-S table row | Drawing-bounded including outer latch features |
| Plug tip-to-wire-end length | 5.70 | D1 p3, Housing side view, left vertical callout; rotates into insertion axis for SM header | Drawing-bounded |
| Plug overall transverse height in seated side-entry pose | 4.15 | D1 p3, Housing side view, upper horizontal callout | Drawing-bounded, includes latch; not a latch-step dimension |
| Fully seated assembly axial extent, header rear to plug wire end | (7.15) | D1 p2, PC board layout and Assembly layout / Side entry, lower assembled view, upper horizontal callout | **Reference drawing bound**, not a maximum tolerance specification |
| Fully seated assembly above PCB mounting surface | (4.35) | D1 p2, same assembled side view, right vertical callout | **Reference drawing bound**, independently agrees with 4.25+0.10 |
| Applicable insulation OD | 0.76–1.00 | D1 p1 Specifications and p2 Contact table | Source context only; no wire solids added in B1 |
| Seated plug tip from header rear | 1.45 | Derived: D1 p2 seated extent 7.15 minus D1 p3 plug length 5.70 | No guessed insertion depth |
| Plug lower bound above mounting surface | 0.20 | Derived bound: D1 p2 assembly height 4.35 minus D1 p3 transverse plug extent 4.15 | Conservative top-aligned bound, not a dimensioned latch/plug mounting offset |

The isolated part downloads were also checked at JST's
[GH product page](https://www.jst-mfg.com/product/index.php?lang=2&series=105).
The [SM14B-GHS-TB 2D link](https://www.jst-mfg.com/product/index.php?doc=4&filename=SM14B-GHS-TB.pdf&series=105&type=10)
returns a company/contact registration form; the corresponding GHR link returns
the catalog page. No identity was submitted and no unseen dimensions were used.
D1/D2 suffice for the authorized bounded model.

## Seated model, latch, outlet and registration

Use local **u** along the pin row and **v** from header rear toward the mating
face / exiting wires. Coordinates below are relative to the footprint origin;
local z is above the PCB mounting surface.

| Model constituent | u range | v range | z range | Reason |
|---|---|---|---|---|
| Header body bound | −10.375…+10.375 | −1.600…+2.450 | +0.100…+4.350 | D1 header bounds; F.Fab rear datum −1.6 from existing Rev7 footprint |
| Seated plug including latch bound | −9.375…+9.375 | −0.150…+5.550 | +0.200…+4.350 | Tip = rear+1.45; wire end = rear+7.15; transverse bound fits within assembly extent |
| Wire outlet bounded face | −9.375…+9.375 | +5.550 | +0.200…+4.350 | Entire rear face retained; no guessed outlet holes, bore centers or wire axis |

The latch's step heights, ramp angles, hook thickness, width and axial break
positions are **not dimensioned in D1/D2**. Consequently its profile remains
inside the **entire plug drawing bounding box**, labelled as such in STEP
context, section and JSON. The same policy retains header openings/end details
and plug cavities inside their body bounds. The plug and header boxes overlap
in the seated insertion region: the exported measured solids are their
**Boolean union**, so no overlap is double-counted. This union does not imply
a solid real connector interior. The outlet faces are zero-volume reference
faces in `roof-gh-b1.step`; they do not contribute intersection volume.

The model reads the actual frozen Rev7 board
`issue-240-main-rev7/inspection/final/main.kicad_pcb`: J2 is native
(82.897854,112.075001), −120°; J3 is (117.102146,112.075001), +120°,
both F.Cu. Assembly coordinates subtract (100,70), retaining native Y's
sixth decimal (the B0 reservation generator rounded Y to 42.075000).

| Side | Ref | Assembly footprint origin XY mm | Native angle |
|---|---|---|---:|
| Left | J2 | (−17.102146,42.075001) | −120° |
| Right | J3 | (+17.102146,42.075001) | +120° |

The exact B0 pose convention is preserved:
`X=x+u*cos(a)+v*sin(a); Y=y−u*sin(a)+v*cos(a)`.
PCB underside **Z7.35**, 1.20 mm board, mounting surface **Z8.55**.
Header body bottom Z8.65, plug bound bottom Z8.75, assembly bound top **Z12.90**.
There is no additional +6 or −8.65 translation: these are already lowered
assembly coordinates. The standalone GH STEP contains both sides in this frame.
The footprint −1.6 datum and PCB pose/thickness are study inputs, not connector
sizes inferred from non-JST sources.

## Exact calculation against the unmodified roof

The solver imports **`b0/roof-b0.step`**, without rebuilding or cutting it.
Its eight valid solids retain volume **32001.277514241505 mm³** and their SHA256.
Minimum gap uses the B0 definition: minimum **vertical underside minus obstacle
height**, not Euclidean penetration depth. Each roof region's affine underside
is optimized over its intersection with the actual model footprint. Independent
STEP replay constructs vertical clipping prisms from the imported roof's eight
underside BRep faces and evaluates their rotated exact support bounds. This
replay uses the STEP roof faces, not the input GeoJSON or a sampled mesh.
OCCT Common computes the intersection of the fused GH bound with that roof.

| Side | Raw vertical gap mm | Outer-surface gap mm | Exact bounded-model Common mm³ | Pocket depth mm | Remaining skin mm |
|---|---:|---:|---:|---:|---:|
| J2 / left | **−1.350000** | +0.650000 | **149.430951** | **1.650000** | **0.350000** |
| J3 / right | **−1.350000** | +0.650000 | **149.430951** | **1.650000** | **0.350000** |

The worst set includes the header's top beneath the low south roof, not just
one corner or the slope boundary. Representative worst points used in the PNG:

- J2: **(−18.805169,44.174723,12.900000)**; roof directly above at Z11.55.
- J3: **(+18.805169,44.174723,12.900000)**; roof directly above at Z11.55.

Both are inside the header bound and the low-south roof footprint. The JSON also
records equivalent worst witnesses at the slope toe Y38.514430874470. Tiny
floating-point differences select the toe in the primary minimum record;
the low-south region has exactly the same analytical minimum. OCCT tolerance
is approximately 1e−7 mm; independent replay agrees within 2e−7 mm. Full-volume
figures are exact for the stated drawing-bound solids only; physical cavities
can reduce their values.

## Minimum local measure and comparison

Required removal/lift is `0.30 − (−1.35) = 1.65 mm`. A pocket would leave
`2.00 − 1.65 = 0.35 mm` and therefore fails the **2.00 mm vertical skin**
yardstick. The minimum closed flat ceiling is `12.90 + 0.30 = Z13.20`;
with the same vertical skin its top is **Z15.20**.

On the unchanged slope, let
`S(Y)=24.65−0.303454142020910*(Y−1.935592549583419)`.
Required rise above that surface over the GH footprint is
**`max(0,15.20−S(Y))`**. It reaches **1.65 mm** at the toe and remains 1.65
above the low Z13.55 surface. For example at Y36 it is 0.886986 mm; the
zero-rise crossing is Y33.077036. Thus a slope-only section must not hide the
governing low-south part. Any transition walls must remain outside the
connector's 0.30 mm clearance envelope. No pocket/blister/transition is added
to the delivered baseline; these are minimum dimensional measures only.

| Screen | Gap mm | Relief for +0.30 mm | Pocket skin mm | Closed ceiling / top Z mm |
|---|---:|---:|---:|---|
| B0 #246 reservation, 20.75×7.15×4.55 | −1.55 | 1.85 | 0.15 | 13.40 / 15.40 |
| B1 JST dimensioned seated bounds | **−1.35** | **1.65** | **0.35** | **13.20 / 15.20** |

The improvement is 0.20 mm, because the 4.55 reservation height is replaced
by the JST 4.35 seated bound. Width/axial occupancy also improve: the bound
Common falls by 31.146813 mm³ per side from the reservation's 180.577764.
This volume change includes different constituent widths and the small retained
Rev7 placement precision; it is not attributed solely to height.

## What remains unmodelled and effect on the verdict

**Unsourced local dimensions:** latch ramp/steps/hook/thickness/width and their
break positions; header and plug cavities, chamfers, radii, wall thicknesses;
individual wire outlet centers/heights/bores; contact and solder-tail detailed
cross-sections; production tolerances for the reference seated dimensions.
The plug's exact independent vertical placement within the assembly is not
called out; B1 uses the conservative top-aligned bound described above. No
numerical values were invented for these features.

These omissions **can change physical intersection volume, the detailed relief
footprint and an exact physical worst-point location**. Those quantities must
not be represented as physical moulding-level results. They do **not change
the nominal clearance verdict or the necessary vertical relief screen**: the
side-entry header itself has a 4.25 mm body on a 0.10 mm stand-off, and its top
rail lies beneath low-south roof in this pose, independent of the plug/latch
internal profile. The header center/rear is already south of the slope toe.
Even deleting the entire plug bound leaves header-bound roof intersection
**91.906058 mm³ per side** and the same −1.35 minimum. Internal voids cannot
raise the unchanged roof or lower the drawing's header top rail. Full seating
keeps all latch detail within the D1 assembly reference envelope.

A drawing reference bound is **not a certified production maximum**. Unspecified
as-built tolerances, solder seating, q and harness dress could change final
clearance and must be measured/qualified before production. This B1 conclusion
is limited to the PO's dimensioned nominal/drawing-bound study. B0's separately
cleared wire sweeps are retained as evidence; no new wire route or unseated
latch/service motion is evaluated.

## Verification and reproduction

[Independent replay](b1/verification-b1.json) passes: both exported GH BReps
valid; both exact support minima −1.350000; both Common volumes agree within
1e−6 mm³; source hashes unchanged. A scratch uniform ceiling lift of 1.65 mm
produces zero Common and **+0.300000 mm** true BRep distance on both sides.
That replay tests the ceiling height, not local transition walls. Both actual
OCCT sections in the PNG were visually inspected.

Run from repository root:

```bash
export TMPDIR="$PWD/.issue248-runtime"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/study-b1.py
/home/hatch/workspace/tools/cad-venv/bin/python hardware/case/issue-248-lowdeck-raise/verify-b1.py
/usr/bin/python3 hardware/case/issue-248-lowdeck-raise/plot-b1.py
```

B0's existing build123d/OCP, Shapely and sexpdata environment is reused.
All runtime/cache/scratch stays in `.issue248-runtime/`. The B1 manifest binds
this report, scripts, outputs and input hashes. B0 and all A–A4 artifacts remain
byte-for-byte unchanged; the runtime-git commit adds only B1 artifacts.
