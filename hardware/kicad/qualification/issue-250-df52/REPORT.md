# Issue #250 — DF52 Main / Wing successor qualification

Study candidate, 2026-11-14, branch `issue-250-df52`. **Do not adopt or release these boards.** Main fails routing and loop-resistance gates; 17R fails the all-pairs via-pad floor and power-width gates. The other three Wings pass the copper-routing gates, but native Wing ERC is unavailable. The exact current manufacturer no-pattern coverage and an in-stock housing procurement path are unresolved. No pass condition has been relaxed. `docs/decisions.md` is unchanged.

## Interrupted-run inventory and continuation

The first inventory found this entire qualification directory untracked, with no Issue #250 commit. The private Git HEAD was `0e5f1703`; `.issue250-runtime/git` already existed on the requested branch. The runtime contained KiCad launchers, tool caches, initial/routed/repaired boards, route/extraction/verification logs, drawing renders, the saved #248 discussion and draft stock responses. None was a release package. [Initial inventory](continuation-inventory.json) binds the then-existing deliverables by SHA-256 and preserves the original qualification summary and **draft** stock conclusions. [Five compressed starting boards](continuation-start/) preserve the precise interrupted copper state.

| Work item | State at interruption | Continuation disposition |
|---|---|---|
| Symbol / footprint | 14 cavities + MP; catalogue-sized lands/nails; conservative body keepout; 1.2 mm process notes | Reused; recovered and inspected an older Hirose individual drawing; current exact no-pattern review still blocked |
| Main | Native DRC 1, open 1, independent open 1; ERC 0; native parity 202; common loop 109.516 mΩ | Frozen copper retained after rejected restoration trial; schematic naming/mechanical documentation repaired; final parity 29 disclosed below |
| 16L | DRC/open 0/0; three 0.10 mm GND stubs; minimum via-pad 0.105390 mm | Removed only redundant stubs; fresh native/physical and resistance checks; finer via relocation search unsuccessful |
| 16R | DRC/open 0/0, copper gates pass; no native ERC | Reused unchanged PCB and hash-bound extraction; reran native/physical checks |
| 17L | DRC/open 0/0; two 0.10 mm GND stubs | Removed only redundant stubs; fresh native/physical and resistance checks |
| 17R | DRC/open 0/0 but three same-net via-in-pad overlaps, minimum −0.300 mm; four undersized GND tracks | Rejected deletion trial created four ground components; original board retained and failure reported |
| Harness | Length/dress specification, six endpoint STEP reservations and transforms existed | Reused; checked length arithmetic, transforms/hashes and supplied B3 datum screen |
| Stock | Direct LCSC/JLC responses plus browser draft claiming housing failure; conflicting older supplier counts noted | Re-requested all 12 product URLs; newly retrieved DigiKey pages; Mouser numeric stock not recoverable; draft not promoted to final evidence |
| Report / handoff | REPORT.md, final evidence audit and commit missing | Supplied here with reproduction/replay entry points and evidence audit |

The interrupted stock draft reported LCSC housing 0, JLC overseas 4, DigiKey 0 / 100 incoming 23-Dec, and Mouser 0 / 1000 incoming 17-Dec. These were **in-progress findings, not a final procurement verdict**. The old browser record is retained only as [interrupted draft](connector/interrupted-draft-browser-observations.json); final observations below have their own retrieval dates and limitations.

## Library, numbering and invariant scope

[DF52.kicad_sym](DF52.kicad_sym) and [footprint](DF52.pretty/DF52-14S-0.8H_14.kicad_mod) implement Hirose DF52-14S-0.8H(21), with fourteen 0.50×1.00 mm rectangular lands at 0.80 mm pitch, X −5.2…+5.2 / Y −1.11; two unnetted 0.90×1.60 mm MP lands at X ±6.45 / Y +0.81. MP is mechanical, never cavity 15 or a harness conductor. Land span in Y is 3.22 mm.

