# Project status

This document is the authoritative record of the project's high-level progress.
Detailed implementation work is tracked by GitHub Issues rather than duplicated
here.

## Current situation (main record confirmed 2026-10-12)

**Location:** Before real Rev.M1/Main design. The current work is qualification
of a repeatable design-to-manufacturing-data method, not product-board design.
EDA-004E's evaluation record was accepted in merged [PR #80](https://github.com/ihsinoky/he-piantor-42/pull/80);
accepting its report is not technical acceptance of KiCad or a product board.

**Current blocker:** No complete design, circuit-check, routing, spacing-check,
manufacturing-output and repeatable-run path is qualified. EDA-004E's fixed
small-fixture acceptance also stopped at two unexpected DRC warnings. Those
warnings are that trial's stop reason, not proof that a method is impossible;
fixing them alone would not qualify the missing product-design path.

**Latest evidence:** With KiCad 9.0.9, the fixed small trial board was created and
saved; the saved file was reopened in a separate program execution. The checked
geometry and connection information were retained for this trial board. This
reduces uncertainty about that board's save/reload behavior only. Main
applicability, a public method in fixed KiCad 9.0.9 for automatically creating a
schematic without GUI interaction, electrically correct
and spacing-compliant routing, effective-rule checking, manufacturing data and
clean-workspace regeneration remain unconfirmed or untested. See the
[EDA-004E report](native-kicad-authoring-feasibility.md).

