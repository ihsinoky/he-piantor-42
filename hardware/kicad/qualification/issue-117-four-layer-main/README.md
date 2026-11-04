# Issue #117 — four-layer Main and Wing outlook

Report: [Stage 0 stop and analytical Wing outlook](../../../../docs/issue-117-four-layer-main-and-wing-outlook.md).

The SHA256-fixed smoke fixture has only net `N`, while the instruction requires
an unchanged net inventory and a filled net-`GND` zone. This conflict prevents
Stage 0 acceptance. Neither router was run: smoke 0 / Main 0 for both cells.
All four independent acceptance metrics remain null. This is not a routing
failure or a verdict on four-layer feasibility.

Main four-layer native generation, filled GND plane, native semantic identity,
DSN regeneration/readback and parser/configuration-only readbacks are retained.
The smoke four-layer file is an explicitly incomplete preparation artifact,
without a fabricated GND net/zone. `preparation-attempt-01` retains an initial
native serialization mismatch; it was corrected before any routing.

Wing evidence is analytical only, from the allowlisted architecture/interface
documents; no `hardware/layout/**` input was consumed. See `evidence/assessment.json`,
`equivalence-gate.json`, `wing-outlook.json`, and the process records.
