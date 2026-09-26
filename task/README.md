# Evidence-aware dashboard

The dashboard is a static site with no build step. Open `task/index.html` or serve
the repository root with a static HTTP server.

## Sources of truth

- `data/project-status.js` records objective, reviewable evidence: milestone,
  pull request state, CI checks, task state, and review gates.
- `data/runtime-status.js` records Codex's transient execution state: current
  work, blockers, whether user input is required, checkpoint, and next action.

Do not copy project evidence into runtime state, infer a passed check, or embed
either data set back into `index.html`. Update timestamps only when the
corresponding facts change; the dashboard is not a heartbeat.

## Files

- `index.html`: semantic page shell
- `style.css`: presentation and responsive layout
- `dashboard.js`: rendering only
- `data/project-status.js`: durable evidence snapshot
- `data/runtime-status.js`: current agent snapshot