Hirose EDC3-356517-01 revision 3, page 1, corroborates these dimensions and pin-1 orientation; page 2 supplies a reference reflow profile. The archived drawing is older, not a substitute for review of the current drawing. [Provenance](connector/PROVENANCE.md), [drawing review](connector/drawing-review.json), the manufacturer PDFs and the exact library files accompany this study. The surface keepout X ±5.95 / Y −0.55…+1.61 prohibits tracks, vias and pours on the mounting copper layer. It is a conservative body reservation, **not a verified transcription of a current manufacturer no-pattern polygon**. Opposite/internal layers remain available. Current exact no-pattern coverage is **BLOCKED**; do not remove the reservation to close Main's route.

Board thickness stays **1.2 mm**. This SMT connector has no thickness-dependent through-board retention feature. The documented process uses a 0.10 mm stencil with 100% land openings, catalogue reference lead-free profile and ≤2 reflows. Warpage, paste/profile and nail wetting on the actual 1.2 mm assembly require assembler acceptance. This is not a manufacturing package.

| Cavity | Electrical contract |
|---|---|
| 1 | HALL_5V |
| 2 / 4 / 8 / 10 / 12 / 14 | Six separate GND returns |
| 3 / 5 / 6 | MUX_A0 / MUX_A1 / MUX_A2 |
| 7 | WING_EN; Main J3 preserves its inherited sheet-local `MUX_EN1` name |
| 9 / 11 / 13 | MUX_OUT_A / MUX_OUT_B / MUX_OUT_C |

The independent native comparison finds **zero invariant or cavity-contract errors on every board**: outlines, mounting holes, stack/thickness, all other footprint poses/pads/nets, other connectors and power-circuit topology are unchanged. All Wing purchased components and electrical test pads remain B.Cu. Replacing a header is not represented as a pin-compatible copper swap.

**Pose adjustments: none.** Main retains J2 native `(82.897854,112.075001)`, −120°, and J3 `(117.102146,112.075001)`, +120°, F.Cu. All four Wings retain their source origins/angles and B.Cu side; [construction.json](construction.json) lists every pose and cavity net. The source 16L hash is the closed round-3 board in REPORT3.md, not its failed round-2 predecessor.

Copper changes exceed the initial connector windows on **all five** candidates. [Scope summary](scope-summary.json) discloses the changed nets, copper-area deltas, object counts and native bounds. Main spans about **45.90×41.20 mm**, including VBUS/V5V2 copper changes. This is a locality failure/exception for review, not a change to electrical topology or an assertion that a local solution is impossible. Power-circuit parts and placements remain fixed; power copper geometry does not.

## Per-board gates against GH baselines

Sources are [Main Rev.7](../issue-240-main-rev7/REPORT.md) and [Wing Rev.4 round 2](../issue-235-wing-round2/REPORT.md) plus [16L round 3](../issue-235-wing-round2/REPORT3.md). Baseline zero ERC for Main is real; Wing baselines explicitly lacked a native schematic, so a logical contract cannot be relabelled as ERC. This issue's explicit Wing ERC-zero requirement is therefore **unverified on every variant**.

| Gate | GH Main Rev.7 | DF52 Main | Verdict |
|---|---:|---:|---|
| Native DRC / unrouted | 0 / 0 | **1 / 1** | FAIL |
| Native ERC | 0 | **0** | PASS |
| Native schematic parity | Saved baseline 0¹ | **29**¹ | Not zero; disclosed |
| Independent opens / wrong-net contacts | 0 / 0 | **1 / 0**, 40 nets | FAIL |
| Outline / holes / other parts / pin contract | Unchanged | 0 invariant errors | PASS |
| Via-pad minimum / binding floor | 0.145 / 0.100 mm | **0.145 / 0.100 mm**, 30,315 pairs | PASS; ≥0.125 target |
| Power/track widths below applicable floors | 0 | 0² | PASS under Main yardstick |
| Input loop at inherited corner | 49.086 mΩ | **28.632 mΩ** | PASS ≤50 mΩ |
| Common loop | 49.491 mΩ | **109.516 mΩ** | FAIL ≤50 mΩ target |
| J2 / J3 branch loops | 20.961 / 43.051 mΩ | **97.536 / 5.454 mΩ** | J2 misses 50 mΩ model target |
| Rev.7-yardstick worst Vfar | 4.792958 V | **4.770792 V** | Numerical PASS ≥4.60 V |
| Local-only routing | Named baseline exception | Outside connector windows | FAIL / disclosed exception |
| Full requested qualification | Adopted GH baseline | **FAIL** | No adoption |

