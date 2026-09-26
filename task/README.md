# Task management

The dashboard UI is `task/index.html`. Its maintained data sources are:

- `data/project-status.js`: roadmap, workstreams, human gates, risks, task list,
  and the latest Git/PR/CI/artifact evidence snapshot.
- `data/runtime-status.js`: the AI/Codex self-report, updated only at work start,
  meaningful checkpoints, blockers, blocker resolution, human gates, or milestone
  completion. Do not create heartbeat commits.

The browser derives the prominent health state from both sources. A CI failure or
concrete blocker overrides a `RUNNING` declaration, a ready/waiting human gate
produces `WAITING_FOR_USER`, and contradictory evidence is marked `STATUS
MISMATCH`. A lack of commits by itself never marks design work as blocked.

The dashboard has no build step and can be opened locally or hosted as static
files (including Vercel Preview). Keep the evidence snapshot explicit: the page
must show `UNKNOWN` rather than inventing a CI result when Actions data has not
been synchronized.
