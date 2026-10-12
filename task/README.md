# Project Dashboard

The UI at `task/index.html` is a human-readable project overview and **read
model**. It is not the source of truth. The authoritative precedence is:

1. `docs/`
2. implementation and design artifacts merged into `main`
3. GitHub Issues and pull requests
4. this Dashboard

If Dashboard content conflicts with `docs/`, use `docs/`. Production represents
merged `main`; a PR Preview can show the proposed state of that PR.

## Data files

- `data/project-status.js` is a manually synchronized read-model copy of the
  authoritative high-level status in `../docs/project-status.md`, plus
  presentation details and optional Git/PR/CI context.
- `data/runtime-status.js` is optional, non-authoritative display context. It is
  not an AI state oracle and must not determine authoritative project status.

GitHub remains authoritative for live PR and CI information, and the Git history
remains authoritative for commits. Snapshot values may be stale and must be
labelled as such; the Dashboard must not invent missing results.
If `data/project-status.js` and `../docs/project-status.md` conflict, the document
is correct. Status changes update both files in the same reviewed PR; there is no
generator or automatic synchronization at present.

## Accepting an evaluation result

In the result-acceptance PR, update the opening status in
`../docs/project-status.md` and the matching structured fields in
`data/project-status.js`. State the product-development location and current
blocker; the latest evaluation's work state, technical result, tested scope and
what remains unverified; and the next owner's action, target and start condition.
If PO/PMO has not selected or authorized a next technical step, show that as
undecided rather than instructing an experiment.

Keep the report and method-history links. Verify that completed evaluation
recording is not described as technical pass, adoption, or manufacturing
approval. Record the source-confirmation time, not the page-view time. Production
is the merged `main` record; a PR Preview shows a proposal. Review the related
procedure and status distinctions in
[`development-workflow.md`](../docs/development-workflow.md#dashboard-and-deployments).

The static Dashboard has no build step. Open it locally or deploy it as static
files. Do not create heartbeat commits. Do not add a merge-triggered Action that
writes Dashboard updates to `main`. A future, separately reviewed solution may
generate the read model from structured docs/status, but no generator exists now.