¹ The baseline native report did not place its schematic beside the PCB and did not establish strict native schematic parity. The interrupted continuation did colocate it and produced 199 root-local/generated-net conflicts plus three missing mechanical symbols. The continuation globalizes root labels without changing connected-pin membership and documents the existing H1/H2/H3 holes without modifying their PCB objects. Native parity now has 29 entries, all generated names for intentionally unconnected pins versus empty PCB net assignments, including MP. The exported connected-pin netlists compare equal after the original root-prefix normalization ([audit](evidence-audit.json)); these expected NC-name diagnostics are not claimed as native parity zero. ERC remains 0.

² Main retains the source yardstick's 0.10 mm GND segments (43 below 0.30 mm); its HALL_5V floor stays 0.30 mm. Wing power **and GND** floors are 0.30 mm. No Wing neck-down exception is accepted.

| Gate | 16L | 16R | 17L | 17R |
|---|---:|---:|---:|---:|
| GH native DRC / unrouted | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| DF52 native DRC / unrouted | **0 / 0** | **0 / 0** | **0 / 0** | **0 / 0** |
| Independent opens / wrong contacts (30 nets each) | **0 / 0** | **0 / 0** | **0 / 0** | **0 / 0** |
| Native ERC, explicit requirement | **Unavailable** | **Unavailable** | **Unavailable** | **Unavailable** |
| Invariant / pin-contract errors | 0 / 0 | 0 / 0 | 0 / 0 | 0 / 0 |
| All purchased components B.Cu | PASS | PASS | PASS | PASS |
| GH via-pad minimum, mm | 0.129641 | 0.133180 | 0.125198 | 0.116836 |
| DF52 via-pad minimum, mm | **0.105390** | **0.133180** | **0.125198** | **−0.300000** |
| Pairs audited | 41,300 | 35,636 | 34,692 | 37,052 |
| Binding 0.100 mm floor | PASS | PASS | PASS | **FAIL, 3 overlaps** |
| 0.125 mm improvement target | Miss | PASS | PASS | Miss |
| Widths below 0.30 mm power/GND floor | **0** | **0** | **0** | **4 — FAIL** |
| GH worst 200 mm Vfar, V | 4.921088 | 4.943619 | 4.926366 | 4.933577 |
| DF52 same-family-yardstick Vfar, V | **4.939023** | **4.943659** | **4.938266** | **4.942842** |
| ≥4.60 V numerical gate | PASS | PASS | PASS | PASS, diagnostic only |
| Copper-routing bundle | **PASS** | **PASS** | **PASS** | **FAIL** |
| Full requested qualification | **BLOCKED** | **BLOCKED** | **BLOCKED** | **FAIL** |

Native DRC does not enforce this project's same-net via-pad distance rule. That is why 17R's DRC zero coexists with a genuine all-pairs floor failure. Exhaustive per-board `.csv.gz` audits include same-net pads, electrical test pads and NPTH shapes, with actual via diameters and copper layers; no pad category is dropped.

## Failed gates and blocker analysis

