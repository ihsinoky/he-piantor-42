# JITX code review — C4B3 observer scripts

Reviewer: jitx-code-review, same-model self-critique. Scope:
`physical/measure_c4b3.py`, `physical/requalify_c4b3.py`.
Rule sources read: JITX base skill Don'ts, architectural-patterns,
code-review checklist, substrate-modeler skill.

CRITICAL: 0. No reflection-based scene navigation, private JITX calls,
parallel design construction, topology mutation or generated-file patching.
The measurement uses public TestCase/visit and existing landpattern objects.
JSON dictionaries are serialized observations, not a model driving JITX.

WARNING: 1 found, resolved. `requalify_c4b3.py:142`: DRC fallback could classify
more than missing-connection pair/order changes. Checklist rule:
"a claim made without backing evidence" (`compliance-theater`).
Fix at lines 143–150 requires all report content outside date and unconnected
items to match exactly, otherwise fails. The historical reconciliation also
checks per-net source islands independently. Reconciliation and comparison
were rerun on the retained final pair; the tightened fallback did not need to
activate. Final analysis hash is recorded separately in determinism.json;
pipeline.json retains the actual generation-script hash.

NOTE: 2 retained.

- `requalify_c4b3.py:159`: literal G01 block/aperture is specific to the frozen
  qualification fixture (`example-shaped-rule`), not a general Gerber parser.
  It fails on different surrounding content and does not alter CAM files.
- `measure_c4b3.py:43`: axis-aligned rectangle/circle formula is restricted to
  this accepted manufacturer's lands, not arbitrary pad geometry. Nominal
  measurement does not supply manufacturing-yield or finished-gap evidence.

Ownership review: rebinding OUTPUT/EVIDENCE at `requalify_c4b3.py:39` affects
only project-owned scripts. JITX owns all design/runtime invariants; the code
queries public APIs and does not rebind framework objects or internals.

Final unresolved CRITICAL: 0; unresolved WARNING: 0; retained NOTE: 2.
Manufacturing acceptance remains BLOCKED as reported.
