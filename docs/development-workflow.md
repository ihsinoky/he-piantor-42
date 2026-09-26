# Development workflow

## Branch and pull-request policy

`main` is the stable integration branch and the production source for the Vercel dashboard.

Engineering work is performed on scoped branches and merged through pull requests.

Default flow:

1. Create a branch for one reviewable engineering increment.
2. Implement and update design documents and dashboard state on that branch.
3. Run GitHub Actions.
4. Open a draft pull request while work is still in progress.
5. Continue commits on the same branch until the PR acceptance criteria pass.
6. Mark the PR ready for review.
7. Merge to `main`.
8. Vercel production then reflects the merged dashboard state.

Do not commit implementation work directly to `main`.

## PR sizing

Prefer one PR per engineering gate, not one PR per file or per small fix.

Current planned sequence:

- Sensor-test electrical baseline: schematics, firmware logger, BOM, CI.
- Sensor-test PCB layout and DRC.
- Sensor-test manufacturing package.
- Sensor-test bring-up / measurement tooling.
- Main 42-key schematic.
- Main PCB layout.
- Production firmware baseline.
- Mechanical enclosure.
- Manufacturing/release package.

A PR may contain multiple commits while the engineering gate is being developed.

## Dashboard behavior

`task/index.html` is updated on the active branch as part of the same PR.

The Vercel production deployment tracks `main`, so it intentionally shows only merged state.

For work-in-progress inspection, use the Vercel preview deployment associated with the branch/PR.

## Merge gates

Before a PR is considered ready:

- relevant GitHub Actions jobs pass,
- KiCad ERC/DRC is clean for included manufacturing-intent files,
- generated artifacts are reproducible,
- BOM/reference designators are internally consistent,
- dashboard reflects the PR state,
- remaining risks and human actions are documented.