- **Main routing:** J2.11 MUX_OUT_B is isolated from the J3.11/R12.1 copper component. A J3 MUX_OUT_B F.Cu track (`0fea47da-1bbd-4362-8943-ec4f59408ef0`) crosses the connector reservation. The interrupted run already attempted keepout-aware rerouting and straight solder-tail fanout searches without closure. Neither a through-body route nor lowering a keepout/clearance is accepted. Closing this needs a new local multilayer fanout/routing search, potentially displacing neighboring signal copper; this study does not prove impossibility.
- **Main resistance:** the extracted common loop is 59.516 mΩ above the 50 mΩ target, and J2's branch also exceeds 50 mΩ. Restoring original Rev.7 VBUS/V5V2 copper was tested in scratch; it created **89 native violations** including shorts to newly routed signals/ground. That trial was rejected. A joint power/signal reroute preserving the wider low-resistance corridor is needed. A passing voltage calculation does not waive either failed resistance target.
- **17R fabrication:** three GND vias overlap J_WING pads 8/10/12; four ground tracks are 0.10 or 0.20 mm instead of 0.30 mm. The saved bounded relocation/widening searches failed. Removing those vias and subfloor tracks produced **four ground components**; rejected, not adopted. This requires new 0.30 mm ground solder-tail escapes, legal off-pad vias and signal displacement as needed. The remaining signal via target misses are also disclosed.
- **16L improvement target:** 0.105390 mm clears the binding 0.10 mm floor but degrades the 0.129641 mm GH result and misses 0.125 mm. A new 0.025–2.0 mm bounded relocation search found no legal move with neighboring copper fixed. This is an explicit target miss, not a hidden pass at 0.125 mm.
- **Wing ERC:** no inherited native schematic exists. Native ERC-zero cannot be certified by extracting a passive schematic from the routed PCB; doing that would merely encode the implementation. A reviewed functional Wing schematic with real pin electrical types and native ERC is required.
- **Library/procurement:** current exact no-pattern coverage and housing supply remain blocked as described here. Assembler process acceptance, physical crimp/housing/dress qualification and case Phase B acceptance are outstanding assembly gates.

[Continuation repairs](continuation-repairs.json) record adopted/rejected trials. Only five redundant GND stubs were removed from the two left Wing boards. The full actual-copper graph after refill still has one ground component and zero required opens on each; native DRC stays zero. Placement, pads, rules and net assignments were not altered. The three other PCB files are byte-identical to the interrupted inventory.

## Resistance and voltage evidence

Main's frozen-board extraction and both right-Wing extractions were reused only after matching their SHA-256 bindings. Both changed left boards were re-extracted on saved copper. Wing solves use 35 µm sheet / 20 µm barrel assumptions, distributed **127 mA**, 0.06/0.015 mm² meshes and nominal/80% track widths. All eight cases per board complete; mesh disagreements are below the inherited 3% limit and KCL residuals below 1 µA. Main analytic rectangle, reciprocity and superposition checks pass. [Power budget](power-budget.json), [sensitivity CSV](power-sensitivity.csv), [Main resistance summary](resistance-summary.json) and individual Wing extraction files contain the detailed results.

| Voltage family | Worst Vfar | Interpretation |
|---|---:|---|
| Main Rev.7 yardstick, historical Wing copper | **4.770792 V** | Main candidate evaluated with the inherited Wing comparison model |
| Wing Rev.4 yardstick, historical Main #196 | **4.938266 V** | Fresh DF52 Wing copper evaluated with unchanged Rev.4 comparison Main |
| Coupled new Main + new Wings | **4.911074 V** | Diagnostic combined model; failed board gates still apply |

All worst cases use two simultaneously loaded Wings, 5.2 V −2%, 50 mV dynamic budget, U5 0.25 Ω, AWG28 minimum area 0.0804 mm², **200 mm finished conductors**, six equal independent returns, **10 mΩ DF52 contact per end plus 40 mΩ per crimp termination**, and the inherited 125°C / −20% width numerical corner. The 40 mΩ crimp allowance is an explicit conservative assumption, not a recovered B3 specification; 0/10/20/40 mΩ sensitivity is included. The allowance must be checked against the actual qualified crimp process. 125°C is a copper-model extrapolation; DF52's operating rating ends at +85°C. These models are not measured fabrication/assembly guarantees.

## Harness and #248 case handoff

[Harness specification](harness/SPEC.md) defines two fourteen-conductor links per keyboard, DF52-14P-0.8C housings and DF52-2832PCF terminals at both ends, cavity n-to-n. Use AWG28 thin-wall insulation OD0.50–0.60 mm and six separate full-length returns.

