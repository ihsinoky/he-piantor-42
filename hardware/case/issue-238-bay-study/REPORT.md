# Issue #238 — flush Z16.2 central bay feasibility study

2026-11-13 · `issue-238-bay-cover` · mm and mm³ · study only

## Verdict: INFEASIBLE with the unchanged #232 starting geometry

Main Rev.6's **BM14B-GHS-TBT + GHR-14V-S rigid mated stack is 7.30 mm**, per the JST assembly drawing. Main top is **Z11.20**, so the mated housings reach **Z18.50**. They exceed the required **Z16.20 plane by 2.30 mm even with a zero-thickness cover**. A nominal 1.50 mm roof puts its underside at **Z14.70**, increasing the rigid shortfall to **3.80 mm**. Neither cable shortening nor moving slack below Main changes this local obstruction.

The plugs' wires exit **vertically**, not sideways. Retaining #232's R5 minimum conductor bend and Ø1 maximum wire, an immediate optimistic 90° bend reaches **Z24.00** (wire centre Z23.50 plus radius0.50). That is **9.30 mm above a Z14.70 underside**, before straight lead, solder, tolerance or assembly clearance. The old route endpoint Z18.5 happens to equal the catalog nominal housing top; it was not used as a dimensional source.

This is a conclusive negative result, not a successful full-assembly clearance certificate. No raised-cover alternative is proposed. A shorter Fly cable alone cannot make this design feasible. No production parts, baseline, decisions, board or electrical contract were changed.

## Inputs and measurement method

