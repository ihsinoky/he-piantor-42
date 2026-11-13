# Issue #235 round 3 — 16mm-left routing closure

Study only · 2026-11-13 · `issue-235-16l-closure` · round-2 base `24a81280fb9f7b4730fb4395bc0ef930b0a81f27`.

**16L passes the unchanged routing, electrical-contract and voltage gates.** The other three variant directories remain byte-identical. This closes the outstanding routing failure for the four-variant study; Rev.4 adoption remains a PO gate. No production, decision, baseline, manufacturing package, push or PR is changed or issued.

The [saved issue and latest PO comment](wing-rev4-16mm-left/round3/issue235.json) direct closing 16L before adoption. [REPORT.md](REPORT.md) remains the historical round-2 result. Its shared evidence manifests and verification output describe round 2; use the round-3 entry point below to verify this updated 16L candidate. The original failed board is preserved as [round2-main.kicad_pcb](wing-rev4-16mm-left/round3/round2-main.kicad_pcb), SHA-256 `0a351011bb244564268a0086f97e9bf99da63b8c92ce3192739cd2e7a3358f44`. Original radial-search evidence, initial diagnostics and round-2 repair history remain intact.

## Local repair, with placement fixed

Round 2 left U_MUX_C.13 isolated on HALL_5V after 2,553 unsuccessful radial bottom-side escapes. A round-3 0.025 mm two-layer search over native `(120,28)–(145,53)` mm also failed with fixed copper, including the search allowing displacement of track interiors while preserving pads, vias and pad fanouts. The via fence required changing a signal escape. [Search log](wing-rev4-16mm-left/round3/search.log), [exact native copper delta and discovered path](wing-rev4-16mm-left/round3/repair.json), and [local two-layer view](wing-rev4-16mm-left/round3/local-closure.svg) retain the evidence.

The selected lever is targeted multi-layer repair. No MUX, decoupler or other footprint moves, and KRT is not rerun:

- Move the MUX_A1 routing via from `(129.5,40.8)` to `(129.4,41.2)` mm, a 0.412311 mm displacement. Adjust its F.Cu segment and replace its B.Cu fanout segment with a three-segment 0.10 mm dogleg. Every signal remains connected.
- Add a 0.30 mm HALL_5V path from the major F.Cu plane at `(132.575,39.725)`, through B.Cu to `(132.575,40.675)`, across F.Cu to `(129.9,40.675)`, then through B.Cu to U_MUX_C.13. It adds three standard 0.60/0.30 mm through vias and six 0.30 mm track segments. The 2.675 mm F.Cu bridge crosses the service routing on the opposite layer. Actual refilled copper, not net names, establishes the plane connection.
- Improve the inherited via-pad minimum by moving the H_C6_RAW via from `(131,42.5)` to `(130.95,42.47)` mm, 0.058310 mm, adjusting its two adjoining signal tracks. The former limiting pad is U_MUX_C.9. An initial downward-only adjustment violated an adjacent via clearance and was rejected; the final diagonal displacement passes every gate.

All coordinates above are native KiCad mm, X right/Y down. Only one signal track is replaced; five existing copper objects are adjusted and twelve added. No net, required pad, foreign signal connection, width floor, clearance, zone outline, keepout or mechanical reservation is removed. The final [candidate PCB](wing-rev4-16mm-left/main.kicad_pcb) SHA-256 is `6812a98ac887d29b289de231ee4b6cd325799e23f6a9780bc4f823ff069ccf11`.

## Unchanged gates

| Gate | Final 16L result |
|---|---:|
| Native DRC violations / unconnected | **0 / 0** |
| Independent required unconnected / wrong-net contact / material violation / unexplained transfer | **0 / 0 / 0 / 0** |
| Required HALL_5V pad components | **1**, formerly 2 |
| Minimum via-to-pad gap, every pad including same-net and NPTH | **0.129641 mm** |
| Via-pad pairs audited | **36,816**, 156 vias × 236 pads |
| Gaps below 0.10 mm / power widths below 0.30 mm | **0 / 0** |
| Logical electrical-contract errors | **0** |

The minimum improves from 0.101340 mm by **0.028301 mm** and exceeds the **0.125 mm target** by 0.004641 mm. No 16L target miss remains. The other three boards retain their round-2 results, including the disclosed 17R target miss; they are not reworked here.

[Native DRC](wing-rev4-16mm-left/drc.json), [independent qualification](wing-rev4-16mm-left/qualification.json), [all-pairs audit](wing-rev4-16mm-left/via-pad-all-pairs.csv.gz), [final blocking summary](wing-rev4-16mm-left/blocking-regions.json) and [logical contract](wing-rev4-16mm-left/round3/electrical-contract.json) bind the result. The original verifier runs unchanged. D-021 remains two layers, 1.2 mm board, 0.10 mm signals/clearance, 0.30 mm power/GND, 0.60/0.30 mm vias, no escalation. The contract repeats D-024 pin order, six separate returns, three seven-channel MUX banks, unused NC/S8, and local decoupling. Native schematic ERC remains unavailable because the inherited package has no native Wing schematic; the logical check is not presented as ERC.

