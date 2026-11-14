# Issue #248 Phase B — tuning continuation

**PROVISIONAL on plateau Z24.65 / unmeasured Junana q=1.50. NOT RELEASED.**

This tuning candidate closes only the gates shown as PASS. It does not complete the requested all-clear wiring/service design. The original first-candidate report and evidence remain byte-preserved in [first-candidate/](first-candidate/REPORT.md). PO comments were reread with `gh issue view 248 --comments`; the continuation snapshot is in sources/issue248-continuation.json.

| Gate | 17 mm primary | 16 mm verification |
|---|---|---|
| 1 Exhaustive fitted collision | FAIL | FAIL |
| 2 Finished conductors ≤200 mm | PASS | PASS |
| 3 Accessible ~30 mm service | FAIL | FAIL |
| 4 Connected Fly 170 / R5 / roof gap | PASS | PASS |
| 5 USB 30 mm insertion | PASS | PASS |
| 6 Assumed swept caps after allowances | PASS | PASS |
| 7 Print envelopes and manufacturing data | PASS | FAIL |
| 8 Fitted preview STEP | PASS | PASS |

## Kept and discarded interrupted work

See [WIP-INVENTORY.md](WIP-INVENTORY.md). Starting at 47f7dd5, uncommitted 17 mm hardware/geometry metadata, cap audit source, boundary regularization and hardware replacement code were inventoried and checkpointed early (aba62a9). M2×10 qualification and the cap audit were kept, rerun and extended to both pitches. The 17 mm shell boundary repair was kept and independently export-verified. Its intermediate two-solid diagnostic is superseded by final geometry diagnostics; the diagnostic is not a final claim. Experimental routes_tuning.py / transport.py remain as rejected development source, not fitted routes. Their fan crossings prevented adoption. Python caches were excluded. Runtime scratch and starting geometry snapshots remain in .issue248-runtime/tuning; no /tmp scratch was used.

Original E-boss regions were restored after a stricter engagement-material audit exposed damage from projected route cuts; the interrupted nominal-only engagement check was insufficient and is superseded. All changed-tray pair and service checks were rerun. The current `routes.py` replaces the early X±27/Y−24 merge with separated outlet lanes through the Wing north corridor, a lower fan into the neck, and concentric reserve turns. The long stored turn was moved from Y22.1 to Y17.1; its released reference is Y2.0, preserving 30.20 mm. This saves routed length. The final audit still rejects unresolved fan/upper-route and fixed-part contacts: no new route is described as qualified on length alone.

## Unchanged inputs and explicit deviations

Deck Z13.55; board undersides Z7.35; plateau Z24.65 provisional q=1.50; slope breaks Y1.935592550 / Y38.514430874; boards, aluminium plates and board/plate stack remain unchanged. Existing PCB and plate manufacturing files are byte-checked against inputs-sha256.json before report/manifests regenerate. Actual fitted invariants and the protected south palm band are recomputed. GH remains the connector. Fly remains one connected 170 mm R5 cable. No thinner skin, changed cap, raised deck or changed well is introduced.

Roofs use **2.00 mm normal thickness**; the slope's vertical thickness is 2.090056857 mm. Main GH blisters retain ceiling/top Z13.20/15.20; Fly Z13.25/15.25; Ø5.10 south openings and north shell retention remain. Case channels are cut only from trays, with the full source floor band restored through Z2 before remaking splice pilots. All local relief is recorded; no gate tolerance is enlarged. Detached north tongues are assigned by explicit geometric adjacency, never a largest-solid filter. The 16 mm south section is not deleted or bridged across a key well.