Every conductor is finished **195±5 mm, absolute maximum 200 mm**, measured along its contact-to-contact electrical path, **including 30.2 mm service reserve**. Thus the non-reserve path is 164.8 mm nominal / 169.8 mm maximum. This is not 200 mm cut wire plus terminals or reserve. Case Phase B must verify actual outermost conductor lengths and reserve storage.

The local mated reservation is **13.40×4.10×1.75 mm**; fourteen 0.60 mm OD cylinders model the first **10 mm of straight, flat, 0.8 mm-pitch dress** before the independent restraint. No gathered bundle or tie is placed at the housing root. [Geometry and transforms](harness/geometry.json), [local STEP](harness/mated-and-first-dress-local.step), and six named endpoint STEPs provide mm units, outward vectors, native-frame bounds and SHA-256. These are conservative reservation solids, not detailed supplier models. Native board top is Z0; Wing B.Cu mounting face is Z−1.2; assembly mounting transforms/Z datums are explicitly documented.

At the supplied unchanged B3 datum poses, the Wing underside reservation remains **B=6.70 mm** and plate-top datum **Z12.90**. Main retains **+1.90 mm nominal roof clearance**, minus **0.50 mm allowance = +1.40 mm**, exceeding **+0.30 mm** by **1.10 mm**. First dress stays below the mated-body height. This is a **PASS of the supplied B3 datum screen**, not a fresh collision calculation against an absent Phase B roof solid. Whole-case route storage, post/tie interfaces, connector access and the actual flexible assembly remain Phase B gates; no case production geometry is modified.

## Stock recheck and housing procurement path

**Stock verdict: FAIL — no confirmed in-stock housing path at the required batch basis.** The continuation freshly requested the product pages on **2026-11-14 UTC**; exact timestamps, response hashes, identity extraction and archived responses are in [stock.json](connector/stock.json). [New primary-page observations](connector/primary-page-recheck.json) are separate from the interrupted draft.

Fifteen keyboards install **60 headers, 60 housings and 840 terminals** (two links, two ends/link). The installed 10× targets are **600 / 600 / 8,400**. The study also discloses a conservative 20% spare allowance: 72 / 72 / 1,008 to buy, preferred 10× visibility **720 / 720 / 10,080**. That extra allowance is not misrepresented as a recovered project mandate; it does not change the stock verdict.

| Part | LCSC exact-product primary quantity | JLC overseas / presale listing³ | DigiKey newly retrieved exact product | Mouser recheck | Result |
|---|---:|---:|---|---|---|
| Header DF52-14S-0.8H(21), C5343398 | **5,079** | 5,084 / 5,082 | **53**, H125104CT-ND | Access-denied shell; numeric count unverified | PASS via LCSC |
| Housing DF52-14P-0.8C, C2904692 | **0** | **4 / 4**, presale minimum 35 | **0**, H125091-ND; 100 estimated 2026-12-23 | Product open unavailable; no final numeric count accepted | **FAIL** |
| Terminal DF52-2832PCF, C506724 | **129,400** | 129,490 / 129,490 | **266,723**, H125109CT-ND; 80,000 purchase limit | Access-denied shell; numeric count unverified | PASS via LCSC / DigiKey |

³ JLC overseas/presale fields are not local PCBA-ready warehouse stock and are not added to LCSC inventory; they may share the same upstream supply. The LCSC extractor uses the page's selected `webData` product, excluding alternate-product stock. Header and terminal pass from LCSC alone. Housing cannot cover even the installed batch from the verified immediate quantities.

