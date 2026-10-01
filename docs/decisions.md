# Design Decisions

This file records decisions that materially affect hardware, firmware, manufacturing, or enclosure design.

## D-001 - One-piece geometry

Status: provisional

Interpret "120-degree reverse-V" as an internal angle of 120 degrees between left and right key fields, with the left field at +30 degrees and right field at -30 degrees in the project coordinate convention (+x right, +y down).

Reason: this is the simplest consistent geometric interpretation and is easy to review visually once the Piantor key centers are transformed.

## D-002 - Key pitch

Status: provisional baseline

Use 17.0 mm pitch rather than 16.5 mm.

Reason: 16.5 mm square narrow MX-stem keycaps exist. At 17.0 mm center spacing this leaves a nominal 0.5 mm cap-to-cap gap. A 16.5 mm pitch would leave no nominal gap.

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

Status: accepted

Do not release the 42-key PCB until a four-key Hall evaluation board has measured:
- switch travel curve and polarity,
- usable ADC span and clipping margin,
- noise and repeatability,
- mux settling time,
- adjacent-key magnetic coupling,
- Hall-rail current and turn-on behavior,
- short-term thermal drift.

Reason: Hall switch behavior depends on the switch magnet, Hall sensor, PCB thickness, physical alignment, analog path and firmware timing as one system. Nominal component specifications alone are not sufficient for the production PCB.

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
