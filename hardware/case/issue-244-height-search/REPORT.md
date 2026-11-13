# Issue 244 — coordinated case-height and rise-route study

**No passing Delta established.** Study only; production geometry, baseline and decisions remain unchanged.
The saved Issue #244 assignment is [issue244.json](issue244.json).

Both requested 17 mm candidates have complete covered-assembly audits. Delta=10
fails, so the requested stop condition applies. No 16 mm evaluation or downward
refinement is justified by these rejected packages. This rejects the evaluated
routes/case changes; it does not prove that every possible redesign at 10 mm is
impossible. There is no minimum passing Delta or passing-design drawing to report.
The drawings below document the measured rejected designs.

## Design and coordinate convention

[CASE-REVISION.md](CASE-REVISION.md) gives the complete proposed case-change list.
Both trays and all twelve Wing posts are remade. Their original upper geometry
is split at Z3 and raised with the boards, supports, rim and decks; the section
is extended to the retained lower floor. The common cover/deck top is 16.2+Delta.
No PCB is cut or moved in XY. Main Rev.7 and Wing Rev.4 remain fixed inputs.

The redesigned rises differ from #242: the OD5 lower U has global centre Z7,
X±7/±19 and turn Y28. Fourteen OD1 wires per side return inward to
X±(5+off), Y−18 at Z7, then rise near X±(5+off), Y−5 to
Z12.8+Delta+dz before traversing toward X±(23+off), Y10 and the GH
approaches. The 5/5/4 pack uses off −2…2 and dz −1/0/+1. R5 rounded
curves, not waypoint chords, control geometry. Per-conductor rounded samples,
lengths and endpoints are in each measurements.json. There is no rack or exterior
storage. OD6 lower channels and buffered upper grooves are real case cuts.
Splice screws move from X−5/12 to X0/15 at both original Y rows. Hexagon-shaped
north nut pockets cut through both pillar and surrounding tray material.

**Cable coordinates in measurements.json are before the final Delta translation**;
add Delta to their Z values. Assembly indices, contact bounds and STEP exports
are in the final floor datum. The reported total height is the requested common
top datum 16.2+Delta, not a new claim about foot/keycap overall envelope height.

## Per-candidate full audit and gates

| Delta | Pitch | Top height | Solids | All pairs | AABB rejected | Intended | Exact candidates | Unexpected | Boolean errors |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 6 | 17 | 22.2 | 456 | 103740 | 101792 | 576 | 1372 | 10 | 0 |
| 10 | 17 | 26.2 | 455 | 103285 | 101351 | 576 | 1358 | 12 | 0 |

Every unordered constituent pair is enumerated, including retained/retained pairs.
AABB rejection only removes pairs with no positive overlap. Every remaining
non-intended pair gets OCCT Common; errors never count as clear. Tolerance is
1e−6 mm³. Cover tiles are a disjoint exact CSG partition; finish.py reconstructs
one valid machinable cover and checks its volume against the partition.
Same connected cable envelopes, own connector terminations, documented inherited
source internals and cover partition boundaries have explicit intended-pair
records. Enlarged Main component clearance reservations and nominal own
nut/thread contacts are separately retained in audit.json, as in #242.
No unexpected contact is exempted just because a previous study had it.

| Delta / pitch | 1: interference zero | 2: accessible ≥30 mm | 3: Fly 170 mm storage | 4: D-037 insertion | 5: retention acceptance |
|---|---|---|---|---|---|
| 6 / 17 | FAIL / not established | FAIL / not established | PASS | PASS | FAIL / not established |
| 10 / 17 | FAIL / not established | FAIL / not established | PASS | PASS | FAIL / not established |

## Measured binding contacts

All unexpected pairs, including repeated constituent contacts, are in each
collision-map.json with exact Boolean intersection bounds. Volumes are per pair;
their sum is not the unique collision volume. The remaining Wing PCB contacts show that this inward-rise redesign still
clips the fixed board footprint at its rounded transition. Merely deepening
the cavity with these waypoints does not yield zero interference; no geometric
claim that all alternative rise locations are impossible is made.
The following table groups pairs
only for readability, showing the largest constituent overlap and the bounding
union of their exact contacts. The complete maps remain authoritative.

