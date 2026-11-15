# Issue #248 Phase B — production-intent GH low deck / raised keyless case

**PROVISIONAL: every CAD, mesh, drawing, audit, dimension and cost in this tree is conditional on the single named `plateau_top_z_mm = 24.65` parameter, based on unmeasured Junana q=1.50. NOT RELEASED.** The latest Issue #248 comments, including PO's GH Phase B GO, were read first and are frozen in [sources/issue248-go.json](sources/issue248-go.json). GH stays; DF52/SH are not reopened. All prior study trees remain untouched. This package delivers fitted candidates and the complete audit, including failed gates; it does not convert a failed audit into approval to manufacture.

| Gate | 17 mm primary | 16 mm verification |
|---|---|---|
| 1 Exhaustive fitted collision | FAIL | FAIL |
| 2 Conductors and dressed target | FAIL | FAIL |
| 3 Accessible ~30 mm service | FAIL | FAIL |
| 4 Connected Fly 170 / R5 / roof gap | PASS | PASS |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps after allowances | FAIL | PASS |
| 7 Print envelopes and manufacturing data | FAIL | FAIL |
| 8 Fitted preview STEP | PASS | PASS |

The physical full-press Junana skirt-to-plate test remains **OPEN** at both pitches. The provisional q is not a measured cap height or a production tolerance bound. Read the failed-gate blockers below before using manufacturing files.

## Geometry, material ownership and invariants

Plate top is Z13.55; Main and Wing PCB undersides remain Z7.35. Main Rev.7 and Wing Rev.4, GH placements, aluminium plate shape/thickness and the board-to-plate stack are preserved by rigid translation −2.65 from #232. The case floor remains at Z0, nominal floor top Z2. Trays and all twelve E/R support posts are remade by removing the neutral Z3…5.65 band; upper seats move down 2.65 while floor and post sockets remain. Floor-level splices, screws and rubber feet stay at their original floor datum. Manufacturing support-post pegs retain the source 3.15 mm free diameter and 0.6 mm split; fitted pegs retain the 3.10 mm compressed diameter in 3.10 mm sockets. These are distinct print and installed states, with unchanged 0.8 mm socket depth and 1.2 mm floor remaining. `invariants.json` compares the fitted boards/plates and the continuous south palm band against their source. No input PCB or aluminium manufacturing file is edited.

The slope exterior is one plane between **Y1.935592550 and Y38.514430874**, with straight X-parallel breaks. The 18 mm wells remain; outer/palm/thumb margins stay at plate height. North strips end at the start line. A4's overlapping plateau/strip polygons are a surface union; B assigns common material to the strips, rather than physically superposing printed parts. Small north wall tongues are assigned to the adjoining strip only after a zero-distance, valid single-solid union check. All original material is retained unless explicitly identified as an obsolete detached tray rim nib. The 16 mm disconnected south shell section is retained and reported; it is not silently discarded or joined through a key well.

Nominal PETG walls and **normal** roof thickness are 2.00 mm. Consequently the slope's vertical thickness is 2.090056857 mm: 0.090056857 more underside intrusion than B0's 2 mm vertical study skin. This is an explicit implementation interpretation of the requested 2 mm roof; the A4 exterior plane and datums are unchanged. It is applied to clearance audits, rather than borrowing B0's clearance verdicts.

Both Main GH projections use the B1 drawing-bounded seated header/plug model, ceiling **Z13.20**, top **Z15.20**, maximum rise 1.65. These are nominal manufacturer drawing bounds, not unpublished moulding cavities or certified production maxima. The baseline Fly storage uses ceiling **Z13.25**, top **Z15.25**, maximum rise 1.70. Blister blend masks extend 0.50 mm north under the already higher slope to recover true 0.30 mm clearance with the normal 2 mm skin; this does not raise the specified blister tops or alter the exterior slope plane. Walls stand outside the obstacle +0.30 clearance footprint. South screw/spacer openings are **Ø5.10** at **(−31.892683,64.40)** and **(+31.892683,64.40)**; the adopted right hardware's 1e−6 mm asymmetry is retained in the hardware, not substituted for the requested hole centre. Those screws retain Main, not the shell.