## Placement, body and post deltas

Native comparisons assert identical footprint and pad positions, poses, nets, sizes, drills and sides against the failed round-2 board. Key/sensor/Hall-cap geometry, mounting holes, outline, all-B.Cu placement, SM14B-GHS-TB selection/anchor/orientation, pour outlines and reservations remain invariant. The projects/rules remain byte-identical.

The original body-screen implementation is rerun for 16L alone: **zero service-body overlaps**. [Six-post rescreen](wing-rev4-16mm-left/round3/post-rescreen.json) recomputes actual native pad/NPTH shapes and conservatively screens full via copper diameters, covering both moved drills and all three added vias. Minimum shaft-to-pad/drill gap remains **0.460311 mm**; minimum shaft-to-via edge is **1.201668 mm**. Every post's nearest pad/via gap delta is zero. Component body and channel envelopes are identical, so their gap deltas are zero and no post moves are required. [Body results](wing-rev4-16mm-left/round3/body-clearance.json) and [scope verification](wing-rev4-16mm-left/round3/verification.json) are separate from the inherited case STEP evidence. No case proposal or production case changes.

## Fresh electrical requalification

[Resistance extraction](wing-rev4-16mm-left/resistance-extraction.json) uses the final saved board: 35 µm copper, 20 µm barrels, distributed **127 mA**, original normalized load proportions, nominal/80% track widths and 0.06/0.015 mm² meshes. All eight rail/mesh/width cases complete. Maximum terminal mesh disagreement is **0.682558%**, below the unchanged 3% limit; maximum KCL residual is **5.639×10⁻¹⁰ A**, below 1 µA. The [rerun analytic FEM checks](wing-rev4-16mm-left/round3/fem-selfcheck.json) pass, with maximum relative error 5.56×10⁻¹⁵.

| Width case | Far terminal | 20°C loop drop | Effective loop resistance |
|---|---|---:|---:|
| Nominal | U_HA4 | 14.458949 mV | 113.849989 mΩ |
| 80% tracks | U_HA4 | 17.418941 mV | 137.157012 mΩ |

The [power summary](wing-rev4-16mm-left/round3/power-summary.json) and [sensitivity CSV](wing-rev4-16mm-left/round3/power-sensitivity.csv) use exactly the round-2/Rev.3 comparison yardstick: historical Main #196 common/branch resistance, two simultaneous Wings, 5.2 V ±2%, 50 mV budget, U5 0.25 Ω, AWG28 and six returns, 50 mΩ/contact ×2, both Main branches, 20/125°C, both widths, 124.097 mm reference, actual modeled conductor path, and 200 mm specification.

Worst **200 mm Vfar = 4.921088 V**, at the 125°C/80% sensitivity corner and historical J3 comparison branch. This is **21.815 mV below** the Rev.3 4.942903 V reference, while retaining **321.088 mV above 4.60 V**. The actual left J2 branch gives **4.924232 V** at that corner. At the 124.097 mm reference length, worst Vfar is **4.924495 V**. This is fresh Wing-copper numerical qualification, not a new qualification of current Main Rev.6, assembled resistance, ADC performance or GH operation at 125°C.

## Reproduce, verify and hand off

From repository root:

```bash
E=hardware/kicad/qualification/issue-235-wing-round2
python3 "$E/round3.py" reproduce
python3 "$E/round3.py" verify
```

`reproduce` replays the explicit UUID-addressed copper delta from the preserved round-2 PCB, then refills, runs the original native/independent gates, logical contract, resistance extraction, power summary, congestion view, analytic selfcheck, body screen and native post screen for **16L only**. It does not rerun the historical search or KRT; the selected repair is deterministic and reviewable. `round3-diagram.py` and `round3-post-screen.py` reproduce the added visual and mechanical evidence. The inherited `toolchain.json` supplies the same installed KiCad 9.0.9 and geometry tools; no install/download is performed. Scratch, Python/XDG state, UI caches, logs and the private Git database remain exclusively in `.issue235r3-runtime/`.

The protected-file manifest checks **15,735 pre-existing tracked files outside 16L**, including every byte in the other three variant directories, production trees, decisions, baselines, shared round-2 scripts and case evidence. All match. The round-3 evidence manifest binds this report, scripts and saved candidate/evidence. The work is committed on the private `issue-235-16l-closure` branch in `.issue235r3-runtime/git`; PMO can rebase the single delta commit. No push or PR.

The outstanding 16L routing closure is resolved without changing an invariant or rule. The round-2 case passage/structure, housing and wire-dressing acceptance, 200 mm storage/length decision, other-variant target miss and PO Rev.4 adoption gates remain as documented there.
