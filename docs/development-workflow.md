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
