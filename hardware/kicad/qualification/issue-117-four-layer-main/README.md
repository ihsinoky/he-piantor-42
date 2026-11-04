# Issue #117 — four-layer Main and Wing outlook

Current report: [Main results and Wing outlook](../../../../docs/issue-117-four-layer-main-and-wing-outlook.md).

The latest amendment-01 results are in `evidence/amendment-01/assessment.json`,
`smoke-gate.json`, `verification.json`, and `submission.json`. Both smoke gates
passed. Each Main router was run exactly once, without changed settings or reruns.
See the report and independent refilled KiCad DRC for the measured open connections.

The original `evidence/assessment.json`, `equivalence-gate.json`, `verification.json`
and preparation scripts retain the prior run 2 Stage 0 stop as historical evidence.
They are superseded by amendment-01, whose instruction assigns the smoke plane to
its existing sole net N. The Main GND-plane input is reused byte-for-byte.

Both initial thermal smoke outputs and the corrected solid-zone smoke outputs
are preserved. The latter passed all four independent metrics. Main inputs were
never rebuilt. The previous report is `amendment-01/report-before-amendment.md`.

Wing analysis is retained verbatim from run 2; no Wing routing or new investigation
was performed, and no `hardware/layout/**` inputs were consumed for that analysis.
