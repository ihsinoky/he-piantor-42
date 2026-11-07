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
and adds 12 Hall-only electrical loads. `representative21` uses the attributed Piantor left-half 3x6+3 snapshot in
`piantor_left21.json`, preserving column stagger and the three thumb centers.
The former 5x4+1 candidate is superseded. The current 16/17 mm boards measure
110x100 / 116.5x104.75 mm; both fail the 100x100 requirement and need a PO decision.
The native 100 mm fabrication constraints remain in place; these oversized inputs
are for review, pending that decision. These roles must not be silently interchanged.

Native classes live in `he_piantor_42_jitx.evaluation_wing`: `Pitch16`, `Pitch17`,
`Representative16`, `Representative17`, `Load16`, `Load17`. For another validated
pitch in [16,17] mm, declare `make_wing_design(name, pitch, kind)` before JITX
instantiation. Matrix/load/representative placements share the same net definition.

The native JITX board is a rectangle. Before routing, consumers must implement
JSON mounting NPTH and keepouts in their target PCB, review the fixture/switch
mechanics, and preserve the exact pin map including six separate GND conductors.
Two-layer rules are provisional scaffolding, not an approved fabrication policy.
For the representative21 Wing, the two-layer baseline (trace width signal 0.10 mm / power HALL_5V and GND
0.30 mm, 0.10 mm clearance) is now adopted by
[D-021](../../../docs/decisions.md#d-021---revm1-wing-two-layer-and-010-mm-design-rule-baseline)
as amended on 2026-11-05 (Issue #143);
this generated data is unchanged and the README remains no manufacturing release.
No routing, manufacturing package, final ergonomic layout or measured acceptance
is included.

Wing Rev.2 (Issue #194 Phase B) has a separate generator:
`python -m wing.rev2` or `python -m wing.rev2 --check`, run from `hardware/jitx`.
It consumes the PMO-approved four Phase A layouts, calibrates the Hall active
point and emits separate left/right definitions at both pitches. The native
PCB builder, routing evidence, independent qualification and Standard-PCBA
panel data are in [issue-194-wing-rev2](../../kicad/qualification/issue-194-wing-rev2/README.md).
The legacy six-variant exporter continues to describe the older evaluation boards.