The explicit housing procurement path is **DigiKey H125091-ND, manufacturer DF52-14P-0.8C**, via a backorder or supplier quote for the required batch/spares and a confirmed delivery allocation. The [DigiKey housing product page](https://www.digikey.com/en/products/detail/hirose-electric-co-ltd/DF52-14P-0-8C/5721346), retrieved again on 2026-11-14, reports zero with a future 100-piece receipt; that is not current stock. The web service identified this as a three-day-old primary-page crawl, while direct HTTP returned 403, so this evidence is not claimed as an authenticated live inventory API. The four-week search cache reporting 840 was rejected as older and conflicting.

Mouser **798-DF52-14P-0.8C** is a second quote/backorder route, but direct HTML was an access-denied shell and repeated product opens failed. A newly surfaced five-day product search had notification text, not dependable numeric availability. The interrupted zero / 1000 incoming date and old conflicting 3351/3361 counts were **not carried forward**. No order, supplier reservation or confirmed delivery has been made. Procurement must obtain a fresh primary allocation covering the batch and recheck the approximate 10× stock criterion before adoption.

## Proposed decision-record changes — not applied

1. **D-024 physical layer:** retain every logical cavity number/net, six returns and the n-to-n harness. Propose DF52-14S-0.8H(21) + DF52-14P-0.8C + DF52-2832PCF for these successors, with 0.8 mm interface, AWG28 OD0.50–0.60, 10 mΩ initial-contact model, qualified crimp allowance, friction retention and 20 mating cycles. State that MP is not a fifteenth cavity and JST/DF52 cables are physically incompatible.
2. **D-040 Main successor:** name the eventual accepted DF52 board/version and fixed poses; preserve stack/outline/holes/parts/power topology. Require rerouting closure, loop targets and all native/independent gates; disclose actual copper scope and new voltage evidence. Do not supersede adopted Rev.7 with this failed candidate.
3. **D-039 Wing successor:** preserve all-B.Cu single-sided assembly and D-021, name all four accepted hashes, native ERC evidence, complete via-pad/width/voltage results, any explicit 0.125 mm target misses, and case body/strain-restraint acceptance. All four must qualify together; the present 17R fails.
4. **Harness/case interface:** replace GH-specific envelope/retention assumptions with the qualified DF52 mated/dress envelope; record finished ≤200 mm inclusive of reserve, B=6.70, supplied roof margin after allowance, and verified storage/mating/strain restraint. Carry this into #248 Phase B without silently changing existing D-041 production-case decisions.
5. **Procurement/process evidence:** record dated housing allocation and stock basis, approved crimp/tooling and resistance allowance, exact current drawing/no-pattern review and assembler acceptance of the 1.2 mm process. Adoption remains a PO decision after blocker closure.

## Reproduction and evidence boundary

Run from the repository root:

```bash
bash hardware/kicad/qualification/issue-250-df52/reproduce.sh
# Optional complete numerical extraction, slower:
bash hardware/kicad/qualification/issue-250-df52/reproduce.sh --extract
```

The first command reruns native DRC on five boards, explicit Main parity/ERC, connected-pin netlist export, independent actual-copper connectivity/invariants/all-pairs via-pad audit, solver selfchecks, voltage budget and copper scope. Its final [evidence audit](evidence-audit.json) tests hash consistency and truthful failure states; **evidence consistency is not design qualification**. The second also reruns Main and every Wing extraction. Do not interpret subprocess success without reading the gate JSON: DRC tools are deliberately allowed to write failing reports.

`replay-continuation.py` reproduces the five accepted stub removals from compressed starting boards; `repair-main-schematic.py` replays schematic presentation/documentation repair from its archived source. `build.py`, routing/cleanup/repair/extraction scripts and recorded construction/route metadata explain the preceding interrupted study. They are not a guarantee that rerunning a heuristic router reproduces a frozen failing board byte-for-byte. Replaying copper or rebuilding requires subsequent extraction and qualification.

All scratch, router outputs, logs, caches and Git state reside in **`.issue250-runtime/`**; no task scratch is placed in `/tmp`. Installed KiCad 9.0.9, geometry and router environments in the adjacent original checkout are read-only dependencies listed in `toolchain.json`. The qualified-tree files are review artifacts, not Gerbers, fabrication ZIPs or an order. The final work is committed using `GIT_DIR=.issue250-runtime/git` with this worktree; no push, PR, production baseline or decision edit is performed.
