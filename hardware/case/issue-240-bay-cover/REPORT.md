# Issue 240 — bay cover study

2026-11-13. **INFEASIBLE for the evaluated complete assembly.** The required
zero-interference gate fails. This is a rejection of the supplied cable
routing candidate, **not a proof that every possible under-cover routing is
impossible**. A successful bay close-out has not been achieved. No baseline,
decision, existing case tree or manufacturing package is changed.

The [Main candidate](../../kicad/qualification/issue-240-main-rev7/REPORT.md)
passes its electrical gates, but discloses a routing-scope exception. Neither
that electrical pass nor the aggregate free volume establishes a viable lid.

## Real stack and exact relief budget

JST's [current GH catalog](https://www.jst.com/wp-content/uploads/2025/06/eGH.pdf),
p2, gives **4.35 reference mated height** and **7.15 axial length** for the
side-entry assembly; the historical manufacturer copy agrees. The source PDF
is saved in the [connector evidence](../../kicad/qualification/issue-240-main-rev7/connector/).
These are reference dimensions, not vendor maximum-tolerance guarantees.
The standard GHR-14V-S plug and horizontal exit are retained.

Main top is **Z11.20**. The nominal mated top is **Z15.55**, below the required
Z16.20 top, but **0.85 above a uniform 1.50 mm roof underside Z14.70**.
The study adds **0.20 mounting allowance** and **0.20 assembly clearance**:
GH pocket ceiling **Z15.95**, depth **1.25**, remaining skin **0.25**.
The pocket outline is the 20.75 ×7.15 rigid mated reservation plus0.30 XY margin.
This thin skin is a geometric study, not a qualified material/process choice.
The wire axis is the inherited **1.60 above-board planning datum, Z12.80**;
it is not misrepresented as a dimension explicitly specified by JST.
R5 and Ø1 conductor limits are inherited dressing assumptions, not JST bend rules.

The Fly cable pocket ceiling is **Z15.80**, depth **1.10**, skin **0.40**.
Its XY sweep includes ≥0.20 clearance after the documented0.02 simplification
of the sampled centreline; radius1.22 offsets the simplified projection.
The Fly external USB shell uses a **10 ×10 / depth0.50** underside pocket,
ceiling **Z15.20**, skin **1.00**. All reliefs are underside-only. The modeled
cover top, and countersunk screw head tops, remain **Z16.20**. The original
#238 bay outline/USB cutout is retained. None of these pockets resolves the
cable collisions listed below.

## Connected cables, length and service accounting

Each Wing model contains the original fourteen Ø1 underside fanouts, the lower
Ø5 conservative bundle and fourteen upper/terminal fanouts. Those constituents
form one connected cable envelope; overlap at the transitions is not added twice
to conductor length. The source #232 wall passages, Wing decks, PCBs and fixing
hardware are retained unchanged. No disconnected coil is credited as slack.

| Harness | Longest connected conductor mm | Shorter R5-valid reference in this routing family mm | Physically represented extra path mm |
|---|---:|---:|---:|
| left | 160.000000 | 155.639413 | 4.360587 |
| right | 160.000000 | 155.038848 | 4.961152 |

The reference uses the same route family with south coordinate−4.99; it is not
a straight chord or a claimed globally shortest route. Both160 mm trials have
zero unmodeled cable length. Their represented extra path is only about4–5 mm,
**not the ≥30 mm service reserve of the #232 design**. Because these routes
collide, no accessible service allowance is certified. Reaching30 mm in this
family would require about185–186 mm, and the same family still collides; a
longer harness is not presented as a successful fix.

The Fly model is **one valid solid, one connected 170.000000 mm sweep**, Ø2,
R5 minimum, with both original EZmate endpoints. Its volume agrees with
π×170 mm³ within0.001. All170 mm, including slack/service length, is present;
there is no detached ring, shortened stock cable or omitted segment.
The selected storage crosses the neck at X0.9/Z14.6, uses a south U at about
Y61–62, returns via X−14.6/−4 and meets Main at(0,17.435,12.6).
Exact per-pitch waypoints and2001 path samples are saved in measurements.json.
The wire's top is15.60 in the upper cruise, allowing0.20 below its pocket.
170 minus the old17 mm point-to-point73.8705 reference is96.1295 mm; this is
comparison accounting, not a newly certified service allowance under this lid.

## Binding measurements and full audit

| Pitch mm | Unexpected constituent contacts | Contacts involving Fly cable | D-037 external USB insertion vs cover |
|---|---:|---:|---|
| 16 | ≥67 | 0 observed | PASS |
| 17 | ≥72 | 0 observed | PASS |

The common left lower route intersects the **north splice screw by
2.628268884 mm³** in both pitches. It also intersects the retained left tray by
**164.790575503 mm³ at17 pitch /164.790354674 mm³ at16**. The right lower route
intersects its tray by **133.702107392 /133.701451895 mm³** respectively.
These are positive BRep intersections with unchanged solid hardware, not
contacts between two representations of one cable. Upper routes also intersect
Wing PCBs; individual examples are **0.044989552 mm³ left** and
**0.044989544 mm³ right**. The layout cannot be assembled as modeled.