The case uses #246's X−5/12 → X0/15 splice-screw relocation at Y−8/55, with lower floor-rooted Ø7 bosses, top Z5.50 and Ø1.70 pilots. Changed splices keep their original print pattern and gain the new Ø2.20 clearance holes. Case-only grooves follow the dedicated wires with 0.87 mm projected radius; the wire solids remain exact R5 sweeps. Subtractions never alter a PCB or plate. Routing can isolate obsolete rim nibs; `geometry-finish.json` records their explicit regions, bounds and removed volume. Topology repair is accepted only when valid and volume change <1e−6 mm³. No tolerance is enlarged and no arbitrary largest-solid filter is used.

## Retention and service design

The central shell uses **two independent north M2 retainers at (±8,−30)**. Both nominal OD3.2 ×4.0 heat-insert annular bounds are included in the fitted STEP and full pair accounting; knurls and thread microgeometry are not reconstructed. Each has a floor-rooted Ø6 pillar ending at Z22.65, a 2.8 mm heat-insert pilot over its top 4 mm, a 2.2 mm shell clearance and 4.0 mm head recess. The nominal low-head screw envelope is Ø3.6 × 1.0, under-head length 4 mm, with 3 mm engagement into the insert. Procurement must meet that envelope; no supplier quote or validated insert pull-out value is claimed. The south Ø5.10 openings carry no retention load. The bay-seat trim initially truncated the north pillars; the final model restores their full floor-to-Z22.65 load path. Two intentional keyless side-wall service openings, X9.7…12.1 mirrored left and Y−33.3…−26.7, run from plate level to the roof underside. They clear the fixed pillars while retaining the 2 mm roof and the nominal 2 mm walls elsewhere; the shell can lift without dragging over the pillars.

Each strip bears on the unchanged keyless north deck through its 2 mm perimeter walls. Two 2 mm tabs per strip at Y−40/−23 extend X8…14 (mirrored left), below the central roof with 0.30 mm clearance. Open-bottom slots let the central shell lift vertically. Upward strip loads pass through the captured tabs into the central roof, its north screws, inserts, pillars and tray floor. Downward roof loads pass through walls to the deck/rim and through the north pillars; south rim contact must be assessed with the collision evidence. The two-retainer local 10 N screen gives 5 N per screw, about 2.49 MPa on a nominal Ø1.6 screw section. This is not whole-shell bending, tab fatigue, insert pull-out or physical inversion qualification; fitted contacts and disconnected geometry prevent release where reported.

Service: disconnect external USB; remove the two north shell screws and lift the central cap; lift the two independent strips. Wing boards, plate screws, posts and spacers remain fitted. Release Main GH latches and withdraw along their outward mating axes; disconnect Main EZmate, remove Main's own H1 and south hardware/loose spacers, then lift Main. Retain the Fly cable in its dressed storage pose. Access each connected U through the open Main bay and move its turn continuously Y22.1→7.00, recovering 30.20 mm into the disconnected Main end. Reverse this procedure, redress the U to Y22.1, seat the caps and tighten their north screws. This is the proposed procedure: only the gate table can certify its fitted/motion feasibility.

The dedicated route has fourteen OD1 conductors per side, horizontal Wing Z5.75 and Main Z10.65 outlet dress axes, R≥5 throughout, no detached reserve; the curves end at nominal outlet dress planes. Outlet axes are nominal paths inside the drawing-bounded faces, not measured individual GH cavity centres. The candidate 4/3/4/3 lower pack sits at Z4.90 in the Main bay, rises north of Main inside the central neck, then traverses at nominal Z14.80 with separated upper offsets. **Unresolved routing deviation:** this candidate aggregates strands at X±27/Y−24 before completely clearing the Wing north corridor. The audit exposes contacts with fixed Wing MUX bounds, retained E/plate screws, plates and other strands. Those are failures, not approved local cuts or allowed harness self-overlaps. The intended separated-wire corridor has not been qualified by this candidate. **Deviation from the first-pass packing suggestion:** reserve is stored below Main at Y7…22.1, south of the north neck, rather than above the deck near Y25…45. This saves routed length and avoids allocating the same volume to two high loops. **Length gate blocker:** the internal wire tip/crimp reference planes are not dimensioned by the bounded outlet model. The earlier routed lengths omit those tails. A deliberately conservative 5.70 mm per end, using B1's plug tip-to-wire-end bound, produces 201.151412 / 202.169482 mm full cut bounds and 170.951412 / 171.969482 mm dressed cut bounds. Both the full and dressed qualifications therefore remain failed; the routed-only margins are not claimed as finished-conductor margins. No terminal length is silently set to zero. It is not claimed accessible merely because 30.20 mm is represented. The service audit uses a continuous filled cap-motion strip for every strand with 0.020 mm excess envelope, and checks retained Wing stacks, case, the other harness and the dressed Fly cable.

