# Issue #294 Pilot A — plan

## Goal
Stand up the semantic review layer's records (procedure + ledger) and run it over the
existing Main Rev.10 two-posture audit findings (Issues #275 / #278 evidence).

## Sources of truth
- Design: ~/workspace/goals/he-piantor-42-keyboard-pmo/files/semantic-review-layer-design-2026-11-19.md
  (record format §3, semantic functions §4, invariants §6)
- Issue #294 body: ledger = docs/review-ledger.md, procedure = docs/review-procedure.md,
  promotion into docs/findings.md when a finding hardens.
- Interpretation basis: docs/decisions.md D-046, D-047, D-051.
- Format conventions: docs/findings.md.
- Evidence: Issue #275 / #278 runtime artifacts (locate on filesystem first).
  ONLY measured values recorded in those artifacts may be used; anything else = MISSING.

## Steps
1. Read Issue #294 body; read decisions.md (D-046/D-047/D-051) and findings.md conventions.
2. Locate #275/#278 audit artifacts; inventory the raw observations of the Rev.10
   two-posture audit (fitted audit, pocket A, A2 channel, extrema clearance 0.314mm,
   EZmate serviceability, FFC board-lift).
3. Write docs/review-procedure.md (kernel run -> structured records -> semantic
   classification -> report with visible suppression accounting). Commit.
4. Write docs/review-ledger.md: (a) problem-class register seeded with the 5 classes
   (manufacturing-margin, interference, clearance-shortfall, assembly-escape-shortfall,
   symmetry-break) with definitions + seed examples; (b) findings register: every distinct
   Rev.10 audit finding in §3 record format with state + semantic classification + cited
   basis. measured=MISSING -> 'unclassified - needs verification'. Commit.
5. Write .issue294-runtime/pilot-a-report.md: NEW list, SAME-CLASS groupings,
   SUPPRESSION breakdown (accepted by D-xxx / in-progress under Issue /
   resolved-confirmed), needs-PO-judgment items as choices. Reconciliation computed
   from the register: raw = new + suppressed + duplicates-merged. Commit.
6. Spot-check: re-read artifacts after each register batch; verify arithmetic from register.

## Invariants
- No invented numbers. LLM never generates/corrects measured values.
- No silent suppression: every suppressed item stays in the ledger with its reason.
- Ledger is a record, not an instruction (台帳ガード).
