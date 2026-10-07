# Design Decisions

This file records decisions that materially affect hardware, firmware, manufacturing, or enclosure design.

## D-001 - One-piece geometry

Status: provisional

Interpret "120-degree reverse-V" as an internal angle of 120 degrees between left and right key fields, with the left field at +30 degrees and right field at -30 degrees in the project coordinate convention (+x right, +y down).

Reason: this is the simplest consistent geometric interpretation and is easy to review visually once the Piantor key centers are transformed.

## D-002 - Key pitch

Status: historical provisional baseline; fixed production pitch superseded/reopened by D-015

Historical decision (retained): Use 17.0 mm pitch rather than 16.5 mm.

Reason: 16.5 mm square narrow MX-stem keycaps exist. At 17.0 mm center spacing this leaves a nominal 0.5 mm cap-to-cap gap. A 16.5 mm pitch would leave no nominal gap.

D-015 reopens production pitch: 17.0 mm remains an evaluation candidate alongside
16.5 and 16.0 mm. The historical clearance rationale above remains evidence,
not a final production-pitch requirement.

## D-003 - Magnetic switch

Status: provisional baseline

Use Gateron Magnetic Jade Pro HE / KS-20-compatible as the primary design reference.

Reason: it is a full-height HE switch, has published magnetic values at 1.2 mm PCB thickness, and has current Japanese availability.

Do not release the 42-key production PCB based only on nominal switch data. Validate the sensor range with a small evaluation board first.

## D-004 - Power indication

Status: accepted

Use a dedicated power indicator LED independent of the MCU.

Reason: it provides a basic hardware diagnostic when firmware or USB enumeration fails.

## D-005 - Layer indication

Status: accepted

Use a separate MCU-controlled RGB LED for four-layer indication.

## D-006 - Manufacturing strategy

Status: accepted

Target JLCPCB PCBA for the assembled PCB and FDM printing for the first enclosure.

## D-007 - Project tracking

Status: accepted

The documents under `docs/` are the authoritative record of project state and
decisions. The Dashboard is a human-readable project overview and read model,
not a source of truth. Production Dashboard deployments represent merged
`main`; a PR Preview may be used to inspect a proposed state before merge.

Reason: separating the reviewed project record from its presentation prevents
stale runtime, GitHub, or deployment snapshots from overriding design decisions.


## D-008 - PCB thickness

Status: provisional baseline

Use 1.2 mm PCB thickness for both the Hall evaluation board and the 42-key production board.

Reason: the Gateron Magnetic Jade Pro reference data publishes switch magnetic-flux values at 1.2 mm PCB thickness. Keeping the evaluation and production geometry equal avoids adding PCB thickness as an uncontrolled magnetic-distance variable.

## D-009 - Hall analog power rail

Status: provisional baseline pending current measurement

Power Hall sensors and analog multiplexers from a switched USB VBUS rail named HALL_5V. Use TPS22919DCKR as the baseline load switch controlled by GPIO7.

Reason: forty-two linear Hall sensors are a significant continuous load. Supplying them through the 3.3 V logic LDO would add unnecessary regulator dissipation. A switched 5 V rail also permits controlled startup and fault isolation.

## D-010 - Hall multiplexing topology

Status: provisional baseline pending evaluation

Use TMUX1208 rather than 5 V 74HC4067 devices. The production board uses six TMUX1208 devices as two banks of three, with seven used sensor inputs per mux.

Shared address lines are MUX_A0..A2. MUX_EN0 and MUX_EN1 select the 21-key bank. Three mux outputs feed RP2040 ADC0..ADC2 through 6.8 kOhm / 10 kOhm dividers and 1 nF ADC-node capacitors.

Reason: TMUX1208 explicitly supports low-voltage digital control while operating from the 5 V analog rail. Three ADC channels sampled per address reduce the number of sequential acquisition slots to 14 for all 42 keys.

## D-011 - Evaluation board before main PCB

Status: accepted measurement intent; one-piece four-key physical implementation assumption superseded by D-015

Do not release the 42-key PCB until a four-key Hall evaluation board has measured:
- switch travel curve and polarity,
- usable ADC span and clipping margin,
- noise and repeatability,
- mux settling time,
- adjacent-key magnetic coupling,
- Hall-rail current and turn-on behavior,
- short-term thermal drift.