## Failed gates and full evidence

Every unexpected fitted pair and Boolean error is retained in each pitch's `audit.json`; motion blockers are in `service.json`; USB blockers in `usb.json`; cap witnesses in `caps.json`. The unmodified aluminium plate and 2 mm slope/low roofs are audited as separate bodies. Any overlapping material remains a failed gate; it is not waived as a mating contact. This exposes whether the settled exterior, full roof thickness and unchanged plate can coexist at the slope-to-deck transition. The retained M2x12 E-stack screw models also reach 0.15 mm into the floor after lowering; this is an unresolved hardware-length mismatch, not a permitted thread contact. Their replacement length and engagement have not been qualified by this candidate. No plate notch, reduced skin, smaller cap, shorter cable or higher deck is introduced to conceal a failure.

## 17 mm evidence

- **1 Exhaustive fitted collision: FAIL.** 305 unexpected contacts; 0 Boolean errors; see audit.json
- **2 Conductors and dressed target: FAIL.** Outlet routes pass, but crimp tails are unsourced. Conservative 5.70 mm/end bound: L 201.151412, R 202.169482 mm; full/dressed limits unclosed
- **3 Accessible ~30 mm service: FAIL.** 30.20 mm represented; motion blocked; accessible certification requires fitted audit and invariants
- **6 Assumed swept caps after allowances: FAIL.** Minimum reported after 0.50 allowance -0.500000 mm; physical skirt gate OPEN; kernel reports zero distance with witnesses outside shell bounds, so no physical-contact or clearance verdict is certified
- **7 Print envelopes and manufacturing data: FAIL.** Independent STEP/STL failures: shell-central: 1 solids, 12 nonmanifold STL edges, relative volume error 1.44980838e-07

| Side | Outlet route max mm | Full cut upper bound mm | Bound margin to 200 | Routed dressed max mm | Dressed cut upper bound mm | Represented reserve mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 189.751412 | 201.151412 | -1.151412 | 159.551412 | 170.951412 | 30.200000 |
| right | 190.769482 | 202.169482 | -2.169482 | 160.569482 | 171.969482 | 30.200000 |

Collision audit: **366 physical constituents, 66795 unordered pairs**, 65061 AABB rejects, 160 explicit own-mate pairs, 1574 completed exact Commons. Threshold stays 1e−6 mm³. No early stop. 0 operation-level Boolean errors. Where present, `retention-completion.json` proves the unchanged operand prefix for the insert addition, and `support-restoration.json` records the subsequent three-component correction. Every pair involving a changed tray or shell is recomputed; exact results are resumed only when both serialized operand hashes are unchanged. Every final insert pair is enumerated and classified. Fresh builds archive checkpoint-transition proofs and perform their own complete audit. `verify_package.py` independently replays coverage of the entire final broadphase, including these additions. Individual OD1 strands are checked against each other; their intersections are not waived as a shared nominal bundle envelope. Full pair results and all witnesses by constituent name are in [17mm/audit.json](17mm/audit.json). Positive component-bound overlaps are listed separately, as in #246; they do not disappear from the evidence. Inherited official Fly source invalidities remain labelled, and never justify a new case or wire collision.

Contact categories:

- conductors / conductors: 170 constituent contacts
- aluminium plates / their fitted hardware / conductors: 36 constituent contacts
- conductors / shell-central: 28 constituent contacts
- Wing underside bounds / conductors: 17 constituent contacts
- conductors / strip-left: 14 constituent contacts
- conductors / strip-right: 14 constituent contacts
- aluminium plates / their fitted hardware / trays: 8 constituent contacts
- aluminium plates / their fitted hardware / shell-central: 8 constituent contacts
- conductors / joint-screw-1-12_0: 2 constituent contacts
- aluminium plates / their fitted hardware / strip-left: 2 constituent contacts
- shell-central / trays: 2 constituent contacts
- aluminium plates / their fitted hardware / strip-right: 2 constituent contacts
- POM-left-H3 / shell-central: 1 constituent contacts
- POM-right-H1 / shell-central: 1 constituent contacts

Continuous service motion:

- left: 18 motion contacts, 0 Boolean errors; `service.json` lists every part/wire.
- right: 18 motion contacts, 0 Boolean errors; `service.json` lists every part/wire.

