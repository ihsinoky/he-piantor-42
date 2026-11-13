# Issue #235 — Wing Rev.4 round 2: right-angle GH and routing closure

Study only · 2026-11-13 · `issue-235-wing-rev4-round2` · checkout base `578ee96a7efbb34fe8aa202d51fc040f22bbebbe` (merged #233 / D-038).

**3/4 routing-qualified electrical candidates: 16mm-right, 17mm-left, 17mm-right. The four-variant Rev.4 adoption gate is NOT closed.** 16mm-left retains the failure evidence documented below. The side-entry GH solves the top-entry floor-height blocker. Installation needs the delivered study-only tray-wall proposal and controlled wire dressing; the original production case does not accept this route. No production trees, Main, decisions, manufacturing packages, orders, push or PR are changed/issued.

## Connector selection and electrical contract

Select **JST SM14B-GHS-TB(LF)(SN), C265343**, a 14-position, 1.25 mm side-entry GH. The preferred family exists, so a different family or hybrid harness is unnecessary. Main keeps BM14B-GHS-TBT. Both ends mate with **GHR-14V-S** using **SSHL-002T-P0.2** contacts. Specify individual AWG28 or larger equivalent copper (>=0.0804 mm²) within JST's insulation OD <=1.0 mm; retain all six separate returns. These are catalog parts; custom fabrication uses standard GH crimp tooling. No AWG30 substitution, reversed cavity order or external Y cable is allowed. Fabricator continuity/retention checks, L/R labels and power-off mating remain required.

Manufacturer [current GH catalog](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), assembly layout p2 and part list p3: **mated side-entry height (4.35 mm), axial length (7.15 mm), horizontal wire exit**. These are reference dimensions, not manufacturer-certified tolerance limits. The [archived manufacturer PDF](connector/eGH-distributor-copy.pdf) distributed by DigiKey agrees (assembly layout p4); the current JST PDF returned HTTP 403 to direct download but was inspected with the web reader. [Source notes](connector/SOURCES.md), [copied library footprint](connector/JST_GH_SM14B-GHS-TB_1x14-1MP_P1.25mm_Horizontal.kicad_mod) and [independent pad coordinates](connector/pads.json) preserve provenance.

**Stock checked directly 2026-11-13 UTC**, not taken from search-cache snippets: [LCSC](https://www.lcsc.com/product-detail/C265343.html) `stockNumber/stockSz` **504**; [JLCPCB](https://jlcpcb.com/partdetail/JST-SM14B_GHS_TB_LF_SN/C265343) `overseasStockCount` **1,859**, separate `canPresaleNumber` **1,196**, `preMinPurchaseNum` **25**. For **30 headers including spares**, the preferred ~10× quantity is 300; both stock observations exceed it. These fields are not additive, reserved stock, a factory BOM acceptance or a purchase. [Timestamp/fields](connector/stock.json) and gzip raw HTML retain the observation. `connector/check-stock.py` performs a fresh read without changing that dated record.

D-024 is invariant: **1 HALL_5V; 2/4/8/10/12/14 GND; 3/5/6 MUX_A0/A1/A2; 7 WING_EN; 9/11/13 MUX_OUT_A/B/C; MP mechanical NC**. Main's buses remain common; J2 pin7 and J3 pin7 remain independent EN0/EN1. Every harness cavity connects 1→1 through 14→14. [electrical-contract.json](electrical-contract.json) independently checks this, six returns, each seven-channel MUX bank, NC/S8 and local decoupling against `hardware/jitx/wing/definition.py`. No component or net role is inferred from a renamed pad.

The connector remains at the unchanged north-tab anchor **assembly (±27,−41)**. Rotation after bottom flip is **210° (−150°) left / 150° right** in native KiCad; tab/outline do not change. Pin1 centre is **(−18.875,−42.850) left / (35.125,−42.850) right** in case coordinates (native case XYZ coordinates). Pin14 is 16.25 mm toward −X from pin1. [Native physical probes](connector/placement.json) transform the actual footprint rear, front face and wire-exit probes through KiCad’s bottom flip and rotation, and assert the southward opening against the case model. This explicit coordinate convention avoids underside-view mirroring ambiguity; inspect cavity 1 against the mounting-surface drawing before cable fabrication. Native mm use X right/Y down; Wing-local is (X−100,100−Y).

## Routing trial and gates

`build.py` starts from round-1 native placements, independently for both pitches/sides. Each MUX and its decoupler moves **2 mm south in case coordinates**, rotates **180°**, and gets new escapes from KRT. The capacitors rotate about their MUX anchors before translation. All electronic parts and test pads stay B.Cu. Key/sensor/local Hall-cap coordinates and pad poses, holes, reservations and every outline segment are asserted invariant against round 1 in [placement-verification.json](placement-verification.json). [body-clearance.json](body-clearance.json) finds no overlap involving any service component's conservative body envelope. Main's native 62 F.Cu / zero B.Cu placements and source hash are in [main-unchanged.json](main-unchanged.json).

Rules remain D-021: **2 layers, 1.2 mm, signal 0.10 mm, power/GND 0.30 mm, clearance 0.10 mm, vias 0.60/0.30 mm, escalation off**. Complementary native-filled F HALL_5V / B GND pours are actual polygons in the independent graph. Southern restrictions and mounting copper reservations remain. Native power normalization precedes all gates; forbidden narrow power is never accepted.

| Variant | Native violations / opens | Independent four metrics¹ | Vias | Minimum via–pad, mm | Routing |
|---|---:|---|---:|---:|---|
| 16mm-left | 0 / 1 | 1 / 0 / 0 / 0 | 153 | 0.101340 | FAIL |
| 16mm-right | 0 / 0 | 0 / 0 / 0 / 0 | 142 | 0.133180 | PASS |
| 17mm-left | 0 / 0 | 0 / 0 / 0 / 0 | 124 | 0.125198 | PASS |
| 17mm-right | 0 / 0 | 0 / 0 / 0 / 0 | 134 | 0.116836 | PASS |

¹ Required unconnected / wrong-net contact / material violation / unexplained transfer. Every pad, including same-net, test and NPTH, participates in the via-pad audit; per-board `via-pad-all-pairs.csv.gz` is exhaustive. All boards have zero widths below the required floors and zero gaps below 0.10 mm. **0.125 mm-class target misses: 16mm-left (0.101340 mm), 17mm-right (0.116836 mm). The binding floor remains 0.10 mm; these target misses are explicit.** Neither that target miss nor a failing board is hidden in a global success label.

Bounded local repair reuses Rev.3's `plane-repair.py` and `cleanup.py`: native-shape clearance checks, actual filled-copper components, unchanged widths/vias. The fresh trials are diagnosed, power-normalized and locally repaired only where needed. Every final candidate is independently re-audited; there is no rule relaxation or net-name-only plane connection.

**16mm-left stop evidence:** required disconnected nets {'HALL_5V': 2}; native violations {}. See native DRC, blocking-regions.json, congestion-map.svg and local repair logs. The bounded second repair searches radial 0.30 mm bottom-side power escapes to the major physical power plane, checking every pad and existing drill, without removing foreign copper. It tests 2553 candidates and finds no legal landing for U_MUX_C.13. Stop after the bounded local trials; no voltage extraction is claimed for a disconnected board. Each variant's `initial-qualification.json` (where repair was needed), `plane-repairs.json`, optional `service-landing-search.json`, `blocking-regions.json`, congestion SVG and final PCB retain the evidence.


The verifier is the Rev.3 independent implementation with one explicit addition: manufacturer-footprint pad rows for the new `connector_ra` kind. No physical acceptance test is disabled. Native schematic ERC is unavailable because the inherited Wing package has no native schematic; the logical electrical-contract check is reported separately, not mislabeled ERC 0.

## Underside stack, connected route and mating

PCB underside **Z10**, top Z11.2, floor top **Z2** stay fixed. Header/plug nominal 4.35 mm leaves **3.65 mm floor gap**. A declared **0.50 mm assembled-height/solder/placement allowance** reserves 4.85 mm and still leaves **3.15 mm**, exceeding the 0.5 mm requirement. That allowance is an engineering budget, not a supplier tolerance certificate. Header/plug horizontal envelope reserves 0.5 mm outside the drawing. Hall depth 3.4 mm, MUX+solder 1.4 mm and capacitor 1.0 mm remain conservative reservations.

The actual wire outlet is modeled at **Y−35.45**, obtained from header rear Y−42.6 plus the 7.15 mm mated length, rather than round 1's hypothetical (±27,−41,Z5). Wire-axis **Z8.4** is a drawing-derived planning value with **±0.5 mm uncertainty**, not a dimension quoted by JST. At worst the 1.0 mm wires have 0.6 mm PCB clearance at their exits. Fourteen individual 1.0 mm wires leave horizontally, fan in/down through R5 bends, and join the conservative Ø5 lower route. The bundled waypoints are **(±27,−24,5), (±7,−16,5), (±7,−16,28.5), (±15.5,43,28.5), (±15.5,43,18.5)**. The fanout ends on the common segment at (±14,−18.8,5); its exported geometry overlaps the bundle as a connected envelope. Every individual route includes the actual exit and common Main termination.

[case/summary.json](case/summary.json) gives wire-by-wire R5 lengths, collision volumes and source hashes. The sweeps check original tray solids, PCB solids, all conservative keycaps, component bodies, Main Rev.6 native footprint bounds, joining hardware and all E-R posts. Only each intended Main mating envelope is exempted from its own cable. There are no modeled non-tray body collisions or post overlaps. **The Ø5 channel has 0.5 mm nominal floor clearance. This is a controlled maximum-OD planning envelope; installed wire dressing, channel position, full housing/latch tolerances and that nominal channel margin still need physical acceptance. It is not a tolerance-certified complete harness.**

| Variant | Longest connected conductor path, mm | +30 mm service, mm | Tray material removed, mm³ | Full route overlap after proposal, mm³ |
|---|---:|---:|---:|---:|
| 16mm-left | 123.395 | 153.395 | 69.640 | 0.000000 |
| 16mm-right | 123.395 | 153.395 | 69.957 | 0.000000 |
| 17mm-left | 123.395 | 153.395 | 69.640 | 0.000000 |
| 17mm-right | 123.395 | 153.395 | 69.956 | 0.000000 |

The original internal wall overlaps the full cable by **~44.13 mm³ left / ~44.18 mm³ right**, near **|X|8.49–15.85, Y−20.89…−14.91, Z2.50…7.62**. Each `tray-*-channel-candidate.step` is a **study-only proposal**, cut with the **Ø6 / R5** path (0.5 radial clearance around Ø5). It is one valid solid, removes zero volume from Z0–2, and gives zero full-route overlap. This is a revised opening shape and position compared with round 1, connected to the real fanout. Production case files are untouched. [Saved STEP replay](case/verification.json) independently reloads the bundle, individual wires and candidate tray. The proposal's structural/printing acceptance is a later case gate.

No E-R post moves: minimum shaft-to-native-pad/drill gap is **0.460 mm (16 pitch)** / **0.627 mm (17 pitch)**; all six posts per Wing, collars, moved service bodies and actual harness are rescreened in each pitch's `post-rescreen.json`. The route does not cross split X3.5, intersect splice hardware or need a top plate connector opening. The original Main rise remains the only end rising above its board. Fly is rerun against these actual GH paths in each pitch's `fly.json`; its stock 170 mm storage is still not qualified.

**Mating procedure in the model:** [pre-mating STEP poses and procedure](case/mating-procedure.json) hold the unswitched Wing outside/above the tray at underside Z35; GHR slides horizontally north through an 8 mm free-space approach, then latches. Check L/R and cavity 1, push the housing rather than wires, and leave Main free. Dress the fanout/channel, lower the prewired Wing to Z10 while feeding Main's end into the central bay, seat four mounts/six supports, fasten, then mate Main from above. Install switches/full-cover plate afterward. Power off and lift the Wing before underside unlatching for service. The fixture's reserved minimum Z30.15 is 4.95 mm above conservative cap tops; this demonstrates pre-mating access, while flexible-wire seating remains a practical assembly check rather than a rigid-body motion certification.

**Length decision:** longest modeled wire **123.395 mm**, plus 30 mm service gives **153.395 mm**. D-033's **200 mm** stays unchanged: it leaves **76.605 mm beyond the path**, of which 30 mm is the explicit service allowance and **46.605 mm has no demonstrated storage**. The former elevated GH rack is not counted. This supplies the requested ~154 mm-class input; it does not authorize a shortened cable order. Specify final cut-length/contact datums with the fabricator after physical dressing and the PO length/storage decision. No 200 mm loop-storage qualification is claimed.

## Electrical requalification of routing passes

Fresh `extract-resistance.py` solves actual saved copper/pads/via barrels at **127 mA distributed load** using the Rev.3 load proportions, 35 µm copper, 20 µm barrel, nominal/80% track width and **0.06 / 0.015 mm²** coarse/fine meshes. Source board hashes are enforced. All eight cases per passing board complete; maximum mesh difference is 1.118% of worst drop (Rev.3 limit 3%) and KCL residuals below 1 µA. [fem-selfcheck.json](fem-selfcheck.json) repeats the rectangular analytic-sheet checks with ~1e-15 relative error. The other Rev.3 applicable Wing checks—pin transforms, seven-channel grouping, unused pins, decoupling, southern routing band, power floors, mounting exclusions, via sizes, wrong-net contact and transfer invariants—are repeated by the native/independent and logical audits. Magnetic response, ADC noise/settling and assembled resistance remain physical evaluation, as in Rev.3.

| Passing board | Nominal far terminal | 20°C loop drop, mV | Effective loop resistance, mΩ | Worst 200 mm Vfar, V² |
|---|---|---:|---:|---:|
| 16mm-right | U_HC3 | 1.337 | 10.526 | 4.943619 |
| 17mm-left | U_HC6 | 11.345 | 89.330 | 4.926366 |
| 17mm-right | U_HC6 | 7.114 | 56.018 | 4.933577 |

² Both Main branches are evaluated for each candidate on the same historical comparison yardstick, even though the actual assembly branch is J2 left / J3 right. Keep the reference's Main #196 common/branch resistance, two simultaneous Wings, 5.2 V ±2%, 50 mV unmodeled budget, U5 0.25 Ω, six AWG28 returns and 50 mΩ/contact ×2. This compares Wing copper, not a fresh qualification of current Main Rev.6. [power-summary.json](power-summary.json) / [power-sensitivity.csv](power-sensitivity.csv) include 20/125°C, both widths, the 124.097 mm reference, actual connected length and **200 mm** specification. The 125°C sensitivity is not an approved GH assembly operating temperature.

Worst **4.926366 V** at 200 mm versus Rev.3 **4.942903 V**: **16.537 mV lower**, but **0.326366 V above 4.60 V**. No Rev.3 voltage result is transferred without fresh Wing extraction. These are numerical design results, not measured minimum-material guarantees or manufacturing approval.

## Reproduction and inspection

From repository root:

```bash
E=hardware/kicad/qualification/issue-235-wing-round2
python3 "$E/reproduce.py"
# Read-only consistency check of saved artifacts and production inputs:
python3 "$E/verify-study.py"
```

The corrected southward native connector pose is asserted by `connector-pose-check.py` before routing. `case/placement-refresh.json` records the refreshed pad/post screen; the already modeled southward body/route and saved STEP replay remain unchanged.

`setup-runtime.py` uses installed read-only KiCad/KRT/geometry/CAD tools; [toolchain.json](toolchain.json) pins KiCad 9.0.9, KRT source/core and the Rev.3 grid-search binary. Override KICAD_ROOT, GEOMETRY_SITE, ROUTER_PYTHON, KRT_HOME CAD_PYTHON and GRID_SEARCH for another host. All scratch, logs, XDG state, Python temporary files and the private Git database stay in `.issue235-runtime/`; no `/tmp` scratch is used. [attempt-plan.json](attempt-plan.json) records bounded launches/repairs, including the interrupted setup launches; current saved copper is accepted only against immutable native inputs, not router status. Routing can produce different UUIDs; every regenerated candidate must repeat all gates.

Each variant directory delivers native input/routed/final diagnostic PCB/project, logs, definition, native DRC, independent qualification, all-pairs via audit and congestion SVG/JSON. A failing board keeps failure evidence; passing boards keep fresh electrical extraction. Case STEP files are study geometry, never a production-case edit or manufacturing package. [verification.json](verification.json) binds these saved artifacts and inputs; evidence consistency is distinct from four-variant design qualification.

Remaining adoption gates: close **16mm-left** without relaxing rules; improve any via-pad target misses; validate actual housings/wire dressing and channel tolerances; approve the tray passage and structural implications; resolve **200 mm storage versus ~153 mm procurement input** (and separate Fly storage/length); then obtain the PO Rev.4/assembly-method adoption gate. Main, D-021/D-024/D-033/D-038 and production baselines remain unchanged.
