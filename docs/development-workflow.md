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

## EDA method changes and retries

Before proposing an EDA method change or retry, read
[`eda-path-history.md`](eda-path-history.md) and state the previous stop reason,
the concrete difference in the proposed method, and the first hypothesis to
verify. Separate observed evidence, PO supplements and unconfirmed causes.
Carry forward existing evaluation effort and limits; a candidate change does not
reset the budget. Existing decisions remain intact until a separate Human Gate.