Local measure replay ([local-measures.json](17mm/local-measures.json)): cover-Main-spacer-2: gap 0.300000 mm, Common 0.000000 mm³; cover-screw-2: gap 0.550000 mm, Common 0.000000 mm³; cover-Main-spacer-3: gap 0.299999 mm, Common 0.000000 mm³; cover-screw-3: gap 0.549999 mm, Common 0.000000 mm³; Main-GH-left-DRAWING-BOUND: gap 0.000000 mm, Common 0.000000 mm³; Main-GH-right-DRAWING-BOUND: gap 0.300000 mm, Common 0.000000 mm³. The 17 mm left GH zero-distance result is subject to the same unresolved central-shell classifier ambiguity; zero Common alone does not certify its 0.30 mm gap. The right south-spacer 0.299999 mm result records the inherited 1e−6 mm axis asymmetry against the requested symmetric hole centres; dimensions are not silently enlarged.

Fly: one valid connected swept solid, **170.000000000 mm**, R5, volume error 0.000000000 mm³ against 170π, minimum true shell distance **0.300000 mm**. Its fitted contacts with other bodies are separately applied to gate 4. USB results enumerate all three shell/overmold/exit reservations and their full 30 mm travel. Caps: all 42 assumed 16 mm swept envelopes are tested against the actual shells, strips and blisters with a 0.50 mm combined allowance; the solver reports worst remaining gap **-0.500000 mm**. For 17 mm, zero-distance witnesses outside the central shell's bounds make this an **uncertified kernel result**, not proof of a physical cap contact. `cap-witnesses.json` preserves the inconsistent points. The physical skirt/full-press gate also remains open.

| Print | Solids | Valid | XYZ including 5 mm XY brim, mm |
|---|---:|---|---|
| splice-1 | 1 | yes | 38.000 × 26.000 × 4.200 |
| splice-2 | 1 | yes | 38.000 × 26.000 × 4.200 |
| post-left-R1 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R2 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R3 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R4 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R5 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R6 | 1 | yes | 14.500 × 14.500 × 6.150 |
| tray-left | 1 | yes | 159.021 × 156.069 × 22.650 |
| post-right-R1 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R2 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R3 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R4 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R5 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R6 | 1 | yes | 14.500 × 14.500 × 6.150 |
| tray-right | 1 | yes | 152.021 × 156.069 × 22.650 |
| strip-left | 1 | yes | 127.425 × 76.302 × 11.100 |
| strip-right | 1 | yes | 127.425 × 76.302 × 11.100 |
| shell-central | 1 | yes | 169.338 × 145.364 × 13.190 |

STEP/STL meshes are independently reloaded in [17mm/export-verification.json](17mm/export-verification.json), including edge manifoldness, degeneracies and volume agreement. [shell-diagnostics.json](17mm/shell-diagnostics.json) localizes each rejected mesh edge and records every shell solid's volume and bounds. At 17 mm the twelve nonmanifold edges block slicing qualification even though the STEP reports one valid solid. At 16 mm the disconnected south section (1772.22 mm³, reported separation 0.20 mm) blocks qualification as one printable central shell. Repairing these would require validated topology reconstruction or a geometric connection that passes all unchanged gates; no mesh welding, material deletion, bridge through a key well or relaxed edge test is used. A multi-solid print remains failed even when its bounding envelope fits. Each print has an SVG drawing and the numerical dimension register. All geometry is in assembly coordinates; translate each print's lowest Z to the bed in the slicer. The fitted preview is [17mm/fitted-assembly-PROVISIONAL.step](17mm/fitted-assembly-PROVISIONAL.step).

Planning cost for the **printed case set plus new retention**: 200.9 g nominal PETG, 251.1 g with support/waste; **USD 7.02–13.53** material/hardware cash allowance. Estimated printer time 8.2–16.5 h. With USD1/machine-hour and USD20 assembly/finishing allowance: **USD 35.26–50.01**. These are arithmetic planning allowances, not quotes, and do not include a rerun of a rejected design. Unchanged aluminium plates and electronics are excluded. [17mm/cost-estimate.json](17mm/cost-estimate.json) records every assumption.
## 16 mm evidence