**Next decision:** Existing constraints and the earlier bounded plan remain
recorded; they are not an authorization for another run after EDA-004E. D-018
prioritized Candidate B for its qualification plan, kept two copper layers,
1.2 mm thickness and 0.20 mm material clearance, put Main before Wing/export,
and capped that plan's first Main evaluation at two workdays. EDA-004B–D are
completed reports from that plan but stopped before routing. The next experiment
after EDA-004E has no approved target, method, implementer or individual
acceptance conditions. PMO prepares a technically bounded proposal and missing
evidence; the PO decides whether to proceed, hold or reconsider direction.
Execution requires a separate PO-created Issue and subsequent PO instruction.
See [D-018](decisions.md#d-018---bounded-alternate-physical-backend-qualification-planning)
and the [historical qualification plan](alternate-physical-backend-qualification-plan.md).

### Current qualification work and product lifecycle

The qualification goal is already defined: demonstrate a suitable path for
creating product-board design data, checking circuit connectivity, routing,
checking the routed connections and required spacing, producing manufacturing
data, and reproducing the result under recorded conditions. These are required
capabilities, **not an approved experiment sequence**.

Existing decisions and limits remain in force within their stated scope:

- D-015/D-017 retain a two-copper-layer, 1.2 mm board baseline; D-018 carries
  the **0.20 mm material-clearance requirement** into its bounded qualification
  plan. These constraints do not prove that a candidate meets them.
- D-018's accepted plan prioritized Candidate B for qualification, not adoption.
  For that plan, Main must pass before Wing/export work; its first Main evaluation
  had a two-workday effort cap, one initial routing run, and one fresh confirmation
  only if the first passed. These limits do not authorize a new run or transfer
  automatically to another candidate.
- The D-018 plan and EDA-004B–D reports are completed planning/evaluation records.
  They do not define an approved next experiment after EDA-004E. That next
  experiment's target, method, implementer and individual acceptance conditions
  remain undecided. PMO prepares the technical proposal and evidence for PO
  decision; execution requires a separate PO-created Issue and PO instruction.

The capability map, latest evaluation coverage and current risks are summarized
by the Dashboard from structured fields.

| Needed capability | Intended output and confirmation | EDA-004E evidence / open state |
| --- | --- | --- |
| Circuit/connectivity definition | Schematic or equivalent circuit definition; separately check component/pin/net consistency before PCB routing. | In fixed KiCad 9.0.9, no public method for automatically creating a schematic without GUI interaction was identified; current Main circuit/connectivity check not entered. |
| PCB data | Board parts/shapes/nets/outline/stack/rules; confirm save/reload preserves shape and connection information and check acceptance DRC. | For the fixed small trial board, the checked shape and connection information were preserved after reopening the saved file in a separate program execution. Initial acceptance failed on two unexpected warnings. Applicability to Main is unconfirmed. |
| Routing | Copper connectivity under physical constraints. | Routing not entered. |
| Circuit and post-route checks | Circuit-level consistency; separately verify routed nets and effective clearance rules. | Current Main connectivity, effective 0.20 mm spacing-rule probe and post-route DRC not entered. |
| Manufacturing output | Board-matched Gerber/drill/BOM/placement and pre-order DFM review. | Not entered for the native KiCad fixture. |
| Reproducible execution | Regenerate equivalent outputs from recorded conditions in a clean workspace. | Empty-workspace regeneration not entered after the initial fixture acceptance failure. |

The accepted D-018 Candidate B plan and its EDA-004B–D reports are historical
planning/execution records, not a current authorization. Their scope, candidate
and stop results remain intact. EDA-004E is a separate later evaluation of native
KiCad board saving; it does not erase D-018's constraints or restart its plan.
Any next evaluation after EDA-004E needs a newly defined target, method, owner and
individual acceptance conditions. PMO prepares that bounded technical proposal;
the PO decides whether it may proceed. No prior candidate's run permission carries
forward automatically.

These functions are related capabilities, not an authorized execution order.
Circuit-level connectivity is distinct from PCB/post-route checks. The two DRC
warnings explain why this trial board failed its acceptance; they do not prove
method-wide impossibility, and resolving them alone would not establish the
other capabilities.

| Current problem / uncertainty | Evidence and consequence | Needed proof / disposition | Owner / source |
| --- | --- | --- | --- |
| Two unexpected DRC warnings stopped initial fixture acceptance. | U1's reference-number printing overlaps a soldering area; the `Resistor_SMD` library is unconfigured. The fixed-trial acceptance criteria were not met. | Warning disposition is unresolved. Any fix is not authorization to continue or sufficient evidence for real-board design. | Technical owner unassigned; [EDA-004E report](native-kicad-authoring-feasibility.md#fixed-fixture-and-measured-results). |
| Fixed-version schematic creation and circuit checking are unqualified. | No public method was identified for automatically creating a schematic without GUI interaction in fixed KiCad 9.0.9; current Main circuit/connectivity check was not entered. | Approved circuit-authoring route and current Main circuit/connectivity evidence; not planned or authorized. | Owner unassigned; [EDA-004E report](native-kicad-authoring-feasibility.md#public-functions-and-fixed-environment). |
| Small-trial results may not apply to Main at product scale. | The read-only Main inventory lists 49 components and 37 electrical connection groups (nets), but is not accepted Main generation/connectivity proof. | Separately authorized Main-scale confirmation for parts, pins, nets, geometry and libraries. | Owner unassigned; [Main coverage](native-kicad-authoring-feasibility.md#representative-main-read-only-coverage). |
| Correct connectivity and required spacing have not been demonstrated together. | EDA-004E did not route; the effective 0.20 mm rule probe was not entered. | Routed connectivity and independent effective-spacing evidence for the authorized target. No router or trial is selected. | Owner unassigned; [EDA-004E report](native-kicad-authoring-feasibility.md#fixed-fixture-and-measured-results). |
| Rule enforcement and clean-workspace regeneration are unknown. | Saved rule settings alone do not prove enforcement; empty-workspace rerun was not entered. | Effective-rule test and regeneration comparison, only if a future plan authorizes them. | Owner unassigned; [EDA-004E report](native-kicad-authoring-feasibility.md#fixed-fixture-and-measured-results). |
| Fixed environment, deprecated PCB API and library maintenance may constrain use. | KiCad 9.0.9 Python SWIG PCB bindings are deprecated (published removal plan: 11); library configuration caused a real warning. Upgrade/maintenance cost is unknown. | Supported maintenance boundary, library/environment reproduction and any migration-cost evidence. No cost estimate is asserted. | Owner unassigned; [EDA-004E report](native-kicad-authoring-feasibility.md#public-functions-and-fixed-environment). |
| Repeated method qualification may delay product work. | EDA-004B–E remain unqualified method evidence. EDA-004E's 0.750 h is an estimated AI-effort allowance, not measured active engineer-hours. | PO chooses continue/hold/reconsider direction and the needed gate/budget. Likelihood and remaining effort are unknown; no mitigation is approved. | PO decision; PMO can organize existing evidence; [history](eda-path-history.md) and [effort record](native-kicad-authoring-feasibility.md#stop-reporting-and-effort). |

The separate product lifecycle is:

1. **Rev.M1 build and measurement:** deliver reusable Main + pitch/magnetic
   Evaluation Wing(s), measurement firmware, pre-order package and measured
   report. G1 reviews ERC/DRC, BOM, manufacturing outputs and measurement plan;
   physical measurements support G2 decisions on range/noise/scan speed/power,
   pitch usability and representative analog path. Firmware is required for
   measurement; the enclosure follows PCB constraints. Hardware implementation
   and the measurement plan are not yet complete.
2. **42-key Rev.A:** use the accepted Main and project-owned Left/Right 21-key
   Wings, subject to G2 and geometry-source approval. Check Main/Wing ERC/DRC,
   manufacturability and firmware build; G3 is a separate pre-order review.
3. **Integration and physical checks:** obtain an assembled unit and procedures;
   verify typing, calibration, USB/Vial and enclosure fit at G4.
4. **Release:** prepare reproducible v1.0 manufacturing, firmware, enclosure and
   procedures for G5 / PO approval.

The specific Rev.M1 board design, firmware milestones, enclosure handoff,
schedule and several acceptance details need planning completion. G1/G2 and
later PO decisions remain distinct from EDA evaluation completion. The disposable
EDA-004E fixture is not the Rev.M1 deliverable.

## Current milestone

**M1 — Magnetic approach / evaluation board** (`current`)

- **Deliverable:** reusable Main board + pitch/magnetic Evaluation Wing(s), measurement
  firmware, and measured-results report. Physical hardware is not implemented yet.
- **Exit criteria:** ERC and DRC pass; physical measurements establish sensor
  range, noise, scan speed, power consumption, and the selected magnetic
  approach, production pitch and representative analog path at G2.

## Roadmap

| Milestone | Status | Deliverable | Exit criteria |
| --- | --- | --- | --- |
| M0 — Design policy / basic geometry | `done` | Historical 42-key requirements, 17 mm layout, and acquisition-method design policy (pitch reopened by D-015) | Principal requirements, key-center coordinates, and evaluation policy are documented. |
| M1 — Magnetic approach / evaluation board | `current` | Reusable Main + pitch/magnetic Evaluation Wing(s), measurement firmware, and measured-results report (hardware not implemented) | ERC and DRC pass; physical measurements establish range, noise, scan speed, power consumption, production pitch, representative analog path, and the magnetic approach. |
| M2 — 42-key Rev.A | `next` | Reuse accepted Main + Left 21-key Wing + Right 21-key Wing + production firmware, subject to G2 pitch/magnetic decision | Main/Wing ERC/DRC, manufacturability checks, and firmware build pass. |
| M3 — Integration / enclosure / test | `todo` | Enclosure, integrated unit, and assembly, calibration, and test procedures | Physical operation, all-key calibration, USB/Vial behavior, and enclosure fit pass testing. |
| M4 — Final release | `todo` | Reproducible v1.0 manufacturing, firmware, and enclosure package | Final artifacts are fixed and the Product Owner approves the completed release. |

## Human Gates

| Gate | Current status | Check | Trigger | Unlock condition |
| --- | --- | --- | --- | --- |
| G0A — JITX Backend Adoption | `done` | C0-C4B5 accepted evidence; Issue #55 PO decision recorded in D-016 | C4C / G0A completed: JITX active physical backend NO-GO for Rev.M1 / Rev.A. | Historical JITX NO-GO remains valid; G0B is done under D-017. D-018's planning scope was accepted at that decision; it did not adopt a candidate or authorize Main. |
| G0B — Rev.M1 Architecture / Interface Freeze | `done` | Accepted connector/pinout, external WING_EN pull-down requirement, evaluation harness, Wings/coverage, test access, measurement framework and DFM boundary in D-017 | Issue #57 PO GO accepted the freeze. | Architecture/interface remain frozen. Subsequent EDA evaluations did not qualify the path; full implementation remains unapproved. |
| G1 — Rev.M1 Main + Evaluation Wing pre-order review | `not-ready` | Actual Main/Wing circuit/ERC, DRC, BOM, manufacturing outputs and measurement plan | Complete manufacturing package exists after separately accepted backend qualification and authorized full Rev.M1 implementation. | Rev.M1 Main + Evaluation Wing ordering may proceed. |
| G2 — Post-EVT-002 magnetic / pitch / analog-path decision | `not-ready` | Measured range, noise, scan speed, power, interference, actual interconnect path and pitch usability | Physical evaluation measurements and report are complete. | Select among 17.0 / 16.5 / 16.0 mm and production magnetic architecture; the Rev.A circuit may be fixed. |
| G3 — Rev.A pre-order review | `not-ready` | Main/Left/Right Wing DRC, BOM, Gerbers, drill/placement outputs and cost | The 42-key manufacturing package is complete. | Rev.A PCBA ordering may proceed. |
| G4 — Physical operation review | `not-ready` | Typing, calibration, Vial, USB, and enclosure fit | Integrated-unit bring-up is complete. | The final design may be fixed. |
| G5 — Final approval | `not-ready` | All v1.0 artifacts and procedures | Acceptance testing passes. | v1.0 may be released. |

## Workstreams

| Workstream | Current high-level state |
| --- | --- |
| Hardware | Historical C0-C4 and EDA-003 results remain in their reports; none qualifies the current Rev.M1 method. D-016 / D-017 / D-018 record their acceptance-time decisions, not a current execution plan. EDA-004B through EDA-004E are completed evaluation records; EDA-004E (Issue #79 / merged PR #80) confirmed save/reload and checked shape/connection information for a fixed small trial board, but failed initial DRC acceptance on two unexpected warnings. Current Main/schematic/routing/manufacturing qualification remains open. Current next direction is undecided; see the current situation above. |
| Firmware | M0 requirements are done; M1 measurement firmware is in progress. Hall/Vial integration and later firmware remain unstarted. |
| Enclosure / Mechanical | M0 geometry constraints are done; M1 is waiting for PCB constraints. Later enclosure integration and manufacturing artifacts remain unstarted. |
| Verification / Test | M0 planning is done; M1 magnetic and power measurement is waiting for the evaluation hardware. Rev.A bring-up and later testing remain unstarted. |

## Historical engineering evidence and accepted product requirements

This section records accepted historical evidence and product requirements; it
is not the current next-step plan. The current location and unresolved method
qualification are summarized at the top of this document. Issue #19's Human Gate returned GO for native stock
tscircuit, so EDA-001 is done and EDA-000 is retired fallback/reference. PR #27
completed EVT-001 and froze `hardware/tscircuit/src/evaluation/m1-four-key.tsx`
and its Checkpoint A/B/C evidence as the M1 electrical golden reference. D-014
remains the accepted historical decision that made native tscircuit the M1
electrical source.

EDA-002C0 passed the technical JITX graph-export gate through the documented
`Export` plugin boundary: it captures stable structural paths, component types,
ports, resolved nets, and port membership from the actual bootstrap build.
`RuntimeDesign.query()` and its net-resolution methods are documented but
explicitly experimental; PMO accepted that category-B surface for the JITX
challenger/parity evaluation workflow without classifying it as stable.
Any future JITX Python package or runtime version change must rerun and pass
the EDA-002C0 normalized graph exporter and bootstrap graph self-test before
graph-parity compatibility may be assumed. EDA-002C1 is accepted/done: all nine
manufacturer models passed and PR #36 was merged into main at a27fc48.
EDA-002C2 (issue #37) is done / accepted / merged PR #38 at `67b6c302`,
electrical graph parity PASS: 68 components, 200 normalized endpoints, 43 named
nets, 185 endpoint/net edges, four direct links and seven intentional NCs.
Actual RuntimeDesign exports are deterministic; the 20-test suite includes
bootstrap regression and C2 fault-injection coverage. Geometry parity is
explicitly NOT established.

EDA-002C3 (issue #39 / merged PR #40, baseline `bc061435`) remains valid
historical evidence. The [unchanged report](../hardware/jitx/geometry/EDA-002C3.md)
and reconciliation record preserve their recorded discrepancies and Human Gate
states; not all geometry questions are resolved. They do not invalidate C2.
Exact geometry convergence against the legacy reference is no longer a JITX
adoption criterion; manufacturer evidence should inform the new product.
No old tscircuit geometry is corrected in C4A.

EDA-002C4A (issue #41) is accepted / merged PR #42; documentation/architecture
rebaseline only. The old footprint-alignment plan is cancelled. The golden is
a permanent qualification oracle, not the physical Rev.M1 manufacturing design.
[D-015](decisions.md#d-015---revm1-reusable-main--evaluation-wing-architecture)
accepts reusable Main + Evaluation Wing architecture: Main owns RP2040,
USB/power, three ADC channels and dividers/filters; Wing owns Hall/TMUX and
pitch-test geometry. Compare 17.0 / 16.5 / 16.0 mm for magnetic performance and
usability; 100 x 100 mm is a cost target, not a pitch requirement. Rev.A's
first-choice is accepted Main reuse + Left/Right 21-key Wings, three TMUX1208
each, generated from one project-owned definition; separate manufacturing
outputs are allowed, without a reversible PCBA requirement.

The following C4B-C4B3 summaries record historical results. The C4B4B
disposition below records the then-current path/product status at its acceptance;
later EDA-004B–E evaluations supersede that historical EDA-route state. Their
reports and evidence remain unchanged.

**EDA-002C4B investigation: BLOCKED** (issue #43). The disposable four-key
qualification wrapper builds with explicit 68-component placement, partial
copper on two layers/two vias, ODB++ and public BOM/PnP review exports. The two
fresh generations repeat captured geometry and CSVs; ODB order/IDs vary.
Full routing, complete DRC and a qualified Gerber/Excellon JLCPCB handoff remain
unproven. C2 electrical parity remains PASS. See the
[C4B evidence](../hardware/jitx/physical/EDA-002C4B.md).

**EDA-002C4B2 downstream CAM: BLOCKED** (issue #45 / merged PR #46).
The unchanged fixture generates JSON DRC, nine Gerber layers, PTH/NPTH Excellon
and 68-row PnP through KiCad 9.0.9 twice from fresh state. Its 147 missing
connections reconcile with C4B's intentional partial routing. Four USB source
copper-to-NPTH clearance conflicts and exported 1.6 mm thickness contradicting
the 1.2 mm source stack block manufacturing qualification. No manufacturing
geometry/drill/assembly-coordinate difference was found between runs; all raw
differences are retained. Historical evidence, versions and full routing remain
unchanged. See [C4B2 evidence](../hardware/jitx/physical/EDA-002C4B2.md).

**EDA-002C4B3 manufacturing disposition: BLOCKED** (issue #47 / merged PR #48).
The thickness mismatch originates in a fixed 1.6 mm runtime export template;
no supported overall CAD/job override was found. A supported limited handoff
excludes the optional job and specifies 1.2 mm independently, preserving all
individual Gerber/drill bytes. Current JLCPCB rigid FR-4 NPTH capability is
0.20 mm; the 0.25 mm fixture rule was a qualification default. The smallest
USB gaps are 0.20009999 mm and remain marginal release blockers. Rev.M1 DFM
policy separates capability floor, 0.25 mm target and numerical review guard;
exceptions require evidence. Fresh two-run CAM/source reconciliation and all
20 C0/C1/C2 regressions pass. Historical evidence, topology, manufacturer
geometry and partial routing remain unchanged. Incomplete routing is **not**
the only major remaining issue. See [C4B3 evidence](../hardware/jitx/physical/EDA-002C4B3.md).

**EDA-002C4B4A completed / merged PR #50** (issue #49): the qualification-only
coupon preserved accepted connector geometry and provided the exact human-upload
ZIP. See [C4B4A](../hardware/jitx/physical/EDA-002C4B4A.md).

**EDA-002C4B4B accepted external evidence disposition** (issue #51; merged PR #52).
Human JLCDFM observation is **INCONCLUSIVE** for the exact
NPTH-to-adjacent-pad-copper measurement; the viewer exposed no measured result.
Absence of a warning is not production approval. The JLCPCB Japan support/sales
response received 2026-10-05 confirms a **0.20 mm minimum capability**, numerically
met by all four accepted-source gaps (0.2000999900 / 0.2348831648 mm).
JLCPCB recommends additional clearance where feasible without specifying 0.25 mm.
The **0.25 mm preferred target** and **0.001 mm numerical review guard** remain
project-owned, not JLCPCB requirements or recommendations.

**JITX -> legacy-kicad -> KiCad -> Gerber/Excellon: PASS_WITH_LIMITATIONS.**
Accepted source geometry was preserved; USB gaps are connector properties,
not export distortions. The misleading generated CAD/Gerber-job overall thickness
metadata must be excluded from production handoff; independently select/confirm
**1.2 mm finished thickness**. This does not qualify a production PCB or complete
routing/DRC.

**USB product release: OPEN — PRE-ORDER DFM REVIEW REQUIRED.** USB margin is
reclassified from a JITX-backend qualification blocker to a product manufacturing
risk. Before any actual Rev.M1 / Rev.A fabrication order, increase clearance
where feasible, or explicitly accept/document manufacturer-minimum geometry and
pass actual order-time CAM/process review. No production exception is granted.
See [C4B4B disposition and external evidence](../hardware/jitx/physical/EDA-002C4B4B.md).

**EDA-002C4B5 — done / accepted BLOCKED evidence** (issue #53; merged PR #54).
Public source Route trees retain 40 downstream unconnected items; a representative
two-via escape retains 39 and a dangling via. C2 topology and manufacturer geometry
remain unchanged. Complete routing and successful two-run reproducibility are
unqualified. See [C4B5 evidence](../hardware/jitx/physical/EDA-002C4B5.md).
**EDA-002C4C / G0A is complete**: the [Issue #55 PO decision](https://github.com/ihsinoky/he-piantor-42/issues/55#issuecomment-5991285003)
is **NO-GO for JITX as the active physical backend for Rev.M1 / Rev.A**, recorded
in [D-016](decisions.md#d-016---jitx-physical-backend-no-go-native-tscircuit-resumes-as-active-revm1-eda-candidate).
The primary reason is the complete-routing workflow not demonstrated in C4B5,
not USB DFM or the separate generated-thickness metadata limitation. Accepted
electrical/component/modeling successes and all JITX source/evidence remain
valid and retained. At that historical D-016 acceptance, native stock tscircuit
resumed as the forward candidate/path, subject to later ERC/DRC and manufacturing
gates; physical Main/Wing remains unimplemented and is not production-qualified.
**G0B is done / accepted** by the [Issue #57 PO GO](https://github.com/ihsinoky/he-piantor-42/issues/57#issuecomment-6010634587) and
[D-017](decisions.md#d-017---revm1-mainwing-architecture-and-interface-freeze).
The JST GH 14-position connector/pinout, six common-GND return contacts, nominal
100 mm 1:1 evaluation harness, external Main-side pull-down per `WING_EN`,
three pitch Wings and full-load three-TMUX/three-ADC coverage are frozen.
The exact pull-down resistor value remains implementation work.

**Historical EDA evaluation sequence (completed through EDA-004E):**
EDA-004D / Issue #77 / PR #78 CONVERSION_BLOCKED -> EDA-004E / Issue #79 /
PR #80 PCB_IO_PASS / FRONTEND_UNQUALIFIED. This records the evaluation history,
not a current next-step plan. Main remains unqualified and full implementation/
adoption remains unapproved. Current next direction is undecided as stated at the
top of this document.
See [EDA path history](eda-path-history.md) and
[native KiCad feasibility](native-kicad-authoring-feasibility.md).
Full Rev.M1 implementation requires separate authorization. No
schematic/PCB/manufacturing package completion, placement, routing or order
is claimed. Production pitch, final Hall choice, final Rev.A cable mechanics/length,
exact pull-down resistor, final placement, PCB routing, representative Main
routing qualification, USB NPTH manufacturing disposition, final USB/system
power budget and manufacturing release remain open. The accepted DRV5055 5 V
basis (3 mA typical / 5 mA maximum) yields approximately 127 mA per 21-key Wing
and 254 mA for 42 sensors / two Wings: planning estimates, not final USB/system
power qualification or final production requirements. `hardware/layout/**` is not consumed; future Wing
geometry must be project-owned or explicitly approved at a later Human Gate.
See [Rev.M1 architecture](../hardware/rev-m1/architecture.md),
[interface](../hardware/rev-m1/main-wing-interface.md),
[evaluation plan](../hardware/rev-m1/evaluation-plan.md) and
[DFM policy](../hardware/rev-m1/dfm-policy.md).

EDA-002A's Cloud Codex capability probe remains historical evidence of that
environment's HUMAN / ENVIRONMENT STOP. EDA-002B subsequently passed the
GitHub Codespaces JITX environment/bootstrap feasibility gate: its canonical
project uses `jitx==4.4.3`, runs against the already validated Linux runtime
4.4.2, and completed a real bootstrap build. EDA-002C0 then passed its
documented graph-introspection proof. See
[`jitx-evaluation.md`](jitx-evaluation.md) for the evidence and stability
classification. The JITX challenger evaluation ended in physical-backend
NO-GO at C4C/G0A; all historical qualification evidence is retained. C4B4B
classifies the demonstrated JITX downstream path PASS_WITH_LIMITATIONS; C4B5
remains accepted BLOCKED for complete routing. G0B remains accepted.
EDA-003B through F are completed historical work;
D-018 remains unchanged. EDA-004B's environment STOP and EDA-004C / Issue #75's
conversion STOP are historical results, superseded as the latest evaluation by
the later EDA-004D/#77 and EDA-004E/#79 records.

The previous spike established reproducibility with a committed dependency
lock, fresh GitHub Actions `npm ci`, Bun 1.2.22, tscircuit 0.0.2646, and
non-interactive CI bootstrap. Its KiCad footprint-import path stopped at
footprint integrity: conversion of `SW_MX_HE_0deg_1u.kicad_mod` using
`kicad-to-circuit-json` 0.0.117 preserved Hall SMD pads, the plated through-hole
pad, duplicate pad-number semantics, two NPTH switch holes, plated/non-plated
distinction, mechanical alignment, and an observed Y inversion, but lost two
copper-pour keepout zones. Therefore KiCad import is not the authoritative
migration path. This result does not rule out native tscircuit design.

**EDA-003A / merged PR #59: accepted UPSTREAM_FIX_CANDIDATE.** Both copper-pour
keepouts were silently lost, warnings did not report the material loss, and
rounded-pad corner radius was incorrect. Current KiCad footprint importer
reuse is **NOT approved**. Native TSX remains authoritative; KiCad assets
remain reference / secondary evidence. Future importer reuse needs separately
accepted fidelity evidence after fixes. Details remain in the
[requalification report](tscircuit-kicad-importer-requalification.md).

Existing KiCad work remains unchanged as reference and prior-design evidence,
but is not the active EDA source. Each detailed increment is
defined and accepted through its own GitHub Issue.


## EDA-003 history and current planning decision

Completed qualification work does not mean a qualified board or adopted backend.
All reports and evidence remain unchanged:

| Work | Actual terminal classification | Evidence / implication |
| --- | --- | --- |
| EDA-003B (Issue #61 / PR #62) | **BLOCKED — ROUTING_CAUSED_PHYSICAL_ERRORS** | [Report](tscircuit-revm1-routing-proof.md): production 0.0.2646; zero required unrouted, seven Main wrong-net copper components; material Main/Wing errors. |
| EDA-003C (Issue #63 / PR #64) | **WRONG_NET_FIXED_LOWER_RISKS_REMAIN** | [Report](tscircuit-latest-routing-risk-qualification.md): isolated stock 0.0.2748, zero required unrouted/wrong-net; 71 Main material records, Wing errors and Main export assertion failure remain. No production upgrade. |
| EDA-003D (Issue #65 / PR #66) | **BACKEND_DECISION_REQUIRED** | [Report](tscircuit-main-clearance-risk-triage.md): BROAD / DISTRIBUTED, 71 records / 54 physical conflicts / 37 net/NC pairs; no demonstrated fixes. |
| EDA-003E (Issue #67 / PR #68) | **BACKEND_DECISION_REQUIRED** | [Report](tscircuit-via-clearance-signature-probe.md): strong 0.115 mm numeric correlation; repair boundary/size unqualified. |
| EDA-003F (Issue #69 / PR #70) | **INTERVENTION_UNSAFE_REGRESSION — K1** | [Report](tscircuit-clearance-intervention-ab.md): control 71 records / 54 conflicts; intervention zero required unrouted but two wrong-net components. Confirmation and physical comparison not entered. |

The [explicit Issue #71 PO comment](https://github.com/ihsinoky/he-piantor-42/issues/71#issuecomment-6046244229)
is recorded in [D-018](decisions.md#d-018---bounded-alternate-physical-backend-qualification-planning).
Additional product-track exploration of the evaluated internal tscircuit router
has ended. Frontend retention is still being evaluated. Candidate B is the first
bounded qualification candidate, **not adopted**. Production tscircuit remains
**0.0.2646**; representative Main routing remains **unqualified**.

**EDA-004B / [Issue #73](https://github.com/ihsinoky/he-piantor-42/issues/73):
ENVIRONMENT_BLOCKED — P1_SMOKE_CAPTURE_GUARD_ERROR.** The PO authorized the actual
execution Issue incorporated from the fixed planning documents. The first failure
was the executor smoke guard rejecting permitted local copper before raw JSON
capture. This is an executor verification/capture error, not EDA/backend incapability.
A subsequent converter invocation, despite that failure, observed the secondary
environment obstacle **P1_CONVERTER_MODULE_LOAD** (`dist/index.js` absent).
Immediate-stop discipline was not followed. Stage 1 was partial; Main transfer, ERC/DRC,
independent KiCad reconciliation, initial routing and fresh confirmation were
**NOT ENTERED**. Main initial/confirmation counts are **0/0**, smoke routing **0**.
All Main acceptance metrics are null. The executor's smoke guard rejected allowed
local bond copper before raw JSON capture, and the converter was attempted after
that capture failure; P0 freeze was incomplete. Evidence is **PARTIAL**, with
these limitations disclosed in the [terminal report](alternate-physical-backend-main-qualification.md).
Terminal reporting is complete; technical qualification is incomplete. The PO
relayed a PMO chronology finding; correction acceptance and backend PASS are not
claimed. That environment/capture correction was subsequently authorized for
EDA-004C / Issue #75, whose new result is below. Issue #71's historical planning
and [execution draft](alternate-physical-backend-main-qualification-issue-draft.md)
remain unchanged. Aggregate cap remains 16 engineer-hours; later work still needs
separate PO authorization and Main PASS before Wing/export.
**EDA-004C / [Issue #75](https://github.com/ihsinoky/he-piantor-42/issues/75) / PR #76:
CONVERSION_BLOCKED — C1_DUPLICATE_GND_PAD_NET_LOSS.** Fixed-source kicadts build,
converter module load, raw capture/stop-control tests and headless KiCad 9.0.9
schema/binding probes succeeded. Source/Circuit JSON geometry and defined
synthetic pin/circuit checks passed after disclosed preparation corrections.
KiCad conversion loses the second U_TX pin2 land's GND net; pre-route DRC reports
one shorting_items and one solder_mask_bridge error. Schematic conversion emits
duplicate Device:U_chip definitions and passive input/output pins; KiCad ERC
reports two pin_not_connected errors. Library warnings are retained and meaningful
ERC remains unqualified. Experiment stopped before DSN; initial/fresh smoke
routes **0/0**, Main **0**. DSN/SES, post-route checks and reproducibility are
**NOT ENTERED**; acceptance metrics remain null. New raw evidence does not restore
EDA-004B's missing output. Read-only parity fault replay detected 26 injected
faults; it does not qualify the full post-route island/clearance verifier.
See the [new report](alternate-physical-backend-smoke-requalification.md).
PMO/PO reviews this conversion STOP; no automatic repair, retry or candidate switch.
The four-hour Issue budget and original cumulative 16-hour cap are retained;
known AI estimates and unobserved historical/human effort are separated in the report.

Full Rev.M1 implementation, backend adoption and ordering remain blocked.
G0A/G0B remain done; G1-G5 remain not-ready. Codex does not reopen or pass Human
Gates. The historical forward sequences in D-016/D-017 and architecture/interface/
DFM documents describe their acceptance-time state; D-018 governs current planning.
USB NPTH **OPEN — PRE-ORDER DFM REVIEW REQUIRED**, unselected production pitch
and the other product risks listed above remain unchanged.

## Dashboard synchronization

`docs/project-status.md` is authoritative for high-level project status.
`task/data/project-status.js` is a manually synchronized Dashboard read-model
copy. If they conflict, this document is correct. Synchronization is reviewed in
the same pull request as a status change; there is currently no generator or
automatic synchronization.

## EDA-004E native KiCad feasibility (accepted report; evaluation-time result)

[Issue #79](https://github.com/ihsinoky/he-piantor-42/issues/79) evaluation record was accepted in merged PR #80:
**PCB_IO_PASS / FRONTEND_UNQUALIFIED**, STOP recommended before Main.
In KiCad 9.0.9, the fixed small trial board's checked shape/connection information
was retained after its saved file was reopened in a separate program execution.
Initial trial acceptance fails two unexpected DRC warnings (U1 reference-number
printing over a soldering area, unconfigured official footprint
library); the two expected unconnected links are identified separately.
Effective-rule negative test and conditional empty-directory regeneration are
NOT ENTERED. No public method for automatically creating a schematic without
GUI interaction was identified for fixed KiCad 9.0.9;
current Main ERC/parity and Main generation/routing/manufacturing are NOT ENTERED.
Deprecated SWIG binding and exact-library/rule maintenance remain additional work.
[Result/evidence](native-kicad-authoring-feasibility.md) and
[history/retry conditions](eda-path-history.md) preserve prior decisions.
EDA-004D's merged PR #78 retains its footprint-library identity collision STOP.
No backend adoption, Human Gate or full implementation authorization is implied.
