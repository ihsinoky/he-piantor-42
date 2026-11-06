# Finding Records

Empirical findings for he-piantor-42, per [D-031](decisions.md#d-031---knowledge-recording-adr-finding-records-and-promotion).
A Finding records what was tried, under what conditions, and where the
result is valid. Judgments and adoptions live in decisions.md, not here.
Raw logs live in the linked Issues/PRs and are not duplicated here.

## Entry template

### F-NNN — <title>

- **Conclusion:** <one or two sentences> (confidence: <low/medium/high>;
  trials: <n>)
- **Conditions tried:** <tool and exact version, target commit, parameter
  ranges, dates>
- **Failed attempts:** <one line each; "none" if none>
- **Validity scope:** <untested ranges; assumptions; invalidation
  conditions; re-verification triggers>
- **Evidence:** <links to Issues/PRs/logs>
- **Promoted to:** <process definition or skill, once promoted; empty
  until then>

## Entries

### F-001 — No Basic-classified 27Ω 0603 resistor exists in the JLCPCB SMT library

- **Conclusion:** As of 2026-11-06, every 27Ω 0603 chip resistor in the
  JLCPCB SMT parts library is Extended; there is no Basic part to
  substitute for R3/R4 (0603WAF270JT5E, C25190) to save the $3.09
  extended-parts fee. (confidence: high for the library state on that
  date; trials: 2 library-wide searches plus individual part checks)
- **Conditions tried:** JLCPCB parts library searches on 2026-11-06 —
  "27R0 0603" (172 results; filtering to Basic returned 0) and "27ohm
  0603 resistor" (3,288 results; Basic filter returned 0). Individual
  checks: C25190 (Extended), C25224 0603WAJ0270T5E (Extended), C22966
  0603WAF2700T5E (Basic).
- **Failed attempts:** 0603WAF2700T5E was initially assumed to be a 27Ω
  Basic candidate; in the Uni-Royal code "2700" is 270Ω, not 27Ω — the
  assumption was caught by checking the part page before any BOM change.
- **Validity scope:** Library contents change over time. Re-verify when a
  future BOM cost-down targets a 27Ω 0603, or when JLCPCB revises its
  Basic parts list. Applies to 0603 thick-film parts of 100mW or more;
  other packages and values were not searched.
- **Evidence:** PR #189 (amendment note in docs/issue-185-main-rev3.md).
- **Promoted to:** —
