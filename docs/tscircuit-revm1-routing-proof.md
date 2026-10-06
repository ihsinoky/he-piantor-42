# EDA-003B — representative Rev.M1 routing proof

**BLOCKED** on a connector evidence prerequisite. Execution stopped before
native footprint or representative board implementation. This is **not a
finding that stock tscircuit cannot route Rev.M1**. Issue #61 remains incomplete
and must remain open. No EDA adoption or Human Gate decision is made.

## Baseline and preflight

On 2026-10-06 the working tree was clean; branch was
`eda-003b-revm1-routing-proof`; HEAD and merge-base with refreshed `origin/main`
were `d97414b16482990452d9f7bfec9aac25bed5bbd9`. Production manifest and lock both
specify `tscircuit 0.0.2646`. Clean `npm ci` succeeded (298 packages added), and
did not modify either file. Initial sandbox filesystem/DNS restrictions were
resolved through approved execution; they are not the blocker.

Read the entire [Issue #61](https://github.com/ihsinoky/he-piantor-42/issues/61)
and its comments (none), decisions, project status, all five Rev.M1 authority
documents named in the task, native spike report, EDA-003A report, production
manifest/lock, HallKey, frozen four-key source, Checkpoint C source/generator/
manufacturing verifier, and M1 electrical verifier. No applicable AGENTS.md was
found. No JITX source was used as physical authority.

## Exact prerequisite and missing evidence

[Accepted G0B section 2.1](../hardware/rev-m1/g0b-freeze-proposal.md#21-candidate-comparison)
requires: “The catalogue dimensions must be transcribed and independently
checked against approved manufacturer CAD before creating the native footprint.”
Section 11.3 also records that this review has not occurred.

The public [JST GH catalogue](https://www.jst-mfg.com/product/pdf/eng/eGH.pdf)
was downloaded and visually inspected, including the mounting-surface land
pattern and exact BM14 row. It establishes 14 contacts, 1.25 mm pitch,
16.25 mm contact span and 20.75 mm header width. The top-entry drawing identifies
pin 1 at the right, 0.6 mm signal-land width, two 1.0 x 2.8 mm reinforcement
lands, and a 5.6 mm overall pattern depth. The 1.7 mm signal-land length is
derived from 5.6 minus 3.9 mm. These are catalogue nominal dimensions, **not an
independently CAD-verified native footprint**. No copper or port numbering has
been authored from them.

JST's [GH product page](https://www.jst-mfg.com/product/index.php?lang=2&series=105)
lists BM14B-specific 2D and STEP data. Its
[2D PDF request](https://www.jst-mfg.com/product/index.php?doc=4&filename=BM14B-GHS-TBT.pdf&series=105&type=10)
and [STEP request](https://www.jst-mfg.com/product/index.php?doc=2&filename=BM14B-GHS-TBT.zip&series=105&type=10)
both lead to a contact-details form and email delivery, introduced in April
2025. They do not supply the files directly. No form was submitted, identity
invented, email sent, access control bypassed, or restricted CAD redistributed.
Repository file searches and exact-part web searches found no usable approved
manufacturer CAD/drawing for the independent check.

Thus nominal catalogue geometry is available, but the accepted independent
manufacturer-CAD comparison is unavailable. This distinction matters: no
unproved pad/body/orientation assumptions should enter the routing authority.
Pin-1 marking, keyed mating orientation, hold-down geometry, body clearance,
and top-entry cable/latch access near a board edge still need that comparison
and review. Board-edge/cable clearance has not been qualified.

To resume: provide a lawfully readable, approved BM14B-GHS-TBT manufacturer
drawing/CAD asset and compare it with the catalogue before authoring the native
footprint. Alternatively, the PO can explicitly revise the accepted CAD-check
requirement for this disposable qualification. This report grants no exception.

## Installed stock routing capability

Primary evidence is the clean installed source/types from the **unchanged
committed lock**, not current upstream documentation. Aggregate pin alone is
insufficient to describe this installation: core is `0.0.1971`, props `0.0.666`,
capacity-autorouter `0.0.919`, checks `0.0.208`, Circuit JSON `0.0.499`, and CLI
`0.1.2170`. Full versions and source hashes are in
[router-capability.json](../hardware/tscircuit/qualification/eda-003b/evidence/router-capability.json).

| Surface | Installed evidence and conclusion |
| --- | --- |
| Board router configuration | Public props `AutorouterProp` accepts strings or `AutorouterConfig`; `default`, `auto`, and `auto_local` resolve to local subcircuit routing in core `getPresetAutoroutingConfig`. Existing Checkpoint C uses `autorouter="default"`. |
| Local/network | With ordinary `new Circuit()` and `default`, core selects `AutoroutingPipelineSolver9_PreloadedTraceGraph`. The networked solver is selected only with platform `useCloudAutorouter`; legacy `auto_cloud` also exists but is deprecated/gated. No cloud service is needed for the default path inspected. |
| Layers/vias | Public BoardProps supports `layers={2}`, thickness, and via diameter rules. Blind/buried vias default false; core converts router via points to physical `pcb_via` records carrying layers, start/end layer and diameters. Checkpoint C proves an explicit top/bottom via, **not automatic via generation on this representative design**. |
| Source constraints | Public routing tolerances include trace width, trace-to-pad, pad-to-pad, board-edge, via-to-pad, drill-to-drill clearances and via hole/pad diameters. Trace props include width, `maxLength`, `maxViaCount`, `pcbPath`/`pcbPaths`, and routing phase index; trace hints and autorouting phases exist. None were applied to a new board. |
| Effort | Public `autorouterEffortLevel` offers 1x/2x/5x/10x/100x. No effort tuning was performed. |
| Failure visibility | Circuit publicly exposes autorouting start/end/error/progress and solver events. Placement-check errors can skip routing and emit `pcb_autorouting_error`. Router failure emits an error with capacity-router version context. `renderUntilSettled()` polls until done and contains no wall-clock deadline; a future runner needs an explicit bounded process timeout. Internal cycle-scheduling timers are not routing deadlines. |
| Physical schema | Records include `pcb_trace_error`, `pcb_trace_missing_error`, `pcb_port_not_connected_error`, `pcb_autorouting_error`, placement, footprint overlap, board-boundary, pad-clearance and via-clearance errors. Keepout overlap can also be a warning and must not be ignored. |
| Stock checks | Public checks cover port contact, missing traces, contiguity, overlaps/shorts, pad/trace and via clearance, placement, boundary and keepout. No exhaustive invalid-layer-transition validator was established. A future verifier must explicitly check layer/via consistency. |
| Export | Proven repository path is stock `tsci export circuit.json --format gerbers --output manufacturing.zip`, containing top/bottom copper, outline, plated/NPTH drill, BOM and PnP. No representative candidate was exported. |

No newer release was installed or used. No exact newer-version routing fix is
recommended: **there is no pinned-router failure to diagnose yet**.

## Physical verification boundary

The public `PcbConnectivityMap` analyzes PCB traces, port attachments and
same-layer trace intersections; `getFullConnectivityMapFromCircuitJson` includes
logical/source membership and must not alone establish physical success.
The installed stock contiguity checker also considers pad contact and via
contact. A future repository verifier must reconcile required source groups
with generated physical pad/trace/via connected components, prove NC intent,
and count the missing physical connections. Endpoint annotations or a router
completion event alone are insufficient. These APIs were inspected, **not
qualified as a complete Main/Wing connectivity verifier**.

`runAllRoutingChecks` calls `addStartAndEndPortIdsIfMissing`, so it is not
strictly input-immutable. Any future read-only wrapper must pass a cloned
in-memory array and preserve/hash the untouched generated file. No generated
data was repaired in this investigation.

## Representative fixture and metrics

The intended fixture remains the user-requested disposable, non-product Main
and Wing, with native TSX authority and two copper layers at 1.2 mm. Neither
board was implemented because the connector prerequisite precedes placement.
No compact dimensions, placements or routing strategies were selected.

| Item | Qualification result |
| --- | --- |
| Main | Not implemented. Required scope remains RP2040, USB-C/ESD, QSPI, clock, decoupling/core power, 3.3 V regulator, TPS22919/HALL_5V, three ADC filters, GH14, address/enable, external enable pull-down, six GND contacts and SWD/RUN access. |
| Wing | Not implemented. Required scope remains GH14, three TMUX1208, four HallKey sensors distributed 2/1/1, local decoupling and all three analog outputs. |
| Board dimensions | Unselected for both boards. |
| Routing attempts | None; attempt 1 was not reached. No placement tuning, enlarged outline or deleted circuitry. |
| Source net / required endpoint / trace / via / intentional NC counts | Unmeasured (`null` in evidence), not zero. |
| `electrically_required_unrouted_count` | Unmeasured (`null`); no connectivity PASS. |
| Physical errors | No representative Circuit JSON exists; unmeasured. |
| Manufacturing | Not run for the qualification; no completely routed candidate exists. |
| Two fresh runs | Not run for the qualification; no reproducibility claim. |

USB NPTH remains **OPEN — PRE-ORDER DFM REVIEW REQUIRED**. No new USB geometry
was authored; no tool-specific corruption was observed or evaluated on a new
board. Existing product risk is not classified as a router failure.

## AI/source-control assessment

1. Native placement, connections and constraints are reviewable in TSX in the
   existing fixtures; representative Main/Wing intent has not been authored.
2. Stock local routing produces copper without GUI state on Checkpoint C;
   usable representative routing is unproven.
3. Codex can edit supported source placement/constraints and regenerate, but
   no representative failure-guided iteration was performed.
4. Public events, errors and checks provide machine-visible diagnostics;
   their adequacy for dense Rev.M1 congestion is untested.
5. Lock reproducibility is established; representative material routing and
   manufacturing reproducibility remain untested.
6. No handwritten route geometry was added; the amount needed for Rev.M1 is
   unknown.
7. Whether routine Rev.M1 maintenance requires interactive EDA is unknown.
8. Compared with accepted JITX C4B5, tscircuit exposes a local global-routing
   surface, but this investigation has **not demonstrated complete routing**
   and therefore does not close the specific AI/source-controlled workflow gap
   that led to JITX NO-GO. No general superiority claim is made.

Full Rev.M1 implementation must remain inactive pending completion and human
acceptance of EDA-003B. D-018, project-status acceptance, EVT-002 and all Human
Gates are unchanged.

## Validation and preservation

Clean `npm ci` passed; the existing native Checkpoints A and B verifiers,
Checkpoint C generator, and frozen M1 electrical verifier all exited zero with
every assertion passing. Checkpoint C regenerated three PCB traces, one
source-authored via, two keepouts, two layers, 1.2 mm thickness and zero emitted
`*_error` records. These are historical regression results, not representative
qualification metrics or a new independent complete-connectivity proof.

Representative generation, physical connectivity/error verifiers,
manufacturing verification and two-run comparison are deliberately not run
after the prerequisite STOP. No placeholder verifier or toy replacement board
was created. Applicable historical manufacturing CI was not rerun.

The manifest/lock and frozen four-key SHA-256 values are recorded in
[environment.json](../hardware/tscircuit/qualification/eda-003b/evidence/environment.json).
Baseline byte comparisons verify these files, all EDA-003A evidence, JITX
evidence and old KiCad assets are unchanged. `git diff --check` passes. Only this
report and compact evidence are committed; no node_modules or generated board
files are included. No PR, Issue, merge, order or external message was created.

Primary classification: **BLOCKED** — accepted connector evidence prerequisite;
representative stock-router capability remains unqualified.
