## Closes

Closes #

## Summary

## Scope

## Out of scope

## Acceptance Criteria

- [ ]

## Documentation

## Verification / CI

<!-- Apply docs/development-workflow.md#verification-evidence and #pcb-to-case-handoff.
Implementer / Codex records inputs, method, result and evidence below; PMO reviews
read-only; PO decides acceptance. Mark each inapplicable check with a reason.
Failed or missing checks hold acceptance / dependent stages; do not relax scope
or criteria without PO direction. -->

- [ ] Independent acceptance (F-002): source commit / input hashes, original rules,
  saved outputs, tool versions / effective settings, independent method and
  evidence; include project-setting differences. Exit code and self-reported
  unrouted / violation counts do not establish pass; null is not zero.
- [ ] Retained-artifact comparison (F-008): for local changes / repairs, name the
  frozen baseline, permitted scope and retained wiring / data set; link before /
  after comparison and independent checks. Missing comparison or unexpected
  loss / change holds acceptance even if connectivity / DRC pass.
- [ ] Full via-pad audit (F-004): for PCBs with vias, link saved PCB hash, criterion,
  full via / copper-pad coverage and results. Measure from annulus outer edge;
  same-net pairs are included. Incomplete coverage or any clearance failure holds
  acceptance; overlap-only / drill-edge checks are insufficient.
- [ ] PCB-to-case handoff (F-005): for PCB input updates, link source / received
  file-set and hash comparisons, mounting-point set / transform and case hole /
  boss checks for every variant. Mismatch or missing evidence holds handoff.

## Human Gate

<!-- State the decision required from the Product Owner. Green CI does not merge the PR. -->

## Dashboard impact

<!-- Note read-model changes, or state "None". The Dashboard is not a source of truth. -->

## Additional issues discovered

<!-- Record out-of-scope findings and suggested follow-up Issues. Do not fix them here. -->
