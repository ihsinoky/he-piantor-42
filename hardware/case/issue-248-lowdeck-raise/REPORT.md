# Issue #248 — REPORT A: low deck with raised keyless regions

2026-11-14 · 17 mm pitch primary · Phase A review package only.

**Conditional Wing plate-top minimum: Z13.55 mm**, bound by the underside
mated GH envelope, with the retained 2 mm floor and declared clearance budgets.
This is a stack lower bound and proposed design target, **not a qualified fitted
assembly minimum**. The harness must be rerouted to attain it. The last qualified
assembly remains D-041, Z22.2. No production CAD, STEP, manufacturing package,
board change, or decision amendment is made here.

**Nominal raised/keytop plane: Z24.65 = plate +11.10 mm**, conditional on the
explicit Junana mounting assumption below. No source located establishes the
actual installed Junana height or full-press skirt clearance. Those physical
conditions remain unresolved at the PMO gate; this report does not mark them PASS.

## Inputs, scope and coordinates

Read the [Issue snapshot](sources/issue248.json) first, then
[D-037–D-041](../../../docs/decisions.md), the adopted
[#246 report](../issue-246-delta6-tuning/REPORT.md) and 17 mm measurements,
assembly index, service/gate data; the
[#232 Delta=0 report](../issue-232-final/REPORT.md), dimensions, component
reservations and plate aperture tables; and
[#235 round 2](../../kicad/qualification/issue-235-wing-round2/REPORT.md)
and [round 3](../../kicad/qualification/issue-235-wing-round2/REPORT3.md).
Round 3 closes the 16-left electrical failure recorded in round 2; D-039 adopts
all four Wing Rev.4 variants. D-040 supersedes round 2's Main Rev.6 with Rev.7.
No round-2 failed routing trial is being used as an adopted harness.

Dimensions are mm. Assembly X right, **Y south**, Z up; Z0 is tray floor
underside, Z2 nominal floor top. Feet extend below Z0, so these Z figures are not
desk-to-keytop heights. Wing-local Y points north; use the #232 transforms.
Boards retain native XY, rotation, outlines, mounting holes and components.
For this study Wing, Main and Fly mounting datums lower together by 8.65 mm
from #246 (2.65 below #232); case seats, walls and USB opening must follow.
Retaining their previous global Z positions is a different, unassessed option.

The [plan PNG](plan.png) / [SVG](plan.svg), [three sections PNG](sections.png) /
[SVG](sections.svg), [numeric tables](tables.json), and
[raised-region geometry](raised-regions.geojson) form one proposal. These are
dimensioned envelope drawings, not production solids. Section C deliberately
projects off-centre obstacles; section A is the centre X0 cut.

## 1. Deck-height lower bound

Let B be Wing PCB underside. The invariant switch/plate stack gives
`plate top = B +1.20 PCB +3.50 POM spacer +1.50 plate = B+6.20`.
Shortening that 3.50 spacer would alter the switch seating relationship; it is
not a way to lower the deck with these switches and boards.

| Constraint | Calculation / envelope | Required B | Plate-top bound |
|---|---|---:|---:|
| Hall underside including inherited reservation | floor 2 + depth 3.40 + free gap 0.50 | 5.90 | 12.10 |
| MUX + solder | 2 +1.40 +0.50 | 3.90 | 10.10 |
| Capacitors | 2 +1.00 +0.50 | 3.50 | 9.70 |
| **Mated GH header/plug, binding** | 2 +4.35 nominal +0.50 assembly allowance +0.50 free gap | **7.35** | **13.55** |
| M2×12 tie / boss root | 5.50 engagement below B, retain ≥1.20 material below screw tip | 6.70 | 12.90 |
| Six E-R posts per Wing | socket bottom 1.20, seated top B; new post length 6.15 | 7.35 target | 13.55 target |
| Floor, ledge and rim | keep floor 0…2, sockets 0.80 deep; ledge plate−1.50 | — | ledge 12.05; rim 13.55 |
| Palm band / shelf | full shelf backing, no proud screws; plate/rim coplanar | — | no independent absolute lower Z |

The component depths come from #232 `build.py` and #235's conservative
reservations, not a new physical measurement. GH 4.35 is a manufacturer reference
dimension; the additional 0.50 is the inherited engineering budget, not a JST
certified maximum. The 0.50 floor gap is retained. Binding GH reservation bottom
is Z2.50; nominal bottom is Z3.00. Hall bottom is Z3.95, leaving 1.95 above floor.
Wire exit axis becomes `B−1.60 = Z5.75`, with #235 uncertainty ±0.50; OD1 wire
bottom at worst Z4.75 gives 2.75 floor clearance. A horizontal exit does not
require adding an R5 diameter below the header: bend north/south in XY first,
then rise inside the central mass. Whether all fourteen paths can make that turn
is the main routing dependency, not an assumed free bend.

| Design | PCB underside | PCB top | Plate bottom | Plate top | Reduction from D-041 |
|---|---:|---:|---:|---:|---:|
| Current D-041 / Delta=6 | 16.00 | 17.20 | 20.70 | 22.20 | 0 |
| #232 / Delta=0 reference | 10.00 | 11.20 | 14.70 | 16.20 | 6.00 |
| Proposed conditional minimum | 7.35 | 8.55 | 12.05 | **13.55** | **8.65** |

Keep 1.50 nominal 5052-H32 plates (finished 1.45–1.51), four 3.50 POM spacers
and M2×12 ties per Wing. Tie screw stack is 0.30 washer +1.50 plate +3.50 spacer
+1.20 PCB =6.50, leaving 5.50 engagement; screw tip is Z1.85, above the retained
1.20 minimum root. Remake twelve insulating posts from 14.80 (#246) /8.80
(#232) overall to 6.15, including the existing seated peg. Root sockets retain
1.20 floor material. Boss pilots and load paths need CAD verification after
channel cutting; available screw depth alone is not a structural qualification.

Retain the complete D-037 curved south outline, solid shelf bearing, 8 mm palm
inspection strip, nominal zero step and 0.20 seam. #232 measured a 0.20 maximum
south seam at 17 mm (0.40 at 16 mm). No new fastener head enters that band.
Manufactured flatness, plate thickness and printing variation still require a
physical seam/step gauge. Lower height does not waive this requirement.

With the #246 bundle architecture retained under a Wing, a conservative radial bound reaches
Z9.5042 at the existing lower-axis Z7 (the nominal OD5 envelope reaches Z9.50). Requiring 0.50 below the PCB would instead
give B≥10.0042, plate≥16.2042 even before local Hall conflicts. Translating the
whole #246 route down 8.65 places the bundle below the floor. **The 13.55 target
therefore expressly excludes that routing architecture.** If a new fanout fails,
raise the plate to the audited routing requirement or reconsider the case floor;
do not call this minimum achieved or relax component/clearance bounds.

## 2. Keytop definition and evidence limits

The in-repo [Jade Pro specification](../../kicad/qualification/issue-194-wing-rev2/sources/jade-pro.pdf),
KS-20TF10B045NW-Y106, 2024-08-19, PDF page 7, shows housing top 11.10 above PCB
top, stem extension TT 3.50, and 5.00±0.05 PCB-top to plate-top. The resulting
**unpressed stem tip is plate+9.60**. Travel is 3.50±0.20; use 3.70 for clearance,
not an adjustable actuation setting. D-038 and #232 specify the 1.50 plate and 14 mm aperture; PDF page 8 is packaging, not a mechanical mounting drawing.

Define `q = cap highest unpressed surface − seated switch stem tip`.
Then `keytop = plate + (11.10+3.50−5.00) +q = plate+9.60+q`.
Use the highest rim/convex/homing surface for the common raised datum; a concave
dish is not one plane. This definition avoids confusing loose cap height with
installed height: loose cap height H alone is insufficient without socket
engagement and skirt datum.

The [maker's storefront](https://decentkeyboards.booth.pm/) and
[maker's profile documentation](https://github.com/hajimen/keycap_designer#junana)
confirm 17 mm pitch, MX compatibility and concave/convex options. The profile
software supplies print artwork, not a mechanical socket/height model.
[Retail listing](https://shop.yushakobo.jp/products/10754) likewise provides no
installed dimension. These were checked 2026-11-14. No defensible Junana installed
height, skirt depth or manufacturing tolerance was located. The earlier repo
15.8 square / skirt Z=plate+0.40 are **required envelopes, not measured cap data**.

For a drawable Phase A candidate **assume q=1.50**, sensitivity 0.50…2.50; thus
keytop/raise **plate+11.10 = Z24.65**, nominal pressed top Z21.15, maximum-travel
top Z20.95 before dimensional tolerances. Budget ±0.75 for the switch offset
(11.10 general ±0.40, TT 3.50 general ±0.30, 5.00±0.05) and ±1.00 for q:
provisional keytop range **Z22.90…26.40** at the target plate datum. This is an
engineering sensitivity range, not a measured or supplier-certified interval.
Do not machine the final raised height from 24.65. Measure the selected Junana
types installed on Jade Pro, replace q, and regenerate drawings. A different q
changes the roof and slope angle one-for-one; the lower deck stack is independent.

## 3. Raised-area plan and longitudinal sections

Use a detachable hollow central shell over the #246 central cover footprint plus a 20 mm wide bridge
at X−10…10 / Y−18…18 across its narrow waist, cut back around every rotated **18×18 well**. Use two independently removable
north Wing strips, clipped to the #232 full-deck silhouettes. Their south edge
follows the staggered R0 centres plus 9 mm in Wing-local north, interpolated
between columns; remove every key's well from all raised regions. The saved
GeoJSON and plan use actual #232 transforms and all 42 aperture centres, including
rotated thumbs. No infill fingers between regular keys: 18 mm wells overlap at
17 mm pitch, so they intentionally merge into open keyfield boundaries.

Raise the inner keyless Wing margins only where needed for that central bridge;
this gives a continuous roof across the former flush cover waist. Leave south
shelves/palm bands, outer side margins and thumb margins at plate
level. This keeps hands off tall edges, avoids cap/puller traps and saves printed
volume. Only the central mass and north strips have a keytop-height plateau.
Separate shell fasteners belong in keyless areas with accessible heads. Raised
parts must come off without removing Wing PCB stacks; do not reuse the old
3 mm cover spacers as if they still reached the new roof.

**Central slope starts at Y8, reaches the low plate at Y69.7**, run 61.70, drop 11.10,
angle **10.20°** for the assumed keytop. #232's transformed second row R1 spans
Y−20.98…12.86; Y8 lies within that latitude band, not at the south edge. The main
reason for continuing the slope to Y69.7 is Main's footprint through Y67.9 and
its south fasteners at Y64.4, plus accessible termination space. A short ramp
ending near Y30 would intersect the unchanged Main/GH volume. Y69.7 also leaves
the flat south palm areas outside the central footprint untouched. The toe is
within the existing cover's south extent; no case outline extension is proposed.

At a nominal 2 mm roof skin the slope underside is Z22.65 at Y8, 20.11 at Y22.1,
14.76 at Y51.86, 12.50 at Y64.4, and 11.87 at Y67.9. Lowered Main GH's envelope
tops at Z13.10 through Y51.86, giving **1.66 mm** vertical margin at the limiting
south end of that projected box. Main screw top at Y64.4 becomes Z10.65,
giving **1.85 mm**. At the lower keytop sensitivity limit these margins approach or fall below
the 0.30 clearance requirement (using a conservative 1.75 mm subtraction gives
−0.09 /0.10). Final cap measurement can therefore require a later slope start,
local roof recess, or a higher deck; those alternatives are not silently accepted. Actual chamfers, skins, bosses and cables
must be audited in 3D. Section C shows conservative YZ obstacle projections;
it is not a claim that GH lies on the X0 cut.

## 4. Wiring first pass: gates retained, route changed

The adopted #246 measurement coordinates are **before +6 Z**. That translation
must be applied before comparing with its assembly index. Lengths and all
fourteen corresponding reserve values below come from the saved data.

| Gate | Adopted #246 evidence | Low-deck first-pass verdict |
|---|---|---|
| Conductor ≤200 | L198.078 / R199.435; margins 1.922 /0.565 | Hard gate retained; new end-to-end route NOT yet proven |
| Service ~30 | Every conductor releases 30.20 by moving U Y22.1→7 | Reserve retained as requirement; put removable loops in raised mass, new motion audit needed |
| Fly 170 storage | Connected OD2 R5, exactly 170; stored max axis global Z20.6 | Same cable length/endpoints relative to boards; lowering geometry fits below plateau, slope conflict requires redressing |
| USB insertion | shell, overmold and exit sweeps clear for 30 travel | Move seat and opening together; roof must reopen north access; rerun all sweeps |
| Retention/service | Four lid retainers, removable POM, lift Main for reserve | New shell retention/support, tool access and removal sequence required |
| Complete collision gate | 427 solids, 90,951 pairs, no unexpected intersections | No inherited PASS for changed geometry; full Phase B audit required |

Propose fourteen separate OD≤1 AWG28 conductors leaving each unchanged GH
horizontally, moving inward through the existing keyless north-tab corridor,
then rising into the central mass **north of Main's Y2.268 edge**. Keep R≥5;
do not force a Ø5 bundle through the reduced under-Wing gap. At Z5.75±0.50 the
exit clears the floor, but an OD5 pack near B7.35 would hit PCB/components.
Locate the two service loops in separate lateral bays above the low deck, with
removable retention. Avoid placing a vertical wire through the Main PCB.
First allocate the rise in the north neck near Y−24, X±7, then carry it
above the Wing decks across the new bridge. Allocate reserve storage further
south near Y25…45 at axis Z14…15; actual available shape
is the central footprint minus wells and retained obstacles, not the entire box.
The southward Main approach descends to the unchanged outward mating axes.
The central shell is a hollow cavity, not solid infill over the wires.

An R5 quarter rise costs 7.854 mm arc length per 90°; an S rise needs ≥10 mm
horizontal extent and ≥10 mm height for two quarter turns. Available exit
axis5.75 to loop axis17 is 11.25 mm; north-corridor-to-Main latitude has >20 mm
for that turn. A 30.2 reserve requires 15.1 extra straight travel per U leg;
two legs 12 mm apart permit R5 turns, with an OD5 envelope width 17 mm.
Two such loop envelopes need about 34 mm lateral space before walls and
separation; the central footprint narrows to 23.6 mm near Y−30, so **they cannot
both occupy the narrow north neck side by side**. Put the loops further south
in the wider bay, stagger them longitudinally or separate their Z layers.
That packing is a Phase B dependency, not a proven reserve volume.

Length accounting: with 30.2 reserve and a proposed 5 mm fabrication allowance,
the dressed path budget is **164.8 mm**. #246 shorter references are
167.878 /169.235, so a replacement must save at least **3.078 /4.435 mm** to
meet that extra allowance; the 5 mm is a proposal, not permission to exceed 200.
The longest GH exit-to-Main endpoint straight chord is about 82 mm after a
common board translation; that leaves substantial theoretical routing budget,
but a chord is neither an R5 route nor collision evidence. The new rises can
consume savings. Keep each full conductor, cavity mapping, six returns and
crimp reference planes in the next route length calculation. Do not add reserve
as a detached cable, count an average wire or invoke an overlength exception.

Fly can reuse its north segment; translating the entire #246 Fly path by −8.65
keeps the exact 170 length and yields overall material max Z12.95. However, at
Y62.12 the new slope underside is ~12.91, already **0.04 below** the
conservative global cable material maximum Z12.95, before any clearance budget.
This projected conflict does not establish a precise 3D intersection but prevents
a first-pass clearance claim; lower keytop sensitivity worsens it.
Do not claim the translated Fly passes: redress its south excursion northward,
or locally change the slope after review, while retaining exactly 170 and R5.
It shares the raised bay with GH loops and supports; its volume is not free.

Retain the #246 splice relocations and floor-rooted structural principle, but
recheck all low-seat/channel/splice intersections. The D-037 USB external
opening/seat must follow the lowered Fly; its internal-model limitation F-015
remains, alongside a physical mating check. A tall north strip must not close
the 30 mm plug/overmold/cable sweep. Verdict: **plausible architecture, conditional
stack target; all six new-geometry gates pending**, with reserve packing, right
length margin and Fly/slope competition the leading risks.

## 5. Cap skirt, full press and extraction clearance

For the first drawing assume a maximum swept cap **16.00 square in its own key
axes**, including all travel positions. This enlarges the inherited 15.8 planning
square by 0.20 but does not turn it into measured Junana data. Cut 18.00 wells
in the same rotated axes, with no inward lip at any height. The plan subtracts
the union of every well from every raised region, including the central slope.

| Check | Nominal calculation | Budget/result |
|---|---|---|
| Moving cap to raised wall, full 3.70 travel | (18−16)/2 | 1.00 radial; allocate 0.20 cap sway/pose +0.15 wall print +0.15 registration = **0.50 residual**, ≥0.30 |
| Full-press skirt to low plate | inherited required bottom plate+0.40 | **0.40 nominal**, only 0.10 margin to 0.30; physical/tolerance gate unresolved |
| Bare switch vertical extraction | width max planning 15.40+0.40 =15.80 | (18−15.8)/2 = **1.10 radial** through raised height |
| Puller jaws / clip release | straight +Z, no shell overhang | remove north strips/central shell first; do not assume jaws fit the 1.10 gap |

All 42 cap-envelope distances to the planned raised regions are ≥1.00 mm by
the accompanying planar calculation. That proves the stated horizontal
envelope arithmetic for these drawings. It does not prove actual cap-to-switch,
cap-to-plate, elastic tilt, moulding, or extraction-tool clearance. Vertical
translation of a fixed swept XY square does not change its clearance to a
vertical well wall, so the same horizontal result applies at full press.
At 17 pitch these wells merge; no unsupported thin webs are proposed. Do not
reduce wells to 14 mm switch apertures. Physical switch retention still uses
the separate #232 14.02 nominal plate apertures.

## 6. Manufacturing and cost, cost first

Recommend **printed PETG removable hollow raised parts**, keeping the existing
specification of aluminium switch plates. Print a separate central shell and
left/right north strips, 2.0 mm nominal walls/roof with ribs in keyless zones,
heat-set/captured hardware outside moving envelopes. Prototype with simple
screw removal; snap-only retention and thin cantilever roofs need extra testing.
Orient shells open side up where practical; verify the slope/roof bridging and
use sacrificial supports or a separate roof if needed. Inspect warping, inserts,
layer separation and palm finishing. Do not transfer #246's aluminium 0.25 mm
pocket skin or local stress result to a printed shell. No whole-shell load
qualification is claimed; thickness/ribs may change after the PMO gate.

| Raised-parts set (excludes replacement trays and switch plates) | Planning cost in USD | Basis / uncertainty |
|---|---:|---|
| DIY printed material | 1.20–4.20 | assumed 60–140 g at $20–30/kg; ~3–8 printer hours, excludes electricity, labour and failures |
| Printed fasteners/inserts | 2–6 | planning allowance; final inventory pending |
| Outsourced printed set | 20–60 | budget assumption, no supplier quotation |
| Machined 6061-T6 three-piece set, one-off | 120–400 | budget assumption; pockets, setup, finishing drive cost |
| Machined set, ten sets, per set | 45–140 | budget assumption, no quantity quote |

These numbers compare proposed processes, not current market quotations.
#246's prior one-off **single** machined cover allowance was $85–290; it is not
a quote for these three larger raised parts. A solid aluminium block wastes
stock and increases mass; hollow machining improves mass but adds pocketing time,
tool access and minimum-web constraints. Printed parts are the cost-first
choice; CNC is an optional later finish/durability choice after physical cap fit.

Ender-3 Pro limit is **220×220 including brim**, not just model bounds. Use 5 mm
brim per XY side. Existing 17 mm tray bounds + brim are left159.021×156.069,
right152.021×156.069; height reduction does not enlarge XY. Each north strip is
clipped inside its respective deck, so those same bounds conservatively apply.
Allocate central shell ≤90×140 model, **100×150 with brim**; split features if
CAD exceeds this allocation. Posts are 4.5 square /14.5 square with brim.
No one-piece full-width case is proposed. These are plan bounding checks;
mesh/manifold checks and actual oriented brim envelopes belong to Phase B.

## Reproduction and verification

Run from repository root:

```sh
mkdir -p .issue248-runtime/pydeps
TMPDIR="$PWD/.issue248-runtime" python3 -m pip install --target .issue248-runtime/pydeps shapely --no-deps
TMPDIR="$PWD/.issue248-runtime" python3 hardware/case/issue-248-lowdeck-raise/analyze.py
```

Uses Python 3, Matplotlib and Shapely (2.2.0 used here). The script derives the
42 placed caps/wells, raised masks, stack arithmetic, slope tables, bed bounds
and PNG/SVG drawings from repo inputs. It asserts the 42 horizontal cap/raise
distances and bed allocations. [Input hashes](sources/input-sha256.json) bind
the core baseline evidence; the saved issue binds scope. No full collision audit,
R5 harness reconstruction or physical test was run for this Phase A geometry.
The private runtime git is based on merged main
`0e5f1703053aa1055db2384c173be0dc89a02f7c`; only this new study tree is committed.
The PMO can fetch that branch and create the issue-requested Draft PR. This worker
does not publish Phase B or alter the adopted design.

## Open questions for the PMO gate

1. Accept **13.55 conditional stack target** for Phase B routing exploration,
   with an explicit increase if complete R5 routes/service motion cannot fit?
   A certified minimum with all gates has not yet been established.
2. Obtain/measure the chosen Junana concave, convex and homing caps on Jade Pro:
   q, installed skirt at full 3.70 travel, swept width, rocking and clip-tool
   access. Is the highest unpressed surface the approved common raise datum?
   **24.65 is provisional**, not an empirical keytop height.
3. Accept the Y8→69.7 slope and its conditional Fly redress; if packing fails,
   which adjustment is preferred: later toe, northward cable storage, or higher
   plate? No length, reserve, clearance or USB gate is waived by this question.
4. Accept cost-first removable printed shells and lowered Main/Fly seats and
   USB opening as the Phase B direction, with new supports/retainers and complete
   #246 audit set plus physical cap/palm/load/inversion/USB acceptance?
