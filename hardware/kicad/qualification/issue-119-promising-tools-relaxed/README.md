# Issue #119 qualification evidence

[Report](../../../../docs/issue-119-promising-tools-relaxed-conditions.md). Input equivalence, matching-condition smoke, then four fixed single Main invocations. No tool source modifications, result-driven setting changes, or Main reruns.

`evidence/instructions.md` preserves the complete instructions. `start.json` pins the time box and source branch commit. `source-117-provenance.json` records direct extraction from the pending #117 branch. `equivalence-gate.json`, `smoke-gate.json`, and `main-freeze.json` establish gate order. `assessment.json` reports independent measurements; raw router logs and KiCad DRC remain in `processes/`, `runs/`, and `inspection/`. Scripts in `source-117/` are archived references; the top-level scripts are this experiment's executable harness.

Existing copper remains 0.20mm; new width/clearance rules are 0.127mm and all standard vias remain 0.60/0.30mm. A residual connection makes all four qualification indicators null even when an individual raw DRC category is zero.