Reason: Hall switch behavior depends on the switch magnet, Hall sensor, PCB thickness, physical alignment, analog path and firmware timing as one system. Nominal component specifications alone are not sufficient for the production PCB.

D-015 replaces the one-piece four-key physical implementation with a reusable
Main + Evaluation Wing(s). The historical requirement above to physically
validate Hall behavior before releasing the 42-key design remains valid.

## D-012 - PCB layer baseline

Status: accepted

Use a two-layer PCB for the evaluation board and as the current production
baseline. Prioritize JLCPCB's low-cost manufacturing options. Four-layer
capability is not a current project requirement; if it becomes necessary, it
must be reconsidered through a separate design decision and Human Gate.

This layer baseline does not change D-008: both the Hall evaluation board and
the production board retain the 1.2 mm PCB-thickness baseline.

Reason: a two-layer baseline keeps the current evaluation aligned with the
project's low-cost manufacturing objective without treating an unneeded
four-layer capability as an EDA acceptance criterion.

## D-013 - EDA backend evaluation strategy

Status: accepted evaluation baseline

Do not adopt automatic KiCad-to-tscircuit import as the authoritative migration
path. Evaluate a greenfield design written in native TypeScript / TSX, using
stock tscircuit, before implementing the evaluation PCB. The intended flow is:

```text
requirements / datasheets / verified geometry
    -> native TypeScript / TSX
    -> stock tscircuit
    -> 2-layer PCB
    -> Gerber / Drill / BOM / PnP
    -> JLCPCB
```

Before a GO decision, do not introduce a tscircuit fork, Circuit JSON fork, or
custom Gerber exporter. Generated Circuit JSON and Gerber files must not be
edited directly. Repository-owned validation and tests are permitted. Existing
KiCad designs remain available as fallback, reference, and prior-design
evidence, and must not be removed before the migration GO decision.

Reason: the earlier Issue #13 spike proved a reproducible non-interactive setup:
a committed dependency lock, a fresh GitHub Actions `npm ci`, Bun 1.2.22,
tscircuit 0.0.2646, and CI bootstrap all passed. However, PR #16's conversion of
`SW_MX_HE_0deg_1u.kicad_mod` with `kicad-to-circuit-json` 0.0.117 reached
**STOP 1 - FOOTPRINT INTEGRITY**. It preserved the Hall SMD pads, plated
through-hole pad, duplicate pad-number semantics, two NPTH switch holes,
plated/non-plated distinction, mechanical alignment, and the observed Y-axis
inversion, but lost two copper-pour keepout zones. This rejects the import path;
it does not establish that a native tscircuit design is impossible. Native
stock-tscircuit feasibility therefore requires a separate technical gate.

## D-014 - Native tscircuit is the M1 electrical source

Status: accepted

Use native TypeScript / TSX through unmodified stock tscircuit to generate
Circuit JSON for the M1 four-key Hall evaluation board. The Issue #19 Human
Gate is **GO**: Checkpoints A, B, and C demonstrated the required Hall geometry,
source-level electrical connectivity, and two-layer manufacturing pipeline.
The KiCad design is retired as fallback/reference evidence (`EDA-000`), not an
authoritative source and not converter input.

This freezes the M1 electrical architecture; it does not approve placement,
routing, a manufacturing package, an order, or G1. The current evaluation and
production baselines are two copper layers and 1.2 mm thickness.

Reason: the native spike preserved the Hall geometry and keepouts, resolved
real source ports/nets/traces, and produced stock outputs without an importer,
Circuit JSON patch, fork, custom schema, or exporter.

## D-015 - Rev.M1 reusable Main + Evaluation Wing architecture

Status: accepted

