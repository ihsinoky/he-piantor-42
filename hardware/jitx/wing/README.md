# Evaluation Wing inputs (Issue #127)

Read [the report](../../../docs/issue-127-wing-design.md) and
[placement review](../../../docs/issue-127-wing-parts-placement-review.md) first.

From `hardware/jitx`, run `python -m wing.export` to regenerate all six variants,
or `python -m wing.export --check` to check committed outputs. The exporter only
needs Python 3.12's standard library; native JITX assemblies use the locked environment.

`definition.py` is the source. `generated/*/definition.json` records mm outlines,
mounting holes/keepouts, component placements, physical-pin connectivity, explicit
NCs and each sensor's MUX/address/role. `nets.csv` includes mechanical `MP` NCs.
`PCB_PAD_1.2MM` in the BOM is PCB copper, not a purchased test-point component.
`placement.svg` is a review drawing with assumed pitch cells, not switch CAD.

`pitch9` is the isolated 3x3 pitch experiment. `load21` keeps the same 3x3 field
and adds 12 Hall-only electrical loads. `representative21` is a new 5x4+1 compact
21-switch geometry proposal. These roles must not be silently interchanged.

Native classes live in `he_piantor_42_jitx.evaluation_wing`: `Pitch16`, `Pitch17`,
`Representative16`, `Representative17`, `Load16`, `Load17`. For another validated
pitch in [16,17] mm, declare `make_wing_design(name, pitch, kind)` before JITX
instantiation. Matrix/load/representative placements share the same net definition.

The native JITX board is a rectangle. Before routing, consumers must implement
JSON mounting NPTH and keepouts in their target PCB, review the fixture/switch
mechanics, and preserve the exact pin map including six separate GND conductors.
Two-layer rules are provisional scaffolding, not an approved fabrication policy.
No routing, manufacturing package, final ergonomic layout or measured acceptance
is included.