- **1 Exhaustive fitted collision: FAIL.** 309 unexpected contacts; 0 Boolean errors; see audit.json
- **2 Conductors and dressed target: FAIL.** Outlet routes pass, but crimp tails are unsourced. Conservative 5.70 mm/end bound: L 201.151412, R 202.169482 mm; full/dressed limits unclosed
- **3 Accessible ~30 mm service: FAIL.** 30.20 mm represented; motion blocked; accessible certification requires fitted audit and invariants
- **7 Print envelopes and manufacturing data: FAIL.** Independent STEP/STL failures: shell-central: 2 solids, 0 nonmanifold STL edges, relative volume error 1.49045604e-07

| Side | Outlet route max mm | Full cut upper bound mm | Bound margin to 200 | Routed dressed max mm | Dressed cut upper bound mm | Represented reserve mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 189.751412 | 201.151412 | -1.151412 | 159.551412 | 170.951412 | 30.200000 |
| right | 190.769482 | 202.169482 | -2.169482 | 160.569482 | 171.969482 | 30.200000 |

Collision audit: **367 physical constituents, 67161 unordered pairs**, 65404 AABB rejects, 161 explicit own-mate pairs, 1596 completed exact Commons. Threshold stays 1e−6 mm³. No early stop. 0 operation-level Boolean errors. Where present, `retention-completion.json` proves the unchanged operand prefix for the insert addition, and `support-restoration.json` records the subsequent three-component correction. Every pair involving a changed tray or shell is recomputed; exact results are resumed only when both serialized operand hashes are unchanged. Every final insert pair is enumerated and classified. Fresh builds archive checkpoint-transition proofs and perform their own complete audit. `verify_package.py` independently replays coverage of the entire final broadphase, including these additions. Individual OD1 strands are checked against each other; their intersections are not waived as a shared nominal bundle envelope. Full pair results and all witnesses by constituent name are in [16mm/audit.json](16mm/audit.json). Positive component-bound overlaps are listed separately, as in #246; they do not disappear from the evidence. Inherited official Fly source invalidities remain labelled, and never justify a new case or wire collision.

Contact categories:

- conductors / conductors: 170 constituent contacts
- aluminium plates / their fitted hardware / conductors: 36 constituent contacts
- conductors / shell-central: 28 constituent contacts
- Wing underside bounds / conductors: 17 constituent contacts
- conductors / strip-left: 14 constituent contacts
- conductors / strip-right: 14 constituent contacts
- aluminium plates / their fitted hardware / shell-central: 10 constituent contacts
- aluminium plates / their fitted hardware / trays: 8 constituent contacts
- shell-central / trays: 4 constituent contacts
- conductors / joint-screw-1-12_0: 2 constituent contacts
- aluminium plates / their fitted hardware / strip-left: 2 constituent contacts
- aluminium plates / their fitted hardware / strip-right: 2 constituent contacts
- POM-left-H3 / shell-central: 1 constituent contacts
- POM-right-H1 / shell-central: 1 constituent contacts

Continuous service motion:

- left: 18 motion contacts, 0 Boolean errors; `service.json` lists every part/wire.
- right: 18 motion contacts, 0 Boolean errors; `service.json` lists every part/wire.

Local measure replay ([local-measures.json](16mm/local-measures.json)): cover-Main-spacer-2: gap 0.300000 mm, Common 0.000000 mm³; cover-screw-2: gap 0.550000 mm, Common 0.000000 mm³; cover-Main-spacer-3: gap 0.299999 mm, Common 0.000000 mm³; cover-screw-3: gap 0.549999 mm, Common 0.000000 mm³; Main-GH-left-DRAWING-BOUND: gap 0.300000 mm, Common 0.000000 mm³; Main-GH-right-DRAWING-BOUND: gap 0.300000 mm, Common 0.000000 mm³. The 17 mm left GH zero-distance result is subject to the same unresolved central-shell classifier ambiguity; zero Common alone does not certify its 0.30 mm gap. The right south-spacer 0.299999 mm result records the inherited 1e−6 mm axis asymmetry against the requested symmetric hole centres; dimensions are not silently enlarged.

Fly: one valid connected swept solid, **170.000000000 mm**, R5, volume error 0.000000000 mm³ against 170π, minimum true shell distance **0.300000 mm**. Its fitted contacts with other bodies are separately applied to gate 4. USB results enumerate all three shell/overmold/exit reservations and their full 30 mm travel. Caps: all 42 assumed 16 mm swept envelopes are tested against the actual shells, strips and blisters with a 0.50 mm combined allowance; the solver reports worst remaining gap **0.500000 mm**. For 17 mm, zero-distance witnesses outside the central shell's bounds make this an **uncertified kernel result**, not proof of a physical cap contact. `cap-witnesses.json` preserves the inconsistent points. The physical skirt/full-press gate also remains open.