Read [Issue238 including the PO comment](sources/issue238.json), [#232 REPORT](../issue-232-final/REPORT.md) and [ASSEMBLY](../issue-232-final/ASSEMBLY.md), #235 [round2](../../kicad/qualification/issue-235-wing-round2/REPORT.md) and [round3](../../kicad/qualification/issue-235-wing-round2/REPORT3.md), and D-024/D-037/D-038/D-039 in [decisions](../../../docs/decisions.md). D-039 is the adopted Rev.4 successor; the round2 report's historical 16L failure is closed by round3. Both 16/17 pitch #232 assemblies are measured independently.

The script loads the **actual exported #232 BReps**, Main Rev.6 native PCB/BOM and #235 native footprint obstacles. It does not rebuild or write any source tree. Main is a triangular PCB with XY vertices (0,2.267949), (−37.892683,67.9), (37.892682,67.9). Main thickness is1.20, undersideZ10, topZ11.20. There are **62 F.Cu footprints: 55 purchased components, four bare test pads, three holes; no B.Cu components**. “Bare underside” does not exclude copper/vias or require cables to rub soldermask.

Heights below are manufacturer package maxima/reference dimensions with an explicit **+0.20 mounting/solder study allowance**, except bare test pads. The actual installed sample height/tolerance is not available. The old blanket5 mm passive reservations are not measured parts and are not used as true heights. Native footprint XY boxes receive a separate **0.50 mm planar body margin** before free-volume subtraction; therefore above-Main figures are conservative envelope budgets, not an exact fluid-volume measurement of every lead. Fixed case/hardware subtraction is exact BRep Boolean geometry. Subtractions are sequential to avoid double-counting overlapping reservations. All inputs are hashed in [inputs-sha256.json](inputs-sha256.json).

## Main top inventory and real height budget

[main-inventory.csv](main-inventory.csv) / [JSON](main-inventory.json) enumerate **every reference, exact BOM MPN, native position/rotation/side, dimensional source, package height, allowance and lid clearance**. [Source notes](sources/README.md) link the manufacturer drawings and identify download limitations.

| Components | Package max/reference height | Study height incl.0.20 | Study top Z | Gap to Z14.70 underside |
|---|---:|---:|---:|---:|
| C1/C2, Fenghua15pF; C20–22, Fenghua1nF |0.55|0.75|11.95|2.75|
| C3–11/C15/C25, Samsung100nF |0.55|0.75|11.95|2.75|
| C12/C13, Samsung0402 1µF |0.60|0.80|12.00|2.70|
| C16–19, Samsung0603 1µF |0.90|1.10|12.30|2.40|
| C14 Samsung10µF; C23/C24 Murata22µF |1.45|1.65|12.85|1.85|
| C26/C27/C28, TDK1210 22µF |2.80|3.00|14.20|0.50|
| R3–19, Uniroyal / Vishay TNPW |0.55|0.75|11.95|2.75|
| L1, XFL4020-152MEC |2.10|2.30|13.50|1.20|
| U1 RP2040 QFN |0.90|1.10|12.30|2.40|
| U3 W25Q16JV **UX** USON |0.60|0.80|12.00|2.70|
| U4 AP2112K SOT25 |1.30|1.50|12.70|2.00|
| U5 TPS22919 DCK |1.10|1.30|12.50|2.20|
| U6 TPS63070 RNM |1.00|1.20|12.40|2.30|
| Y1 exact ABM8-272-T3 |0.80|1.00|12.20|2.50|
| J4, mated EZmate |1.90|2.10|13.30|1.40|
| J2/J3, **mated top-entry GH** |7.30|7.50|18.70|**−4.00**|
| TP1–4 |0|0|11.20|3.50|

The non-GH top components fit below the nominal roof budget. This does **not** mean a Ø5 Wing bundle can cruise across them: bare-board headroom is only3.50 under the roof; over C26–28 it is0.50. At the zero-thickness plane the bare-board budget is5.00, exactly the bundle diameter with zero clearance before components.

JST housing dimensions are not inferred from the bare **4.25 mm header height**: GHR-14V-S housing height5.70, 14-way pitch span16.25, housing width18.75, BM header width20.75. The **mated** assembly drawing explicitly gives7.30. Even Ø0.76 wire with zero straight lead and R5 needs **Z23.88**. With Ø1, optional straight lead0/1/2 mm gives top24/25/26. **R5 is the inherited design minimum, not a bend requirement falsely attributed to JST**; the manufacturer catalog does not specify a harness bend radius. Even an impossible zero-radius turn would not remove the rigid2.30 mm excess.

## Free volumes and their limits

| Region (same nominal result both pitches) | Gross | Available after fixed features/envelopes |
|---|---:|---:|
| Above Main, Z11.20…16.20 plane |12434.872|9249.410|
| Above Main, Z11.20…14.70 roof underside |8704.411|6263.777|
| Under Main, Z2…10 |19895.796|18091.365|
| Selected neck, X±10.498/Y−43…2.267949, Z2…14.70 |12070.662|10274.602|

The neck and Main plan regions are disjoint except their boundary; the two above-Main rows are alternatives and must **not** be added. Counts exclude the old cable routes so they represent room potentially allocatable to new cables. Main cavities are **not** an unobstructed8 mm-high rectangle: three Ø4.5 Main bosses rise toZ10, the south splice has bosses/screws at(−5,55)/(12,55), and case webs occupy more space. Subtraction lists in each pitch JSON account for those features. The broad neck also contains inner Wing bosses/posts/fasteners, rack column(1,−14), and north splice bosses at(−5,−8)/(12,−8), Ø7, topZ8. These obstruct paths even when aggregate volume is large.

Fly board bottom remainsZ10 and top11.59; its EZmate header alone hangs to **Z8.55**. The retained 1.90 mated stack reaches **Z8.10**; the plug is **5×3.5×1.30**, spanningZ8.10…9.40, with **6.10 mm floor gap**. Its wire axis isZ8.60. These values come from the official Fly/header and retained Molex envelope, not the elevated loop endpoint. The plug is not the binding Z constraint. Fly USB external shell top isZ14.90, so a uniform1.50 roof would clip it by0.20; local underside relief toZ15.20 could leave0.30 clearance and a1.00 skin while keeping topZ16.20.

Other possible room is the existing Wing underside passages. It is reserved by Rev.4 Hall/MUX/connector bodies and twelve support posts, not an unoccupied cable locker. No volume outside the case or above the closed top is credited.

## Harness re-dress and storage accounting

**Wing160 mm class:** retain the real #232 underside fanouts, the Ø6/R5 passage and centreZ5 bundle. The measured connector-to-bundle exits are (±27+(i−6.5)×1.25,−35.45,8.4), then (sameX,−31.5,8.4), (±27,−24,5), joining the lower run. The lower common path passes (±7,−16,5). Those physical entrances remain usable. A Ø5 envelope atZ5 has0.50 floor gap and2.50 to the Main underside away from features.

The old complete160 mm path contains **33.825 mm service** over its126.175 mm integrated reference. Its elevated detour and cruise are not credited under a lid. **There is no valid complete under-cover re-dress to J2/J3 at any length**: the final connected segment must exit vertically above the Z18.50 housing. Moving the lower run/slack beneath Main cannot change that terminal boundary condition. A planar loop or a disconnected160 mm ring would conceal the obstruction. Consequently no under-cover30 mm service allowance is certified. D-024's fourteen1:1 conductors and six independent returns are maintained; no right-angle adapter, soldered flying lead or connector substitution is silently introduced.

For scale, two160 mm conservative Ø5 bundle tubes need **6283.185 mm³**, versus **3518.584 mm³** of14 separate Ø1 wire cylinders. Those are demand estimates, not collision-free packing certificates. R5 loops require at least10 mm centreline U-turn width,15 mm total Ø5 envelope width. Volume is not the decisive shortage here.

**Fly stock170 mm:** the script builds one continuous sweep with the **original two mating endpoints**, R5 prefix fillets and three exact R5 S bends. Its length is170.000000, diameter2, analytic/exported volume **534.070751 mm³**, topZ13.600000, nominal roof gap1.10. All170 mm—including service/slack—are explicitly present. The lower out-and-back leg uses X±9/Z5 in the neck, reverses at the pitch-dependent Y below, returns north via(9,−18,5)/(9,−30,12.6), and travels south on the upper layer. R5 S bends move X−4→0→5→0 and finish at Main(0,17.435,12.6). Full prefix waypoints and sampled complete path are saved per pitch; the S-bend script is authoritative.

| Pitch | Cover outline area | Cover Y range | Fly lower U-turn Y | Fly tray overlaps L / R, mm³ |
|---|---:|---|---:|---|
| 16 | 3889.683 | -52.344…69.700 | 6.523909 | 2.728060 / 9.724879 |
| 17 | 3922.122 | -53.726…69.700 | 5.838317 | 1.634145 / 9.724879 |

For reference, the original17 mm point-to-point Fly route is73.8705 mm;170 −73.8705 =96.1295 mm includes its30 mm service allowance and66.1295 mm further slack. That elevated reference is not counted as an under-cover route. The new trial contains all170 mm, with zero unmodeled length; accessible service allowance is unqualified because the trial collides.

**This Fly candidate is rejected**, not a claimed successful storage design. It clears the other retained bodies tested but intersects the north splice bosses and local neck material; BRep intersections are recorded in JSON. The earlier connected trial also hit the Main screw and inner Wing stacks; its evidence is in [rejected-trials.json](rejected-trials.json). There is enough aggregate volume for534 mm³, but no approved170 mm under-cover storage location is established. This does not prove Fly alone impossible; the independent GH rigid-stack obstruction already proves the requested combined assembly impossible. No cable is shortened, cut, disconnected into multiple pieces or represented by a loose ring.

## Cover outline, retention and service concept

[Top view](top-view.svg), [GH section A–A](section-gh.svg), [longitudinal BRep section B–B](section-bay.svg). Native polygons and CSV/JSON coordinates drive the drawings. The cover uses #232's service-bay mask, inset0.20 from the retained inner rim, and follows the D-037 silhouette at its north/south terminations. It stays between the independent Wing decks; it does not introduce a Wing connector notch. Maximum X extent is about±41.010 mm. Exact per-pitch outlines are in the measurement JSON. This is a 2D review proposal; **no 3D production cover or manufacturing tree is issued before the issue's outline gate**. Numerical slabs are interference probes.

TopZ16.20 gives nominal **0.00 step** to the Wing plates and rim. The drawing targets a **0.20 seam to the inner rim**. On straight boundaries the full cover-to-plate separation is nominally1.40 mm:0.20 seam +1.00 retained rim +0.20 plate seam; corner transitions follow the saved polygons. The two decks stay fixed by their own four ties each. A hypothetical1.50 cover would use the Z14.70 ledge where present, with underside relief over the Fly shell and narrow case intrusions. Thickness/flatness and print variation remain physical risks: #232 plate thickness alone permits −0.05…+0.01 top variation before flatness/printing. This study cannot certify a manufactured single plane.

The #232 inner rim is a boundary, **not a continuous new cover support ledge**. A viable continuation would need independent support/retention inside the bay. A concept is two concealed edge hooks and captive underside M2 screws into cover lugs, leaving no screw head aboveZ16.20. This would require new floor access/retention features or an independently qualified removable carrier; locations, lug strength and cable clearance have not been qualified. Do not drill the existing case or use Wing ties as shared cover fasteners based on this study.

Conditional service sequence, if the height obstruction were resolved in a later authorized design: power off/unplug USB; release underside captive fasteners; lift the south edge and disengage north hooks; remove cover vertically without moving the Wing plates; release GH/EZmate housings by their latches, then remove Main's three screws or Fly's two screws. Both boards remain replaceable **without desoldering**. Wing deck ties remain accessible and independent. During reassembly, all slack must be laid in connected channels before seating the roof; the cover must not compress wires. This procedure is a requirement/concept, **not a demonstrated successful covered assembly**.

## Checks and disposition

Uniform Z14.70…16.20 slab probe against the fixed assembly and new source-derived Main envelopes:

| Interference |16 mm, mm³|17 mm, mm³|
|---|---:|---:|
| cable-rack | 18.849556 | 18.849556 |
| Fly-official-42-instance-42 | 8.834742 | 8.835230 |
| tray-left | 6.642586 | 7.075091 |
| tray-right | 6.641244 | 7.074308 |
| Main-study-J3 | 413.954104 | 413.954104 |
| Main-study-J2 | 413.954113 | 413.954113 |

The Main overlap volumes are conservative placement-envelope intersections, not exact plug plastic volumes. The **height shortfall is from the actual manufacturer assembly dimension**, independent of those boxes. The rack and tray values are BRep intersections. The source Fly shell is invalid as accepted in D-037; its reported intersection is diagnostic and is not a newly certified solid-volume measurement. Neither discarding that shell nor removing the rack removes the GH proof.

- **Full assembly, cover on, interference0: FAIL.** Rigid plugs, rack and the connected Fly candidate fail; no all-pairs zero-overlap pass is claimed. A single unavoidable positive obstruction is sufficient to reject feasibility.
- **D-037 USB insertion:** source seat, board, opening, mouth and fixings remain unchanged; the source30 mm/6.20 engagement external case-side test remains applicable. Each shell/overmold/cable-exit continuous30 mm translation is conservatively enclosed by its swept bounding prism; the proposed cover has **zero intersection** with all three, at both pitches. Minimum shell-to-unrelieved-roof gap0.18; local Fly relief would improve it. This new check certifies no added *cover* obstruction, not a successful whole covered assembly. D-037's defective internal shell/mating overlap remains expressly accepted/unqualified; no strict internal-mating pass is invented.
- **#232 passage:** unchanged Ø6/R5 passage retains the original Ø5 lower envelope; saved baseline tray/harness overlap0 at both pitches, floor removal0, original roof≥2.75077. Removal volumes are68.617896/68.818003 mm³ (16L/R),68.617778/68.817600 (17L/R). This preserves the passage, not the elevated rise. The current rack top is **Z22.20**, not Z20.20;20.20 is its height fromZ2. It must be removed/replaced in any flush continuation. It is a detachable accessory, so it is not the irreducible board obstruction.
- **Thermal note, not a gate:** closing the bay removes open convection above the5.2 V TPS63070/L1 converter. Under the budget U6 has2.30 mm and L1 has1.20 mm roof gap. Cable storage must not blanket these parts. Temperature rise/efficiency under a lid is not measured; any future closed design should compare temperatures at the existing electrical load. No thermal rejection or electrical change is imposed by this study.

## What would have to change

Keeping the existing top-entry GH orientation and R5/Ø1 exit, a1.50 roof would require Main top≤Z1.90, underside≤Z0.70: **lower Main by at least9.30 mm**, or9.50 including the declared0.20 mounting allowance. That puts its underside **1.30–1.50 mm below the existing Z2 floor surface**, before clearance/support, and removes the current under-Main storage cavity. It is not a feasible simple boss trim in this case. Bare housing alone would require3.80 mm lowering, but that ignores the wire and is insufficient.

A side-entry Main connector would change Main's mechanical/PCB input (and requires a fresh placement/routing/mating study); a raised roof violates the explicit PO decision. A deeper case/floor plus relocated Main supports, removal/replacement of the rack, and new routing could be investigated as a named case change, but are not demonstrated feasible here. No exact shorter Fly length is offered as a supposed cure: even a zero-slack cable cannot fix J2/J3.

Thus this report deliberately does **not** use “FEASIBLE ONLY WITH A NAMED CHANGE” for an unverified redesign. The measured2.30 mm rigid shortfall at the current Main datum is binding for the supplied unchanged assembly.

## Reproduce and verify

Run `hardware/case/issue-238-bay-study/reproduce.sh` (includes report generation and verification). For a read-only check alone run `python3 hardware/case/issue-238-bay-study/verify.py`. Tools: build123d0.13, OCCT via OCP, Shapely2.2, sexpdata, CairoSVG; installed read-only CAD environment, with CAD_PYTHON/GEOMETRY_SITE overrides supported. No downloads are needed for reproduction. Drawings are SVG and PNG; the B–B section uses actual BRep edges, excluding only the already-invalid shell, whose external bbox is shown separately. A verifier PASS means the **negative result is consistent**, not that the design fits.

Scratch, caches, logs and the private Git database are exclusively `.issue238-runtime/`. That database's first commit snapshots the starting checkout; study changes are committed on `issue-238-bay-cover`. No push/PR. Existing trees, decisions and baselines remain unchanged. `artifact-sha256.json` binds the delivered files, while the private Git comparison protects the rest of the checkout.
