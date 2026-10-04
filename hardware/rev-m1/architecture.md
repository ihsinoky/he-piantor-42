# Physical Rev.M1 architecture

Requirements only — EDA-002C4A, issue #41. No schematic, footprint, PCB,
routing, panel or manufacturing output is implemented here.

[D-015](../../docs/decisions.md#d-015---revm1-reusable-main--evaluation-wing-architecture)
separates physical Rev.M1 from the permanent four-key qualification fixture.
The frozen native tscircuit source/verifier, C2 parity contract/evidence, C3
geometry report and historical sensor-test inputs remain unchanged. D-014 is
historical electrical authority for the fixture, not an adoption decision for
the new product. C2 remains accepted PASS: 68 components, 200 normalized
endpoints, 43 named nets, 185 endpoint/net edges, 4 direct links, 7 intentional
NCs. C3 remains valid discrepancy/modeling/footprint-policy evidence; exact
geometry convergence to the legacy reference is no longer required for adoption.
Those questions have changed relevance, not all been resolved.

```text
USB -> Reusable Main: RP2040 + 3V3 + switched HALL_5V + debug
                    | address / enable / power / ground
                    v
             Evaluation Wing(s): Hall positions -> TMUX1208
                    | analog outputs through representative interconnect
                    v
             Main: three divider/filter paths -> three ADC channels

Rev.A: accepted Main <-> Left 21-key Wing (3 TMUX1208)
                     <-> Right 21-key Wing (3 TMUX1208)
```

Main owns USB, MCU/core and logic power, switched Hall power generation,
three ADC channels and their dividers/filters, Wing interface and bring-up
facilities. Evaluation Wing owns Hall positions, TMUX1208, its connection to
Main and physical switch geometry for pitch and magnetic experiments.

First-choice Rev.A reuses Main unchanged or with explicitly approved
corrections. Left/Right Wings share a project-owned generation definition;
separate designs and manufacturing outputs are allowed, with no reversible
PCBA requirement. Keeping the validated MCU/power/ADC/filter boundary reduces
Rev.A risk, but interconnect loading and production bank behavior must be
represented in M1 measurements before reuse is accepted.

Fixed by D-015: modular responsibilities, Main-side ADC conditioning, Main
reuse intent, three-TMUX/21-key-per-Wing Rev.A candidate, and evaluation of
17.0 / 16.5 / 16.0 mm. Production pitch is not fixed. Connector MPN, pinout,
shielding/ground allocation, mechanics, test-Wing structure, additional
control/reference signals and future Wing geometry source approval remain
TBD at G0B/later Human Gates. Do not consume `hardware/layout/**`.

[G0A/G0B](../../docs/project-status.md#human-gates) are not-ready. JITX adoption
requires C4B proof then C4C Human Gate; C4A does not select an active backend.
See [logical interface](main-wing-interface.md), [experiments](evaluation-plan.md)
and [DFM policy](dfm-policy.md). No physical hardware is claimed implemented.