| Print | Solids | Valid | XYZ including 5 mm XY brim, mm |
|---|---:|---|---|
| splice-1 | 1 | yes | 38.000 × 26.000 × 4.200 |
| splice-2 | 1 | yes | 38.000 × 26.000 × 4.200 |
| post-left-R1 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R2 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R3 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R4 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R5 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-left-R6 | 1 | yes | 14.500 × 14.500 × 6.150 |
| tray-left | 1 | yes | 152.318 × 149.558 × 22.650 |
| post-right-R1 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R2 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R3 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R4 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R5 | 1 | yes | 14.500 × 14.500 × 6.150 |
| post-right-R6 | 1 | yes | 14.500 × 14.500 × 6.150 |
| tray-right | 1 | yes | 145.318 × 149.558 × 22.650 |
| strip-left | 1 | yes | 121.729 × 73.266 × 11.100 |
| strip-right | 1 | yes | 121.729 × 73.266 × 11.100 |
| shell-central | 2 | yes | 160.615 × 140.513 × 13.190 |

STEP/STL meshes are independently reloaded in [16mm/export-verification.json](16mm/export-verification.json), including edge manifoldness, degeneracies and volume agreement. [shell-diagnostics.json](16mm/shell-diagnostics.json) localizes each rejected mesh edge and records every shell solid's volume and bounds. At 17 mm the twelve nonmanifold edges block slicing qualification even though the STEP reports one valid solid. At 16 mm the disconnected south section (1772.22 mm³, reported separation 0.20 mm) blocks qualification as one printable central shell. Repairing these would require validated topology reconstruction or a geometric connection that passes all unchanged gates; no mesh welding, material deletion, bridge through a key well or relaxed edge test is used. A multi-solid print remains failed even when its bounding envelope fits. Each print has an SVG drawing and the numerical dimension register. All geometry is in assembly coordinates; translate each print's lowest Z to the bed in the slicer. The fitted preview is [16mm/fitted-assembly-PROVISIONAL.step](16mm/fitted-assembly-PROVISIONAL.step).

Planning cost for the **printed case set plus new retention**: 186.7 g nominal PETG, 233.4 g with support/waste; **USD 6.67–13.00** material/hardware cash allowance. Estimated printer time 7.7–15.3 h. With USD1/machine-hour and USD20 assembly/finishing allowance: **USD 34.33–48.32**. These are arithmetic planning allowances, not quotes, and do not include a rerun of a rejected design. Unchanged aluminium plates and electronics are excluded. [16mm/cost-estimate.json](16mm/cost-estimate.json) records every assumption.

## Files and reproduction

The continuation run resumed the retained final geometry without restarting the design. It re-read the live Issue #248 and all nine comments through the connected GitHub tool after the CLI network request was blocked, completed both collision witness maps, bound them to the final geometry hashes, localized the shell export failures, and regenerated this report and its manifests. The full fitted audit and independent export reload from the interrupted run are retained; their hashes, complete pair coverage and final preview inventories are independently checked by `verify_package.py`. The continuation does not claim a fresh complete CAD rebuild or convert any failed gate into a pass.

Both pitch directories contain the fitted STEP, manufacturing STEP/STL/SVG for all nineteen printed parts, a dimension register, connected service-motion STEP envelopes, and raw gate evidence. PROVISIONAL is embedded in manufacturing filenames, STEP labels, STL headers and drawings. Plate drawings/manufacturing remain the unchanged D-038 package in #232; they are not reissued as printed plates. `parameters.json` is the single plateau-height authority. `artifact-sha256.json` binds this report, scripts and outputs; `inputs-sha256.json` binds all source CAD, layouts and PCB inputs. The runtime git contains checkpoint commits; no push, purchase or production release is performed.

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` from the worktree with the existing CAD Python environment. All scratch, source BRep caches, audit checkpoints and logs stay in `.issue248-runtime/`; no `/tmp` scratch is used. Each stage is separate to bound memory. Exact audits checkpoint progress and resume only when the geometry-index hash matches. Do not reuse any PASS from a prior geometry or prior study. The independent export verifier and full-pair accounting are part of the final run. After report generation, run `/usr/bin/python3 hardware/case/issue-248-phaseb/verify_package.py` for dependency-free input/artifact hashes, print-file hash consistency and complete unordered-pair coverage.
