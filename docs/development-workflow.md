# Development workflow

## Issue-driven standard flow

All implementation starts from an approved GitHub Issue, which is the work
contract for its Purpose, Scope, Out of scope, Acceptance Criteria, verification,
and Human Gate.

> Issue → PO instruction to Codex → Issue branch → implementation → Draft PR →
> CI → PMO review → PO approval → Squash merge → Issue close

1. The PO selects and prioritizes an Issue and instructs Codex.
2. Codex creates a dedicated branch from the latest `main`.
3. Codex implements only the Issue Scope and updates the required documentation.
4. Codex opens a Draft PR early, links it with `Closes #<issue>`, and records
   verification and out-of-scope discoveries.
5. CI checks all automatable Acceptance Criteria, including applicable builds,
   ERC/DRC, and generated-artifact consistency.
6. The PMO reviews the Issue, diff, documentation, and CI read-only and gives the
   PO evidence supporting a MERGE or HOLD decision.
7. The PO performs the Human Gate and final approval, then squash-merges.
8. The linked Issue closes when the PR is merged.

## Branch, commit, and PR policy

- Implementation must start from an Issue.
- One Issue equals one PR.
- Direct implementation commits to `main` are prohibited.
- A PR may contain iterative or experimental commits while review continues.
- PRs are squash-merged so `main` retains each reviewed increment as one commit.
- CI becoming green never authorizes an automatic merge; PO approval is required.
- Out-of-scope findings are reported in the PR and proposed as follow-up Issues,
  not fixed in the current branch.

## Dashboard and deployments

The Dashboard is a human-readable overview/read model. It does not own project,
PR, commit, or CI truth; the precedence policy in [governance](governance.md)
applies. Production represents merged `main`, while a PR Preview may represent
the proposed state in that PR. Dashboard heartbeat updates are neither required
nor permitted as a reason for commits.

Dashboard changes needed by an Issue are reviewed in that Issue's PR. Do not add
a post-merge GitHub Action that writes Dashboard updates to `main`. Structured
docs/status-to-Dashboard generation may be considered separately in the future.
When an Issue changes high-level progress, update the authoritative
[`project-status.md`](project-status.md) and manually synchronize the Dashboard
read-model copy in `task/data/project-status.js` in the same PR.

When accepting an evaluation result, the PR must update both records with:

- product-development location, separate from the current technical evaluation
  stage; record each stage's purpose/output, confirmation, completion condition,
  accountable decision owner, and known dependencies. Mark missing plan details
  as unplanned instead of inferring them;
- latest evaluation's work state, technical result, tested scope and explicit
  successful, failed, unverified, or not-entered evidence;
- next owner's concrete decision/action, target, and start condition. If no
  next technical step is authorized, state that plainly instead of proposing
  an experiment as an instruction;
- current problems and unresolved uncertainties, including their evidence,
  consequence, needed proof, disposition, owner (or unassigned), and source.
  Keep downstream and historical-method risks separate. Label any mitigation
  proposal unapproved;
- links to the authoritative report and history, with the Dashboard fields
  derived from the same structured data. Keep stable decision/history references
  separate from fields that follow the latest evaluation identifier, links, and
  status.
- distinguish retained decisions/constraints and completed historical plans from
  the next experiment. Record each constraint's scope and source; PMO prepares the
  next target, method, implementer, individual acceptance conditions and investment
  boundary for the PO to decide. Prior execution permission does not transfer to a
  new candidate or run.

For a Dashboard review, substitute a temporary latest-evaluation record and
verify the current-stage and evaluation panels update IDs, links, title, and
status without stale current references. Do not commit the temporary record.

Review the wording separately for assessment/report completion, technical
acceptance, method adoption, and manufacturing approval. A merged report,
green CI, completed issue, or finished fixture does not by itself establish
technical success, approve a design method, or pass a manufacturing gate.
Record the status confirmation timestamp from its source; do not use page-view
time. Production reflects merged `main`; PR Preview content is a proposal, not
current accepted status.

## Merge gates

Before the PO makes the merge decision:

- the Issue Acceptance Criteria are accounted for,
- relevant GitHub Actions jobs pass,
- applicable KiCad ERC/DRC is clean,
- generated artifacts are reproducible and consistent,
- required documentation is updated,
- remaining risks, Human Gates, and out-of-scope findings are documented.

