# Project governance

## Roles and responsibilities

### Product Owner (PO)

The Product Owner owns requirements, prioritization, design decisions, Human Gate
approval, instructions to Codex, final pull-request approval, and merge decisions.
All implementation instructions to Codex must come through the PO.

### PMO / Technical Reviewer

The PMO / Technical Reviewer may read the repository, Issues, pull requests, and
CI results. It supports planning and review, drafts proposed Codex instructions
for the PO, and presents evidence for a **MERGE** or **HOLD** decision.

The PMO is read-only. It does not write to the repository and does not create or
modify Issues, branches, commits, pull requests, or merges. It never instructs
Codex directly; proposed instructions are delivered through the PO.

### Implementer / Codex

Codex implements only the Scope of the PO-designated Issue. It is responsible
for implementation, relevant tests, documentation updates, the Issue branch and
pull request, and fixes for CI failures introduced or exposed by that work.

Changes outside the Issue Scope are prohibited. Codex records discovered
out-of-scope problems under **Additional issues discovered** in the pull request
and, when useful, proposes a follow-up Issue instead of fixing them unilaterally.

### CI / GitHub Actions

CI performs repeatable, automated acceptance checks, including builds, KiCad
ERC/DRC, generated-artifact consistency, and any other Acceptance Criteria that
can be evaluated automatically. CI evidence informs review but does not replace
the PO's Human Gate or final approval.

## Source of truth

When project information conflicts, use this precedence order:

1. `docs/`
2. implementation and design artifacts merged into `main`
3. GitHub Issues and pull requests
4. Dashboard

[`docs/project-status.md`](project-status.md) is the authoritative high-level
project-status record. The Dashboard is a human-readable read model, not a source
of truth, and `task/data/project-status.js` is a manually synchronized copy of
that record. If they conflict, `docs/project-status.md` is authoritative.
Production displays merged `main`; a PR Preview may display a proposed,
unmerged state.

A possible future direction is generation from structured documentation or
status data into the Dashboard. No post-merge workflow should write an
unreviewed Dashboard commit to `main`.

## Repository settings (PO manual action)

The Product Owner must configure these GitHub repository settings manually:

- Allow squash merging: **ON**
- Allow merge commits: **OFF**
- Allow rebase merging: **OFF**
- Automatically delete head branches: **ON**
- Auto merge: **OFF**

Repository settings are not changed by repository code or CI in this project.
