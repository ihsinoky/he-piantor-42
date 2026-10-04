# Project status

This document is the authoritative record of the project's high-level progress.
Detailed implementation work is tracked by GitHub Issues rather than duplicated
here.

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
| G0A — JITX Backend Adoption | `ready-for-decision` | C0-C3 accepted evidence and C4B/C4B2/C4B3 physical/manufacturing results | C4B3 BLOCKED: supported job-free thickness handoff identified; USB margin unresolved; routing remains separate. | C4C GO / NO-GO selects active EDA backend for physical Rev.M1 implementation. |
| G0B — Rev.M1 Architecture / Interface Freeze | `not-ready` | Reusable Main / Evaluation Wing architecture, logical interface, exact connector selection/pinout, experiment design, representative interconnect, pitch-test Wing structure, Rev.A reuse assumptions, DFM constraints and project-owned/approved geometry source | Architecture/interface and experiment review package is complete. | Rev.M1 schematic/PCB implementation may proceed to manufacturing-package completion. |
| G1 — Rev.M1 Main + Evaluation Wing pre-order review | `not-ready` | Actual Main/Wing circuit/ERC, DRC, BOM, manufacturing outputs and measurement plan | Complete manufacturing package exists after G0A/G0B. | Rev.M1 Main + Evaluation Wing ordering may proceed. |
| G2 — Post-EVT-002 magnetic / pitch / analog-path decision | `not-ready` | Measured range, noise, scan speed, power, interference, actual interconnect path and pitch usability | Physical evaluation measurements and report are complete. | Select among 17.0 / 16.5 / 16.0 mm and production magnetic architecture; the Rev.A circuit may be fixed. |
| G3 — Rev.A pre-order review | `not-ready` | Main/Left/Right Wing DRC, BOM, Gerbers, drill/placement outputs and cost | The 42-key manufacturing package is complete. | Rev.A PCBA ordering may proceed. |
| G4 — Physical operation review | `not-ready` | Typing, calibration, Vial, USB, and enclosure fit | Integrated-unit bring-up is complete. | The final design may be fixed. |
| G5 — Final approval | `not-ready` | All v1.0 artifacts and procedures | Acceptance testing passes. | v1.0 may be released. |

## Workstreams

| Workstream | Current high-level state |
| --- | --- |
| Hardware | EDA-001 / EVT-001 historical four-key fixture is frozen under unchanged D-014. C0/C1 accepted; C2 accepted electrical PASS; C3 merged PR #40 retains valid historical geometry discrepancies. C4A accepted / merged PR #42 under D-015. C4B issue #43 investigation is BLOCKED: partial copper/ODB/CSV demonstrated; full routing/DRC and qualified Gerber/drill handoff remain open. C4B2 issue #45 is also BLOCKED: downstream DRC/CAM executes twice, but source hole clearances and exported thickness prevent manufacturing qualification. C4B3 issue #47 is BLOCKED: thickness has a supported job-free handoff limitation; near-limit USB margin remains unresolved. C4C / G0A remains Human Gate, ready-for-decision; adoption remains undecided. New physical Rev.M1 Main/Wing implementation and EVT-002 remain unstarted behind G0A/G0B. |
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

**EDA-002C4B investigation: BLOCKED** (issue #43). The disposable four-key
qualification wrapper builds with explicit 68-component placement, partial
copper on two layers/two vias, ODB++ and public BOM/PnP review exports. The two
fresh generations repeat captured geometry and CSVs; ODB order/IDs vary.
Full routing, complete DRC and a qualified Gerber/Excellon JLCPCB handoff remain
unproven. C2 electrical parity remains PASS. See the
[C4B evidence](../hardware/jitx/physical/EDA-002C4B.md).

**EDA-002C4B2 downstream CAM: BLOCKED** (issue #45; pending PMO/PO review).
The unchanged fixture generates JSON DRC, nine Gerber layers, PTH/NPTH Excellon
and 68-row PnP through KiCad 9.0.9 twice from fresh state. Its 147 missing
connections reconcile with C4B's intentional partial routing. Four USB source
copper-to-NPTH clearance conflicts and exported 1.6 mm thickness contradicting
the 1.2 mm source stack block manufacturing qualification. No manufacturing
geometry/drill/assembly-coordinate difference was found between runs; all raw
differences are retained. Historical evidence, versions and full routing remain
unchanged. See [C4B2 evidence](../hardware/jitx/physical/EDA-002C4B2.md).

**EDA-002C4B3 manufacturing disposition: BLOCKED** (issue #47; PMO/PO review pending).
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

**EDA-002C4C / G0A is next / Human Gate, ready-for-decision** on this blocked
result. It must decide whether further supported-workflow investment is
warranted or a supported fallback is preferable. No GO/NO-GO decision or D-016
is made here. No board is ordered. This geometry is disposable backend
qualification infrastructure; physical Rev.M1 is unimplemented.

G0B must freeze the architecture/interface, exact connector/pinout and
representative experiments before implementation. Physical Main/Wing,
connector selection, schematic, placement, routing, DRC and manufacturing are
not implemented here. `hardware/layout/**` is not consumed; future Wing
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
classification. JITX remains a challenger qualified against the historically authoritative
frozen tscircuit fixture; C4B is BLOCKED; C4C adoption and G0B product freeze remain ahead.

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
