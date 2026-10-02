# Project status

This document is the authoritative record of the project's high-level progress.
Detailed implementation work is tracked by GitHub Issues rather than duplicated
here.

## Current milestone

**M1 — Magnetic approach / evaluation board** (`current`)

- **Deliverable:** four-key Hall-sensor evaluation board, measurement firmware,
  and measured-results report.
- **Exit criteria:** ERC and DRC pass; physical measurements establish sensor
  range, noise, scan speed, power consumption, and the selected magnetic
  approach.

## Roadmap

| Milestone | Status | Deliverable | Exit criteria |
| --- | --- | --- | --- |
| M0 — Design policy / basic geometry | `done` | 42-key requirements, 17 mm layout, and acquisition-method design policy | Principal requirements, key-center coordinates, and evaluation policy are documented. |
| M1 — Magnetic approach / evaluation board | `current` | Four-key Hall-sensor evaluation board, measurement firmware, and measured-results report | ERC and DRC pass; physical measurements establish range, noise, scan speed, power consumption, and the magnetic approach. |
| M2 — 42-key Rev.A | `next` | Manufacturable 42-key Rev.A PCB and baseline Vial/Hall firmware | Main-board ERC/DRC, manufacturability checks, and firmware build pass. |
| M3 — Integration / enclosure / test | `todo` | Enclosure, integrated unit, and assembly, calibration, and test procedures | Physical operation, all-key calibration, USB/Vial behavior, and enclosure fit pass testing. |
| M4 — Final release | `todo` | Reproducible v1.0 manufacturing, firmware, and enclosure package | Final artifacts are fixed and the Product Owner approves the completed release. |

## Human Gates

| Gate | Current status | Check | Trigger | Unlock condition |
| --- | --- | --- | --- | --- |
| G1 — Evaluation circuit review | `not-ready` | Circuit/ERC, BOM, and measurement plan | Evaluation-PCB manufacturing data is complete. | Evaluation-board ordering may proceed. |
| G2 — Magnetic approach decision | `not-ready` | Range, noise, scan speed, power, and interference | Evaluation-board measurements are complete. | The 42-key circuit may be fixed. |
| G3 — Rev.A pre-order review | `not-ready` | Main-PCB DRC, BOM, Gerbers, and cost | The 42-key manufacturing package is complete. | Rev.A PCBA ordering may proceed. |
| G4 — Physical operation review | `not-ready` | Typing, calibration, Vial, USB, and enclosure fit | Integrated-unit bring-up is complete. | The final design may be fixed. |
| G5 — Final approval | `not-ready` | All v1.0 artifacts and procedures | Acceptance testing passes. | v1.0 may be released. |

## Workstreams

| Workstream | Current high-level state |
| --- | --- |
| Hardware | EDA-001 and EVT-001 are done. PR #27's native tscircuit four-key electrical model is the frozen M1 golden reference. EDA-000 is retired fallback/reference. EVT-002 and final placement, routing, and DRC have not started and are gated on the JITX EDA evaluation. |
| Firmware | M0 requirements are done; M1 measurement firmware is in progress. Hall/Vial integration and later firmware remain unstarted. |
| Enclosure / Mechanical | M0 geometry constraints are done; M1 is waiting for PCB constraints. Later enclosure integration and manufacturing artifacts remain unstarted. |
| Verification / Test | M0 planning is done; M1 magnetic and power measurement is waiting for the evaluation hardware. Rev.A bring-up and later testing remain unstarted. |

## Current and next work

The project is in M1. Issue #19's Human Gate returned GO for native stock
tscircuit, so EDA-001 is done and EDA-000 is retired fallback/reference. PR #27
completed EVT-001 and froze `hardware/tscircuit/src/evaluation/m1-four-key.tsx`
and its Checkpoint A/B/C evidence as the M1 electrical golden reference. D-014
remains the accepted historical decision that made native tscircuit the M1
electrical source.

EVT-002 must not begin until the Product Owner resolves the JITX-versus-frozen-
baseline EDA evaluation gate. Final two-layer placement, routing, DRC,
manufacturing preparation, and G1 readiness have not started and remain
follow-up work. The evaluation does not replace or delete the frozen tscircuit
baseline.

The previous spike established reproducibility with a committed dependency
lock, fresh GitHub Actions `npm ci`, Bun 1.2.22, tscircuit 0.0.2646, and
non-interactive CI bootstrap. Its KiCad footprint-import path stopped at
footprint integrity: conversion of `SW_MX_HE_0deg_1u.kicad_mod` using
`kicad-to-circuit-json` 0.0.117 preserved Hall SMD pads, the plated through-hole
pad, duplicate pad-number semantics, two NPTH switch holes, plated/non-plated
distinction, mechanical alignment, and an observed Y inversion, but lost two
copper-pour keepout zones. Therefore KiCad import is not the authoritative
migration path. This result does not rule out native tscircuit design.

Existing KiCad work remains unchanged as fallback, reference, and prior-design
evidence, but is not the active EDA source. Each detailed increment is
defined and accepted through its own GitHub Issue.

## Dashboard synchronization

`docs/project-status.md` is authoritative for high-level project status.
`task/data/project-status.js` is a manually synchronized Dashboard read-model
copy. If they conflict, this document is correct. Synchronization is reviewed in
the same pull request as a status change; there is currently no generator or
automatic synchronization.