Largest17 mm contacts (solid indices identify individual envelope constituents):

| Added part | Other part | Intersection mm³ |
|---|---|---:|
| Wing-left-lower [0] | tray-left [0] | 164.790575503 |
| Wing-right-lower [0] | tray-right [0] | 133.702107392 |
| Wing-right-upper [9] | tray-right [0] | 7.809604616 |
| Wing-left-upper [5] | tray-left [0] | 7.809261197 |
| Wing-right-upper [4] | tray-right [0] | 7.740778103 |
| Wing-left-upper [0] | tray-left [0] | 7.740432203 |
| Wing-right-upper [13] | tray-right [0] | 7.409865710 |
| Wing-left-upper [10] | tray-left [0] | 7.409534295 |
| Cover [0] | tray-left [0] | 7.075091292 |
| Wing-right-upper [8] | tray-right [0] | 6.890646841 |

The scheduled audit covers added/replaced parts against retained leaves and
other new parts. **The exhaustive enumeration was stopped after measured
counterexamples had conclusively failed the zero-interference gate.**
`all_pairs_audited` is false; counts above are lower bounds and the contact
list is not exhaustive. No full-fit certificate is issued. The exclusion
policy permits only own connector mating volumes, constituents of the same
conservative cable envelope, and nominal thread mating. Pair counts and every positive overlap are in
[16 mm measurements](16mm/measurements.json) and
[17 mm measurements](17mm/measurements.json). Constituent volumes must not be
summed into a unique assembly intersection volume because envelopes may overlap
within the same cable. The retained fixed-versus-fixed audit and documented
D-037 defective official USB internal-model limit are inherited from #232;
this does not relabel that internal mating model a physical pass.

The continuous30 mm USB shell/overmold/cable insertion reservations are checked
against the new cover. The unchanged source seats and opening are not modified.
The reported USB result concerns external insertion clearance; the prior
physical USB mating limitation remains.

## Rack, support/retention and service procedure

The **64 ×15 mm detachable rack, original top Z22.20, is removed completely**.
Leaving it in place is incompatible with aZ16.20 lid. No new raised rack or
outside-cover slack storage is credited.

The #232 rim is not treated as a continuous ledge. Four separate clip ledges
are modeled at the north Y−34…−30 and south Y59…63 bands,4 mm inward bearing,
Z13.20…14.70. Four **M1.6×4 countersunk screws** and3.2 AF nuts retain the lid;
the nut envelope spansZ11.90…13.20. Sites, part envelopes and any contacts are
recorded in measurements.json. Threads are nominal envelope mating, not a
helix model. The clip roots bridge the0.20 rim seam and require bonded attachment
to the retained inner wall, about6 mm² nominal root contact per clip. Bond
strength, thin-skin stiffness and retention/load/inversion performance are
**unqualified**. These supports are a reviewable rejected-study concept, not
approval to manufacture or a successful structural close-out.

Incremental inventory is one pocketed cover, four clip ledges, four screws and
four nuts, plus the two header substitutions; the rack is omitted. No supplier
or machining quote is established. Since the assembly fails, **no costed,
feasible change package is asserted**.

Service would require unplugging USB, removing the four flush cover screws,
lifting the lid vertically clear of its underside pockets, then releasing GH
latches and pulling housings along their horizontal mating axes. Do not pull
conductors. Wing decks and PCBs can remain fixed for electrical inspection.
A route with only the represented4–5 mm extra path cannot inherit the prior
30 mm service procedure; connectors must be unmated before lifting Main.
There is no demonstrated service procedure for the colliding as-built trial.

## Artifacts and reproduction

[Top view PNG](top-view.png) / [SVG](top-view.svg),
[GH section PNG](section-gh.png) / [SVG](section-gh.svg),
[bay section PNG](section-bay.png) / [SVG](section-bay.svg).
Each pitch contains `cover-trial.step`, both connected Wing160 mm trials,
`fly-170mm.step` and **`assembly-with-cover-REJECTED.step`**. The filename and
verdict deliberately prevent confusing a rendered assembly with a fit pass.

Run `bash hardware/case/issue-240-bay-cover/reproduce.sh 17` and the same with16,
then `MPLCONFIGDIR=$PWD/.issue240-runtime/mpl /usr/bin/python3
hardware/case/issue-240-bay-cover/drawings.py` and
`python3 hardware/case/issue-240-bay-cover/write-report.py`.
Default runs audit afresh; an explicit second argument `--resume` resumes a
same-geometry local collision checkpoint. Do not reuse checkpoints after geometry
or input changes. Scratch, caches and logs stay in `.issue240-runtime/`.
`--resume --reject-known` exports a conclusive rejected-study checkpoint
without finishing the remaining pair enumeration; this cannot produce a fit pass.
`inputs-sha256.json` binds the immutable source assemblies, component inventory,
Rev.6 board and decisions. `manifest.py` verifies the delivered artifact hashes.

The requested complete acceptance is **not established**: the local routing
scope exception, collision-free Wing dressing, inherited service reserve and
qualified retention remain unresolved. The measured failure is documented;
it must not be promoted into a feasible/adopted design.