Length uses a **3.40 mm nominal internal wire upper bound per end**, plus the 0.50 mm Wing external dress lead, from the [JST GH manufacturer drawing](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf), readable repository archival figure on printed page 2. Exact dress-plane definition and derivation are in [tail-source.json](tail-source.json): housing mouth to cut copper end; 5.70 housing axial length minus protected 2.30 mating section. Wing actual mouth is Y−35.45 (#235: header rear −42.60 + seated 7.15); this candidate starts at Y−34.95, so another 0.50 mm is explicitly included. Total unrouted bound is 7.30 mm (Wing 3.90 + Main 3.40). This assumes a correctly seated terminal whose nose does not protrude past the housing mating tip and a wire end that does not invade the mating section. It is a drawing-derived bound, not a measured crimp or a production tolerance guarantee. The 2.10 mm crimp-region and 1.50 mm strip dimensions are not misused as that tail. The 164.8 mm Phase A dressed budget is reported as a reference only. Physical mating, q/skirt/full-press, crimp inspection and retention testing remain OPEN.

## Remaining blockers and service procedure

Wiring remains a failed candidate wherever the exhaustive audit finds strand crossings or fixed-body contacts. Remove USB, shell screws, central cap and strips; disconnect Main GH/EZmate, remove Main and its own hardware, then translate the connected reserve turns north by 15.10 mm. Wing hardware remains fitted. The continuous audit tests that proposal; its blockers are retained in service.json. No accessible-service certification is granted while fitted collisions remain. A further separated fan/upper-path redesign is required; this run does not prove that redesign impossible.

There is also a direct fixed-input roof conflict: the required low skin and unchanged aluminium overlap in material. An underside pocket cannot preserve 2.00 mm skin there. At 16 mm, the settled central surface footprint has a disconnected south component separated by 0.200 mm; a single solid requires revised ownership/footprint or an authorized connection. These constraints are reported explicitly instead of deleting skin, plate or shell material. The full physical Junana skirt test remains OPEN at both pitches.

## 17 mm current evidence

- **1 Exhaustive fitted collision: FAIL.** 295 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS.
- **2 Finished conductors ≤200 mm: PASS.** Longest finished upper bound 197.822584 mm including 3.90 mm Wing / 3.40 mm Main sourced dress-to-tip bounds and 30.20 mm connected reserve; nominal assembly conditions in tail-source.json.
- **3 Accessible ~30 mm service: FAIL.** Motion blocked; fitted collisions additionally prevent accessible certification.
- **4 Connected Fly 170 / R5 / roof gap: PASS.** 170.000000000 mm, R5; true roof gap 0.300000 mm; 0 fitted contacts.
- **5 USB 30 mm insertion: PASS.** Three continuous 30 mm reservations recomputed.
- **6 Assumed swept caps after allowances: PASS.** Certified trimmed-face minimum after 0.50 mm allowance: 0.500000 mm; physical Junana skirt test OPEN.
- **7 Print envelopes and manufacturing data: PASS.** All nineteen STEP/STL sets independently reloaded with unchanged verifier.
- **8 Fitted preview STEP: PASS.** Preview reloaded 366 / 366 constituents.

| Side | Routed max mm | Finished bound mm | Margin to 200 mm | Finished dressed bound mm | Margin to 164.8 reference mm | Connected reserve mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |
| right | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |

The 164.8 mm value is a reported Phase A reference, not a binding gate. The 3.40 mm internal tails plus the 0.50 mm Wing dress lead are included in finished and dressed bounds. The 30.20 mm reserve is the difference between connected curves, not a detached length allowance. See [length-fly.json](17mm/length-fly.json).

Fitted audit: **366 constituents, 66795 unordered pairs**, 65084 AABB exclusions, 132 explicitly classified own mates, 1579 exact Commons, 0 operation errors. Intersection threshold remains 1e−6 mm³. [tuning-comparison.json](17mm/tuning-comparison.json) lists cleared, remaining and new named pairs against the first candidate. Both pitch geometries and all exact candidates were rerun in this tuning round. After E-boss restoration, results are replayed only when both serialized operand hashes, names and constituent indices are unchanged; every changed-tray pair is recomputed. audit-E-restoration-reuse.json binds this proof to preserved parent evidence; verify_package.py independently checks it. No first-candidate PASS is reused. Full names, Common volumes/bounds and all positive contacts are in [audit.json](17mm/audit.json) and [collision-map.json](17mm/collision-map.json). Inherited Fly source invalidities remain labelled.

- conductors / conductors: 172 contacts.
- aluminium plates / conductors: 28 contacts.
- conductors / shell-central: 28 contacts.
- conductors / trays: 25 contacts.
- conductors / strip-left: 14 contacts.
- conductors / strip-right: 14 contacts.
- E screws / conductors: 6 contacts.
- E screws / shell-central: 2 contacts.
- aluminium plates / shell-central: 2 contacts.
- shell-central / trays: 2 contacts.
- POM-left-H3 / shell-central: 1 contacts.
- POM-right-H1 / shell-central: 1 contacts.

Continuous service-motion results:

- left: 14 contacts, 0 errors; represented release 30.20 mm.
- right: 14 contacts, 0 errors; represented release 30.20 mm.

The swept envelope includes every intermediate translation of each concentric reserve U, plus a 0.020 mm excess. Wing stacks and the other harness remain fitted. Main and its removable hardware, shell caps and own moving harness are excluded as documented in service.json. The fixed legs shorten along their existing loci. A clear reserve-motion result alone cannot certify a harness with fitted fan/upper-route crossings. Individual own-harness motion was not promoted to service certification while those crossings remain. The new route clears every fixed Wing MUX bound (0 MUX contacts), but still has 172 strand/strand fitted contacts plus the fixed-body contacts listed above; it is not a successful separated-harness qualification.

Hardware: all eight **M2×10** E replacements PASS. Under-head Z13.85, tip Z3.85, boss top Z7.35: **3.50 mm nominal engagement**, full thread-bearing annulus verified by exact Common (major radius 1.00 / pilot radius 0.85 over Z3.85…7.35), tip **1.85 mm above floor top**, **≥1.20 mm root material** verified with material probes. Washer and head envelope are retained. Existing pilot depths remain recorded per seat. Replacement procurement must preserve the polymer-compatible thread and Ø3.4 ×1.3 mm head envelope; physical retention remains untested. [hardware-inventory.json](17mm/hardware-inventory.json) lists each seat. New north-head wall relief is below the plateau roof. A stricter engagement check rejected the routing cuts that left only 32.5% of the two north thread-bearing annuli. Exact original source boss material within a named Ø7 region was restored, preserving its pilots and the compressed stack; hardware-inventory.json now requires complete annulus and root material. This adds legitimate wire/boss contacts to the failed routing evidence, rather than weakening the supports. Required-skin contacts are not excused by it.

Certified local distances:

- cover-Main-spacer-2: distance 0.300000 mm; Common 0.000000000 mm³.
- cover-screw-2: distance 0.550000 mm; Common 0.000000000 mm³.
- cover-Main-spacer-3: distance 0.299999 mm; Common 0.000000000 mm³.
- cover-screw-3: distance 0.549999 mm; Common 0.000000000 mm³.
- Main-GH-left-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.
- Main-GH-right-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.

Caps: all 42 assumed 16×16 mm swept envelopes, Z13.95 to provisional Z24.65, checked against every actual central/strip solid. Common is below 1e−6 mm³ for every pair. The minimum exact trimmed-face distance is **1.000000 mm**, leaving **0.500000 mm** after the unchanged 0.50 mm allowance, against a 0.30 mm gate. Face pairs are excluded only by Euclidean AABB lower bounds; finite closest points and their actual face bounds are checked. This bypasses the defective whole-solid inside classifier. [cap-witnesses.json](17mm/cap-witnesses.json) records faces and points. Physical skirt/full-press test remains OPEN.

Required-skin blockers (independent intersection of the unchanged roof rule and fixed bodies):

- POM-left-H3 / required low_south roof: 3.653100 mm³.
- plate-left / required low_south roof: 1158.194242 mm³.
- plate-left / required slope roof: 175.400194 mm³.
- POM-right-H1 / required low_south roof: 3.653100 mm³.
- plate-right / required low_south roof: 1158.183766 mm³.
- plate-right / required slope roof: 175.400197 mm³.
- tray-left protected south palm band / required low_south roof: 89.482726 mm³.
- tray-right protected south palm band / required low_south roof: 84.196891 mm³.

These overlaps cannot be removed by underside relief while preserving a full 2.00 mm skin below the settled exterior at the same footprint. The low roof occupies Z11.55…13.55; the aluminium plate occupies Z12.05…13.55. Clearing it requires changed footprint/material ownership, stack or exterior. None is silently changed. Other remaining tray/hardware/strand contacts are still failed and enumerated, not claimed impossible merely because this candidate fails.

Central shell: **1 solids**. Boundary regularization cancels opposing internal planar sheets; volume preserved within 1e−6 mm³. All detached north tongues are explicitly assigned to an adjoining strip only after a valid volume-preserving single-solid union. Exact component separation and footprint component bounds are in [tuning-blockers.json](17mm/tuning-blockers.json). A disconnected south section is retained in STEP/STL and the print gate fails for it.

| Print | STEP solids | Nonmanifold STL edges | Export verification |
|---|---:|---:|---|
| splice-1 | 1 | 0 | PASS |
| splice-2 | 1 | 0 | PASS |
| post-left-R1 | 1 | 0 | PASS |
| post-left-R2 | 1 | 0 | PASS |
| post-left-R3 | 1 | 0 | PASS |
| post-left-R4 | 1 | 0 | PASS |
| post-left-R5 | 1 | 0 | PASS |
| post-left-R6 | 1 | 0 | PASS |
| tray-left | 1 | 0 | PASS |
| post-right-R1 | 1 | 0 | PASS |
| post-right-R2 | 1 | 0 | PASS |
| post-right-R3 | 1 | 0 | PASS |
| post-right-R4 | 1 | 0 | PASS |
| post-right-R5 | 1 | 0 | PASS |
| post-right-R6 | 1 | 0 | PASS |
| tray-right | 1 | 0 | PASS |
| strip-left | 1 | 0 | PASS |
| strip-right | 1 | 0 | PASS |
| shell-central | 1 | 0 | PASS |

The unchanged export checks include STEP validity, single solid, 220×220 mm XY envelope including 5 mm brim, height ≤250 mm, exact STL edge incidence, no degenerate triangles, volume error <0.001, hashes and preview inventory. No mesh welding or discarded solid is used. [export-verification.json](17mm/export-verification.json), manufacturing STEP/STL/SVG and dimension register correspond to this candidate.

Updated planning cost: 200.2 g nominal PETG; 250.3 g with waste; USD 7.81–15.91 case material/new hardware; 8.2–16.4 print hours. Including machine time and assembly, USD 36.02–52.33. Eight M2×10 replacements are newly included; these are assumptions, not quotes.

## 16 mm current evidence

- **1 Exhaustive fitted collision: FAIL.** 299 unexpected contacts; 0 Boolean errors; exhaustive all-pair audit; full E thread-bearing annuli/root PASS.
- **2 Finished conductors ≤200 mm: PASS.** Longest finished upper bound 197.822584 mm including 3.90 mm Wing / 3.40 mm Main sourced dress-to-tip bounds and 30.20 mm connected reserve; nominal assembly conditions in tail-source.json.
- **3 Accessible ~30 mm service: FAIL.** Motion blocked; fitted collisions additionally prevent accessible certification.
- **4 Connected Fly 170 / R5 / roof gap: PASS.** 170.000000000 mm, R5; true roof gap 0.300000 mm; 0 fitted contacts.
- **5 USB 30 mm insertion: PASS.** Three continuous 30 mm reservations recomputed.
- **6 Assumed swept caps after allowances: PASS.** Certified trimmed-face minimum after 0.50 mm allowance: 0.500000 mm; physical Junana skirt test OPEN.
- **7 Print envelopes and manufacturing data: FAIL.** shell-central: 2 solids, 0 nonmanifold edges
- **8 Fitted preview STEP: PASS.** Preview reloaded 367 / 367 constituents.

| Side | Routed max mm | Finished bound mm | Margin to 200 mm | Finished dressed bound mm | Margin to 164.8 reference mm | Connected reserve mm |
|---|---:|---:|---:|---:|---:|---:|
| left | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |
| right | 190.522584 | 197.822584 | 2.177416 | 167.622584 | -2.822584 | 30.200000 |

The 164.8 mm value is a reported Phase A reference, not a binding gate. The 3.40 mm internal tails plus the 0.50 mm Wing dress lead are included in finished and dressed bounds. The 30.20 mm reserve is the difference between connected curves, not a detached length allowance. See [length-fly.json](16mm/length-fly.json).

Fitted audit: **367 constituents, 67161 unordered pairs**, 65428 AABB exclusions, 133 explicitly classified own mates, 1600 exact Commons, 0 operation errors. Intersection threshold remains 1e−6 mm³. [tuning-comparison.json](16mm/tuning-comparison.json) lists cleared, remaining and new named pairs against the first candidate. Both pitch geometries and all exact candidates were rerun in this tuning round. After E-boss restoration, results are replayed only when both serialized operand hashes, names and constituent indices are unchanged; every changed-tray pair is recomputed. audit-E-restoration-reuse.json binds this proof to preserved parent evidence; verify_package.py independently checks it. No first-candidate PASS is reused. Full names, Common volumes/bounds and all positive contacts are in [audit.json](16mm/audit.json) and [collision-map.json](16mm/collision-map.json). Inherited Fly source invalidities remain labelled.

- conductors / conductors: 172 contacts.
- aluminium plates / conductors: 28 contacts.
- conductors / shell-central: 28 contacts.
- conductors / trays: 25 contacts.
- conductors / strip-left: 14 contacts.
- conductors / strip-right: 14 contacts.
- E screws / conductors: 6 contacts.
- aluminium plates / shell-central: 4 contacts.
- shell-central / trays: 4 contacts.
- E screws / shell-central: 2 contacts.
- POM-left-H3 / shell-central: 1 contacts.
- POM-right-H1 / shell-central: 1 contacts.

Continuous service-motion results:

- left: 14 contacts, 0 errors; represented release 30.20 mm.
- right: 14 contacts, 0 errors; represented release 30.20 mm.

The swept envelope includes every intermediate translation of each concentric reserve U, plus a 0.020 mm excess. Wing stacks and the other harness remain fitted. Main and its removable hardware, shell caps and own moving harness are excluded as documented in service.json. The fixed legs shorten along their existing loci. A clear reserve-motion result alone cannot certify a harness with fitted fan/upper-route crossings. Individual own-harness motion was not promoted to service certification while those crossings remain. The new route clears every fixed Wing MUX bound (0 MUX contacts), but still has 172 strand/strand fitted contacts plus the fixed-body contacts listed above; it is not a successful separated-harness qualification.

Hardware: all eight **M2×10** E replacements PASS. Under-head Z13.85, tip Z3.85, boss top Z7.35: **3.50 mm nominal engagement**, full thread-bearing annulus verified by exact Common (major radius 1.00 / pilot radius 0.85 over Z3.85…7.35), tip **1.85 mm above floor top**, **≥1.20 mm root material** verified with material probes. Washer and head envelope are retained. Existing pilot depths remain recorded per seat. Replacement procurement must preserve the polymer-compatible thread and Ø3.4 ×1.3 mm head envelope; physical retention remains untested. [hardware-inventory.json](16mm/hardware-inventory.json) lists each seat. New north-head wall relief is below the plateau roof. A stricter engagement check rejected the routing cuts that left only 32.5% of the two north thread-bearing annuli. Exact original source boss material within a named Ø7 region was restored, preserving its pilots and the compressed stack; hardware-inventory.json now requires complete annulus and root material. This adds legitimate wire/boss contacts to the failed routing evidence, rather than weakening the supports. Required-skin contacts are not excused by it.

Certified local distances:

- cover-Main-spacer-2: distance 0.300000 mm; Common 0.000000000 mm³.
- cover-screw-2: distance 0.550000 mm; Common 0.000000000 mm³.
- cover-Main-spacer-3: distance 0.299999 mm; Common 0.000000000 mm³.
- cover-screw-3: distance 0.549999 mm; Common 0.000000000 mm³.
- Main-GH-left-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.
- Main-GH-right-DRAWING-BOUND: distance 0.300000 mm; Common 0.000000000 mm³.

Caps: all 42 assumed 16×16 mm swept envelopes, Z13.95 to provisional Z24.65, checked against every actual central/strip solid. Common is below 1e−6 mm³ for every pair. The minimum exact trimmed-face distance is **1.000000 mm**, leaving **0.500000 mm** after the unchanged 0.50 mm allowance, against a 0.30 mm gate. Face pairs are excluded only by Euclidean AABB lower bounds; finite closest points and their actual face bounds are checked. This bypasses the defective whole-solid inside classifier. [cap-witnesses.json](16mm/cap-witnesses.json) records faces and points. Physical skirt/full-press test remains OPEN.

Required-skin blockers (independent intersection of the unchanged roof rule and fixed bodies):

- POM-left-H3 / required low_south roof: 3.672595 mm³.
- plate-left / required low_south roof: 915.143479 mm³.
- plate-left / required slope roof: 160.260272 mm³.
- POM-right-H1 / required low_south roof: 3.672595 mm³.
- plate-right / required low_south roof: 915.139204 mm³.
- plate-right / required slope roof: 160.260276 mm³.
- tray-left protected south palm band / required low_south roof: 75.033093 mm³.
- tray-right protected south palm band / required low_south roof: 69.742299 mm³.

These overlaps cannot be removed by underside relief while preserving a full 2.00 mm skin below the settled exterior at the same footprint. The low roof occupies Z11.55…13.55; the aluminium plate occupies Z12.05…13.55. Clearing it requires changed footprint/material ownership, stack or exterior. None is silently changed. Other remaining tray/hardware/strand contacts are still failed and enumerated, not claimed impossible merely because this candidate fails.

Central shell: **2 solids**. Disconnected south surface footprint at 16 mm: a bridge would add exterior footprint or cross an excluded well. No bridge/deletion used. Exact component separation and footprint component bounds are in [tuning-blockers.json](16mm/tuning-blockers.json). A disconnected south section is retained in STEP/STL and the print gate fails for it.

| Print | STEP solids | Nonmanifold STL edges | Export verification |
|---|---:|---:|---|
| splice-1 | 1 | 0 | PASS |
| splice-2 | 1 | 0 | PASS |
| post-left-R1 | 1 | 0 | PASS |
| post-left-R2 | 1 | 0 | PASS |
| post-left-R3 | 1 | 0 | PASS |
| post-left-R4 | 1 | 0 | PASS |
| post-left-R5 | 1 | 0 | PASS |
| post-left-R6 | 1 | 0 | PASS |
| tray-left | 1 | 0 | PASS |
| post-right-R1 | 1 | 0 | PASS |
| post-right-R2 | 1 | 0 | PASS |
| post-right-R3 | 1 | 0 | PASS |
| post-right-R4 | 1 | 0 | PASS |
| post-right-R5 | 1 | 0 | PASS |
| post-right-R6 | 1 | 0 | PASS |
| tray-right | 1 | 0 | PASS |
| strip-left | 1 | 0 | PASS |
| strip-right | 1 | 0 | PASS |
| shell-central | 2 | 0 | FAIL |

The unchanged export checks include STEP validity, single solid, 220×220 mm XY envelope including 5 mm brim, height ≤250 mm, exact STL edge incidence, no degenerate triangles, volume error <0.001, hashes and preview inventory. No mesh welding or discarded solid is used. [export-verification.json](16mm/export-verification.json), manufacturing STEP/STL/SVG and dimension register correspond to this candidate.

Updated planning cost: 186.1 g nominal PETG; 232.6 g with waste; USD 7.45–15.38 case material/new hardware; 7.6–15.3 print hours. Including machine time and assembly, USD 35.08–50.64. Eight M2×10 replacements are newly included; these are assumptions, not quotes.

## Reproduction and integrity

Run `bash hardware/case/issue-248-phaseb/reproduce.sh 17 16` from this worktree with the retained CAD Python environment. Each stage is separate; all scratch and audit checkpoints are under .issue248-runtime. Exact audit reuse is permitted only for the identical geometry index hash. This continuation rebuilds both pitches and reruns all eight gates, independent exports, witnesses and package checks. All 44 preserved first-candidate files are independently checked against the frozen 47f7dd5 hashes in first-candidate-sha256.json; new outputs describe the tuning candidate. Run `python3 hardware/case/issue-248-phaseb/verify_package.py` after report generation for input/artifact hashes and independent all-pair coverage. The package remains provisional and unreleased, with the explicitly failed gates above.