| Delta / pitch | Parts | Pairs | Largest mm³ | Contact X mm | Contact Y mm | Contact Z mm |
|---|---|---:|---:|---|---|---|
| 6 / 17 | wing_left / Wing-left-upper | 1 | 0.003019988 | -8.4770…-7.9906 | -4.2897…-3.8883 | 17.1304…17.2000 |
| 6 / 17 | wing_right / Wing-right-upper | 1 | 0.003019989 | 7.9906…8.4770 | -4.2897…-3.8883 | 17.1304…17.2000 |
| 6 / 17 | tray-left / Wing-left-upper | 4 | 0.321635687 | -7.8940…-4.2186 | -4.7920…-2.9897 | 19.9000…20.2932 |
| 6 / 17 | tray-right / Wing-right-upper | 4 | 0.321702755 | 4.2186…7.8943 | -4.7920…-2.9895 | 19.9000…20.2932 |
| 10 / 17 | wing_left / Wing-left-upper | 2 | 0.021717198 | -8.7218…-7.3969 | -4.3619…-3.6470 | 21.0272…21.2000 |
| 10 / 17 | wing_right / Wing-right-upper | 2 | 0.021717185 | 7.3969…8.7218 | -4.3619…-3.6470 | 21.0272…21.2000 |
| 10 / 17 | tray-left / Wing-left-upper | 4 | 0.236531150 | -7.7901…-4.4334 | -4.5273…-2.9996 | 23.9000…24.2759 |
| 10 / 17 | tray-right / Wing-right-upper | 4 | 0.236593830 | 4.4334…7.7905 | -4.5273…-2.9995 | 23.9000…24.2759 |

## Connected length, service and USB

| Delta / pitch | Side | Longest represented conductor mm | Shorter reference mm | Represented reserve mm | Cable union valid / solids |
|---|---|---:|---:|---:|---|
| 6 / 17 | left | 207.910229 | 175.910229 | 32.000000 | False / 16 |
| 6 / 17 | right | 209.673874 | 177.673874 | 32.000000 | False / 5 |
| 10 / 17 | left | 215.234742 | 183.234742 | 32.000000 | True / 3 |
| 10 / 17 | right | 216.939124 | 184.939124 | 32.000000 | False / 7 |

The U reference turns at Y12 instead of Y28, shortening two legs by 16 mm
and releasing 32 mm on the same harness; no detached loop or unmodeled cable
is credited. Fourteen entry fanouts, the shared lower bundle and fourteen rising
wires are union-tested; the table records validity and solid count. A failed
union does not certify one connected manufactured cable, and the original
audited conservative envelope export is retained in that case. The raw union
volume in metrology.json is an algorithm diagnostic for failed unions, not a
certified physical material volume; a negative mass or multiple solids is not
accepted as continuity evidence. R5/OD1/OD5 remain
study assumptions, not manufacturer-qualified bend or tolerance specifications.
These longer redesigned paths also exceed the fixed Rev.7 qualification's
200 mm conductor bound (see table); no electrical requalification or silent
relaxation of that bound is made.
A colliding assembly cannot certify accessible service from length arithmetic.

Proposed access procedure:

1. Disconnect external USB. Remove two north M2x6 and two south M2x10 cover
   screws. Main H1 remains installed while the cover is lifted.
2. Lift the lid and remove the two loose south POM spacers.
3. Release GH latches, withdraw each plug along its outward mating axis,
   disconnect Main EZmate, then remove H1 and lift Main. Wing boards/decks stay fixed.
4. Lift/unlace the now open under-Main U and move its turn from Y28 to Y12,
   recovering 32 mm. Reverse to reassemble, checking channel dressing and ensuring
   the cover bears on supports. This is a candidate procedure, not a successful
   service demonstration for a rejected design.

Fly is represented by one connected OD2 R5 sweep of exactly 170 mm, original
EZmate endpoints retained, volume 170π within 0.001 mm³. No segment is shortened
or detached. Its full fitted-case contacts enter the exhaustive audit. Each
USB shell/overmold/cable-exit reservation covers a continuous 30 mm insertion;
measurements.json records any overlap with actual case, lid, cables and hardware.
The protected D-037 seat/opening is separately compared above the Z3 extension,
undoing the uniform Delta translation. The deeper floor region is intentionally
changed and is not certified unchanged. The inherited defective official USB
internal-shell model limitation remains; no physical insertion test is implied.

## Cover, retention, print envelope and cost of Delta

6061-T6 aluminium cover, 1.50 mm nominal, underside 14.7+Delta, flush top
16.2+Delta. Underside pockets retain 0.25 mm GH, 0.40 mm Fly and 1.00 mm USB
skins. Fit the perimeter around retained north rim with 0.30 mm clearance.
Two north M2x6 countersunk screws load captured AF4×1.6 nuts in integral OD8
pillars rooted at global Z1. Two south M2x10 screws use existing Main H2/H3
bosses and washers through removable POM OD4.5/ID2.2×3 mm spacers. No board
hole or spacer length changes; nominal south engagement remains 3.8 mm.
Nuts enter through actual side slots before closure. All screw heads are flush.