Physical Rev.M1 is a new modular design, separate from the permanent frozen
four-key EDA qualification fixture. D-014 remains unchanged as historical native
tscircuit electrical authority for that fixture. C2 electrical graph parity is
accepted PASS; C3 geometry discrepancies remain valid historical evidence, not
resolved by this decision. Exact geometric convergence to the legacy golden is
no longer a JITX adoption criterion. Manufacturer evidence should inform the new
production design; no legacy geometry is corrected in EDA-002C4A (issue #41).

The reusable Main carries RP2040, USB, 3.3 V logic/core power, switched HALL_5V
generation, three RP2040 ADC channels, ADC dividers and filters, the Wing
connection interface, and M1 debug/bring-up facilities. Reuse this Main unchanged
in Rev.A, or with only explicitly approved corrections.

The Evaluation Wing carries Hall sensor positions, TMUX1208, the board-to-board
or cable connection to Main, and switch geometry for pitch/interference tests.
No board or exact connector is designed or selected in C4A.

First-choice Rev.A reuses the accepted Main with a Left 21-key Wing and a Right
21-key Wing, three TMUX1208 devices per Wing. Both Wings are generated from the
same project-owned design definition; separate manufacturing datasets are
allowed. A single reversible left/right PCBA is not required. Future geometry
must be project-owned or explicitly approved; its source approval remains a
later Human Gate. `hardware/layout/**` must not be consumed.

The logical Main/Wing interface includes HALL_5V, GND, MUX_A0/A1/A2, Wing/bank
enable, three analog MUX outputs for production-compatible Wings, and any
additional required control/reference signals identified at interface design.
ADC dividers/filters stay on Main. At D-015 acceptance, exact connector, pin
count/order, shielding, ground allocation and mechanical implementation were
TBD at G0B. D-017 now records the accepted interface and evaluation harness;
final Rev.A cable mechanics remain open.

Compare 17.0, 16.5 and 16.0 mm pitches experimentally for typing feel/mechanical
usability, neighboring-magnet Hall interference, signal range, repeatability,
and practical switch/keycap interference. 16.0 mm is interesting because it may
allow a 21-key Wing inside JLCPCB's low-cost 100 x 100 mm region. Fitting that
region is an optimization target, not a pitch requirement. Magnetic performance
and usability take priority over PCB cost.

Use the [Rev.M1 DFM policy](../hardware/rev-m1/dfm-policy.md): prefer Economic
PCBA where practical, two copper layers, 1.2 mm thickness and SMD on one side.
Prefer Basic, then Promotional Extended parts; minimize unnecessary distinct
Extended types without sacrificing performance. Main + Evaluation Wing within
100 x 100 mm is a cost experiment, with separate orders allowed. No panel is
designed here.

Main reuse is intended to reduce Rev.A risk by retaining the power, MCU, ADC
and analog conditioning path once physically validated, while scaling the sensor Wings. G0A selects an active
EDA through C4B pipeline proof and C4C GO/NO-GO; G0B freezes architecture,
interface and experiments before physical implementation. C4A does not adopt
JITX or create D-016. See [architecture](../hardware/rev-m1/architecture.md),
[interface](../hardware/rev-m1/main-wing-interface.md) and
[evaluation plan](../hardware/rev-m1/evaluation-plan.md).

## D-016 - JITX physical backend NO-GO; native tscircuit resumes as active Rev.M1 EDA candidate

Status: accepted

The [Product Owner decision on Issue #55](https://github.com/ihsinoky/he-piantor-42/issues/55#issuecomment-5991285003)
completes EDA-002C4C / G0A: **NO-GO — JITX physical backend** for Rev.M1 / Rev.A.
JITX is not selected as the active physical EDA backend under the qualified
versions and workflow. Native stock tscircuit resumes as the active forward EDA
candidate/path for physical Rev.M1, subject to G0B and later product,
ERC/DRC and manufacturing gates. This is a project-fit decision, not a claim
that JITX is generally incapable or that routing completion is impossible.

Primary reason: [C4B5's accepted BLOCKED evidence](../hardware/jitx/physical/EDA-002C4B5.md).
Source-level routing worked materially, reducing the historical 147 downstream
unconnected items substantially. The retained multilayer experiment still had
39 downstream unconnected items plus a dangling via. No supported public
headless global multilayer routing workflow was demonstrated in the pinned
JITX environment. The complete, reproducible AI/source-controlled physical-routing
workflow required by this project was therefore not demonstrated. Further
investment in global fanout, layer allocation, via placement, route ordering
and conflict avoidance would require substantial routing strategy/tooling or
interactive work; the PO judged that investment a poor fit for completing the
keyboard. These bounded results do not prove that an expert cannot route the
board or that other placements and strategies cannot succeed.

Accepted positive results remain valid: graph introspection, manufacturer
component modeling, electrical parity, source-controlled design representation,
headless build and verification, and the downstream KiCad/CAM path with known
limitations. Retain all JITX source, manufacturer models, qualification code and
C0-C4B5 evidence unchanged for reference or possible future reevaluation. Carry
forward useful manufacturer-model, DFM, architecture and validation knowledge.

USB NPTH DFM is **OPEN — PRE-ORDER DFM REVIEW REQUIRED**, a separate product
manufacturing risk and not a reason for JITX NO-GO. The generated 1.6 mm
overall-thickness metadata problem remains historical JITX downstream-path
evidence/limitation, not the primary NO-GO reason; that path requires an
independent 1.2 mm finished-thickness handoff.

D-014 remains valid historical authority for the permanent frozen M1 electrical
fixture and is not rewritten. D-015 remains valid and continues to define the
reusable Main + Evaluation Wing architecture. No historical C0-C4B5 verdict
is changed by this adoption decision.

**At D-016 acceptance, G0A was complete and G0B was next / not-ready.**
D-017 below now completes G0B; EDA-003B acceptance remains necessary before
full Rev.M1 implementation. This decision does not authorize physical Rev.M1
implementation. Physical Main/Wing remains unimplemented; at this decision,
G0B acceptance was still required. Native
tscircuit is the forward candidate/path, not an already implemented or
production-qualified physical Rev.M1 design.


## D-017 - Rev.M1 Main/Wing architecture and interface freeze

Status: accepted

The [Issue #57 PO GO](https://github.com/ihsinoky/he-piantor-42/issues/57#issuecomment-6010634587)
on 2026-10-06 accepts the [reviewed G0B record](../hardware/rev-m1/g0b-freeze-proposal.md).
**G0B is complete.** The frozen values are authoritative within this boundary;
implementation items explicitly left open remain open. D-014/D-015/D-016 and
historical qualification evidence remain valid.

### Connector and interface

JST GH 14-position: `BM14B-GHS-TBT(LF)(SN)` Main/Wing headers,
`GHR-14V-S` housings, `SSHL-002T-P0.2` contacts. The exact accepted pin allocation
is in [G0B section 3](../hardware/rev-m1/g0b-freeze-proposal.md#3-accepted-exact-14-pin-interface):
`HALL_5V`, six physical GND/return contacts on common `GND`, `MUX_A0`, `MUX_A1`,
`MUX_A2`, `WING_EN`, `MUX_OUT_A`, `MUX_OUT_B`, `MUX_OUT_C`.

Switched `HALL_5V` remains default-off. Each `WING_EN` requires its own explicit
external Main-side hardware pull-down; firmware/internal pulls are insufficient.
The exact resistor value remains implementation work. The evaluation harness
is nominal 100 mm, 14 conductors, wired 1:1.

### Evaluation and current planning basis

Use three pitch-specific Evaluation Wings: **17.0 / 16.5 / 16.0 mm**. Preserve
production-equivalent/full-load electrical coverage, three TMUX1208 / three ADC
path coverage and the 21-sensor full-load/electrical-load path. The reviewed
[G0B coverage, test-access and measurement framework](../hardware/rev-m1/g0b-freeze-proposal.md#6-production-equivalent-mux-and-bank-evidence)
is accepted. Production pitch is not selected.

DRV5055 at 5 V: **3 mA typical / 5 mA maximum**. Planning estimates are
approximately **127 mA per 21-key Wing / 254 mA for 42 sensors / two Wings**.
These are planning estimates, not final USB/system power qualification; MCU,
other loads and startup/inrush remain subject to later verification. The final
Hall sensor is not selected by this planning basis.

### PCB / DFM

Two copper layers, 1.2 mm thickness, SMD one side preferred, and JLCPCB Economic
PCBA preferred where practical. **100 x 100 mm is optimization only.**

**USB NPTH — OPEN — PRE-ORDER DFM REVIEW REQUIRED**

No manufacturing exception or release is approved.

### EDA authority and sequence

Native stock tscircuit remains active forward physical EDA; native TSX remains
authoritative. [EDA-003A](tscircuit-kicad-importer-requalification.md) / merged
PR #59 is accepted as **UPSTREAM_FIX_CANDIDATE**: both copper-pour keepouts were
silently lost, warnings did not report the material loss, and rounded-pad
corner radius was incorrect. Current KiCad footprint importer reuse is **NOT
approved**. KiCad assets remain reference / secondary evidence. Future importer
reuse requires separately accepted fidelity evidence after fixes.

**G0B accepted -> EDA-003B representative stock-tscircuit physical/routing proof
-> if accepted, full Rev.M1 implementation.** EVT-002's G0B prerequisite is
satisfied; full implementation is not yet active. No schematic/PCB/manufacturing
package completion is claimed.

### Remaining open

Production key pitch; final Hall sensor choice; final Rev.A cable mechanics/length;
exact `WING_EN` pull-down resistor; final placement; PCB routing; representative
stock-tscircuit routing capability; USB NPTH manufacturing disposition; final
USB/system power budget; manufacturing release. Planning values do not become
final production requirements.


## D-018 - Bounded alternate physical backend qualification planning

Status: accepted PO planning decision; qualification execution not authorized

The [Issue #71 PO Human Gate comment](https://github.com/ihsinoky/he-piantor-42/issues/71#issuecomment-6046244229)
on 2026-10-07 approves decision recording, documentation/Dashboard alignment,
a bounded qualification plan and a draft of the next execution Issue body.
It approves ending additional product-track exploration of the internal
tscircuit router evaluated in EDA-003F. The accepted EDA-003F result remains
**INTERVENTION_UNSAFE_REGRESSION**, terminal **K1**: zero required unrouted,
but two wrong-net copper components. Neither reduced diagnostic counts nor
signature disappearance establishes a safe improvement.

Retention of the tscircuit frontend is still being evaluated; it has not been
abandoned. **Candidate B is the first qualification candidate, not an adopted
backend**: native TSX -> genuinely unrouted Circuit JSON -> KiCad -> DSN ->
local headless Freerouting -> SES -> KiCad verification/manufacturing.
Prefer existing converters and public APIs. No private API, permanent fork,
large custom interchange implementation or new manufacturing exporter is
approved. A and C remain comparison candidates, with no automatic fallback.

The first Main evaluation has a **two-workday engineering-effort cap**, including
preparation, interchange and reconciliation. Permit one initial Main routing
run and one fresh confirmation only if the first passes. Preserve components,
connectivity, placement, outline, two copper layers, 1.2 mm thickness and the
unchanged **0.20 mm material-clearance requirement**. Stop on material transfer
loss, headless failure, shorts, incomplete routing, targeted physical violations,
non-reproducibility, excessive adapter work or exceeded budget. Main must pass
before Wing/export work advances. Candidate/placement changes, retries/tuning
or exceptions require a new PO decision.

Issue #71 authorizes **documentation and planning only**. Actual qualification
requires a separate **PO-created execution Issue** and a subsequent **PO
instruction after its number is confirmed**. Full Rev.M1 implementation,
backend adoption and ordering remain blocked. CI success cannot pass these
gates. Existing G0A/G0B decisions remain completed; no Human Gate is reopened
or newly passed by Codex.

D-014 remains historical electrical authority for the permanent frozen fixture.
D-015/D-017 Main/Wing architecture and interface, D-016 JITX physical backend
NO-GO, all historical verdicts and design/evidence bytes remain unchanged.
Production **tscircuit 0.0.2646** remains pinned. **USB NPTH OPEN — PRE-ORDER
DFM REVIEW REQUIRED** remains a product risk with no manufacturing exception.
Production pitch is unselected; final Hall choice, Rev.A cable mechanics,
exact WING_EN pull-down, final placement/routing and USB/system power remain
open. This forward planning decision supersedes the old future EDA-003B
sequence without rewriting D-016/D-017's historical authority.

See the [bounded qualification plan](alternate-physical-backend-qualification-plan.md)
and [execution Issue body draft](alternate-physical-backend-main-qualification-issue-draft.md).
