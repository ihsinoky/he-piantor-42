# Issue #163 — plan C adopted, mechanical gate unestablished

**Stopped before PCB implementation. The full Issue is not complete.**
The [report](../../../../docs/issue-163-main-dual-wing-plan-c.md) distinguishes
the adopted outline/interface from unqualified mechanics and electronics.
No design writer, router, refill, CAM export or quotation submission ran.

| Evidence | Meaning |
| --- | --- |
| instructions.md, issue.json, pr162-input.json, start.json | Full authority, imported head, branch and conservative four-hour deadline |
| import-proof.json | All27 PR162 changed files compared bytewise; D024 unchanged, D025 appended |
| input-hashes.json, native-readback.json | #155 original PCB/project identity and native read-only crosscheck |
| sources.json | Primary product sources and access limits; full GH handling PDF not retrieved |
| analyze.py, mechanical.json, beam-sensitivity.csv | Concrete trial screw/tool/operation and72 explicitly hypothetical strip-beam cases; NOT physical validation or a bound on a point-supported plate |
| draw.py, mechanical-review.svg | Review projections generated from JSON, NOT a PCB/3D CAD model |
| ideal-main-dc.csv, power-preflight.json |128 recomputed scenarios with zero Main resistance, NOT routed resistance extraction or system voltage qualification |
| protected-start.json.gz |10,754 existing non-runtime files protected after authorized import; decisions checked separately against PR162 |
| run-checks.py, verification.json, processes/ | Reproducible provenance/preservation/model checks; all new-board qualification metrics null |
| draft-pr-body.md, publication.json | Prepared review text and actual publication outcome |
| manifest.json | SHA256 of added evidence files, excluding the manifest itself |

From the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 hardware/kicad/qualification/issue-163-main-dual-wing-plan-c/run-checks.py
```

The read-only native check uses existing KiCad bindings in `.issue129-runtime/`
and the historical #160 script. It does not install or alter those dependencies.
All temporary/XDG files use `.issue163-runtime/`. The runner uses its writable
Git metadata there; on a fresh checkout substitute that checkout's normal Git
directory. Re-running these checks refreshes only this issue's derived evidence;
refresh the manifest afterward. Historical #160 verification remains historical
and is not rewritten to make its pre-D025 assertions pass.

The mechanical gate has not established actual latch/probe swept geometry,
14-way insertion/unlocked extraction force, upward and downward local restraint,
laminate stiffness, fastening preload or accepted solder strain. Trial choices
are not newly approved product requirements. The 4.75/5V and temperature/load
DC sensitivities are not guaranteed USB/system operating conditions.

This result invokes the issue's stop condition without claiming plan C physically
impossible. New PCB, schematic, manufacturing data, POFV classification and PCBA
quotation remain **unimplemented/unavailable**, not zero-cost or qualified.
No order, charge or merge was performed.
