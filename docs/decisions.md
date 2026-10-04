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
ADC dividers/filters stay on Main. Exact connector, pin count/order, shielding,
ground allocation and mechanical implementation remain TBD at G0B.

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