The GitHub merge-method and branch-cleanup settings are manual PO actions listed
in [governance](governance.md#repository-settings-po-manual-action).

## Verification evidence

These checks supply evidence for the Merge gates above. The implementer / Codex
runs and records each applicable check in the PR's Verification / CI section;
PMO reviews that evidence read-only and PO retains the acceptance / Human Gate
decision. Record why a check is not applicable rather than leaving it blank.

### Independent acceptance

- **Applies when:** accepting generated or modified engineering artifacts,
  including routing results. Source: [F-002](findings.md) (K03).
- **Inputs:** approved Issue criteria, source commit and input hashes, original
  project rules, exact tool versions / effective settings, saved output artifacts
  and tool logs.
- **Check:** independently read and inspect the saved artifacts against the
  approved criteria; for PCB routing include actual copper connectivity, DRC,
  dimensions and input/output project-setting differences, using the original
  approved rules. Record the independent method, versions, results and evidence
  paths separately from the generator's exit code and self-reported unrouted /
  violation counts. Neither exit code nor self-reported counts establish pass.
- **Stop when:** independent checks fail, are missing, or settings differ without
  authorization. Do not report acceptance or continue to a dependent stage;
  report failed / unverified items, keep null results distinct from zero, and
  obtain PO direction before changing requirements or retry limits.
- **Owner:** implementer / Codex produces evidence; PMO checks it; PO decides.

### Retained-artifact comparison

- **Applies when:** making a local change or repair with wiring or data that must
  remain unchanged. Source: [F-008](findings.md) (K07).
- **Inputs:** frozen pre-change artifacts / hashes, permitted change scope and an
  explicit retained wiring / data set, plus saved post-change artifacts.
- **Check:** compare the retained set before and after as an acceptance condition,
  alongside independent acceptance above. For PCB copper, check retained segment
  coverage on the same layer, width and net, via identity / geometry, nonroute AST,
  whole-board connectivity and DRC; compare retained data by content / structure
  as appropriate. Record differences and evidence, including zero differences.
- **Stop when:** the retained set is undefined, comparison is missing, or retained
  wiring / data is lost or changed outside the permitted scope, even if connection
  and DRC counts pass. Report and seek PO direction before expanding scope.
- **Owner:** implementer / Codex defines the set from the approved scope and checks
  it; PMO reviews the comparison; PO decides any scope change.

### Full via-pad audit

- **Applies when:** accepting a PCB containing vias, or changing PCB / pad / via
  geometry, copper layers or manufacturing conditions. Source:
  [F-004](findings.md) (K09).
- **Inputs:** saved PCB hash, native effective pad copper shapes / common copper
  layers, via outer diameters and the approved design-audit clearance criterion
  (this project's criterion is at least 0.10 mm).
- **Check:** audit every via against every copper pad on common copper layers,
  including same-net, NC, reinforcement and bare test pads; exclude NPTH without
  copper. Measure clearance from the via annulus outer edge to pad copper, not
  from the drill edge. Record counts / coverage, minimum gap, violations and
  evidence for the full set, including non-overlapping pairs. Electrical DRC or
  overlap-only checks do not replace this audit. This nominal-geometry criterion
  does not certify manufacturing tolerances, vendor DFM acceptance or cost.
- **Stop when:** coverage or inputs are incomplete, or any pair misses the
  approved clearance; report and hold acceptance pending correction and full
  re-audit, with independent connectivity / DRC / CAM rechecks as applicable.
- **Owner:** implementer / Codex performs the audit; PMO reviews coverage and
  results; PO decides acceptance and any manufacturing Human Gate.

## PCB-to-case handoff

- **Applies when:** updating PCB-side inputs (such as CSVs) supplied to the case,
  including changes to geometry, datums, coordinate transforms or mounting holes.
  Source: [F-005](findings.md) (K12).
- **Inputs:** approved source commit and complete input-file manifest with hashes
  (including each pitch / side), received case-side copies, coordinate transforms,
  expected mounting-point identities / positions and generated case artifacts.
- **Check:** compare the complete file sets and hashes between approved PCB
  sources and case inputs, not just outlines or filenames. Compare mounting-point
  sets, including additions / removals, identities and transformed positions,
  against case holes and bosses; counts alone are insufficient. Check boss wall
  material, pilot-hole openings and inverse-transformed hole positions against
  declared tolerances. Record expected / actual sets, hashes, differences and
  evidence for every variant. Digital geometry checks do not establish physical
  retention, creep or print-shrinkage performance.
- **Stop when:** files / hashes / mounting-point sets differ, required boss or
  hole checks fail, or inputs / tolerances / evidence are missing. Hold handoff
  acceptance and downstream use until reconciled; report to PO rather than
  carrying forward an old mounting-point count.
- **Owner:** implementer / Codex records PCB-side inputs and case-side receipt /
  checks; PMO reviews their correspondence; PO resolves input changes and accepts
  the handoff.

## EDA method changes and retries

Before proposing an EDA method change or retry, read
[`eda-path-history.md`](eda-path-history.md) and state the previous stop reason,
the concrete difference in the proposed method, and the first hypothesis to
verify. Separate observed evidence, PO supplements and unconfirmed causes.
Carry forward existing evaluation effort and limits; a candidate change does not
reset the budget. Existing decisions remain intact until a separate Human Gate.