The #242 local screens remain applicable to the translated upper details:
at the stated 10 N lid load, nominal 0.25 mm aluminium skin deflection 0.051 mm,
stress 87.1 MPa; 0.22 mm minimum skin gives 0.074 mm / 112.5 MPa. Per-retainer
5 N gives screw tension 2.49 MPa, nut-roof stress 0.82 MPa and south thread
shear 0.42 MPa. These are local study calculations from
[mechanics.json](../issue-242-bay-final/mechanics.json), not whole-panel FEA,
layer-strength qualification or a physical inversion test. Pillar length increases
with Delta; no full-case stiffness pass is inferred. A disconnected tray fragment
or an interference is a retention failure despite acceptable local stress screens.
Machine pockets with the top face supported, then release the perimeter and
inspect minimum skin, flatness and deburring. A one-layer printed roof is not selected.

| Delta / pitch | Part | Valid | Solids | Print XYZ incl. 5 mm XY brim, mm | Fits 220×220×250 |
|---|---|---|---:|---|---|
| 6 / 17 | tray-left | True | 1 | 159.02 × 156.07 × 22.20 | True |
| 6 / 17 | tray-right | True | 2 | 152.02 × 156.07 × 22.20 | True |
| 10 / 17 | tray-left | True | 1 | 159.02 × 156.07 × 26.20 | True |
| 10 / 17 | tray-right | True | 1 | 152.02 × 156.07 × 26.20 | True |

Delta=6 costs 6 mm additional common-top height (22.2 mm); Delta=10 costs
10 mm (26.2 mm). Both complete trays and twelve support posts must be remade;
this is not a lid shim. Plates, boards, spacers and the Fly assembly translate
rigidly; splice plates require new clearance holes. Increased wall/pillar material
and print time are additional to the full replacement print cost. No new supplier
quote is claimed. Reuse the #242 planning allowance: one-off machined cover
US$85–290, batch of ten US$25–80 each, retention parts US$1–4 per set.
The basis was 1–2 shop hours at US$60–120/h plus US$25–50 stock/fixture/finish.
The cover thickness/pocket process stays the same as Delta grows; the main
height cost is the case remake and taller keyboard, not thicker cover stock.

## Artifacts and reproduction

- **Delta 6, 17 mm:** [audit](delta-6/17mm/audit.json), [contact map](delta-6/17mm/collision-map.json), [measurements](delta-6/17mm/measurements.json), [metrology](delta-6/17mm/metrology.json), [invariants](delta-6/17mm/invariants.json), [gates](delta-6/17mm/gates.json); [top PNG](delta-6/17mm/top-view.png) / [SVG](delta-6/17mm/top-view.svg), [sections PNG](delta-6/17mm/sections.png) / [SVG](delta-6/17mm/sections.svg).
- **Delta 10, 17 mm:** [audit](delta-10/17mm/audit.json), [contact map](delta-10/17mm/collision-map.json), [measurements](delta-10/17mm/measurements.json), [metrology](delta-10/17mm/metrology.json), [invariants](delta-10/17mm/invariants.json), [gates](delta-10/17mm/gates.json); [top PNG](delta-10/17mm/top-view.png) / [SVG](delta-10/17mm/top-view.svg), [sections PNG](delta-10/17mm/sections.png) / [SVG](delta-10/17mm/sections.svg).

The routing section is a YZ projection, not an X-constant clearance section;
exact 3D intersections determine the verdict. STEP files deliver changed trays,
Wing cables, Fly storage and the single cover, plus the covered rejected assembly.

Run `bash hardware/case/issue-244-height-search/reproduce.sh 6 17` and similarly
`10 17`. Each rebuilds and audits all pairs, then performs metrology and protected
region comparison. `--audit-only --resume` reuses only hash-matched runtime BReps.
Run `python3 hardware/case/issue-244-height-search/drawings.py`, then
`finalize.py` and `verify.py` to regenerate presentation/hash verification.
The CAD_PYTHON/GEOMETRY_SITE overrides are documented in reproduce.sh.
The first metrology attempts in delta logs stopped on an assumption that rejected
Wing envelopes must union successfully. The completed metrology logs record
their actual failed union results; the verifier checks that these cannot pass
the service gate. No geometry or all-pairs audit was changed by that diagnostic
handling correction.
All scratch, BReps, logs and private Git live under `.issue244-runtime/`; nothing
uses `/tmp`. Completed logs are copied into evidence/. The private Git starting
snapshot and study commit permit checking that only this study directory changed.
A verifier PASS certifies consistent evidence, not a feasible assembly.
No production/baseline/decision edit, push, PR, fabrication release or order occurs.
