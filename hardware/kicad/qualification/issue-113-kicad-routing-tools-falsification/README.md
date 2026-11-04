# Issue 113 evidence

`evidence/instructions.md` is the complete PO instruction. See the report at
[`docs/issue-113-kicad-routing-tools-falsification.md`](../../../../docs/issue-113-kicad-routing-tools-falsification.md).

- `inputs/{smoke,main}/`: immutable original native PCB/project, corrected DSN and a fresh public KiCad snapshot.
- `input-provenance.json`, `*-dsn-equivalence.json`, `equivalence-gate.json`: source/hash freeze and independent pre-route equivalence.
- `official/`, `source-provenance.json`, `source-manifest.json`, `release-v0.23.8.json`: official version, MIT license, documentation/defaults and source provenance.
- `processes/`: exact argv, UTC, elapsed time, exit, environment, stdout and stderr for each process. Routing processes are named `smoke-route` and `main-route`; installation/help/inspection are distinct.
- `runs/`: untouched router inputs and raw outputs, including output project settings.
- `inspection/`: exact output PCB copy graded with the original frozen project. This keeps the tool's DRC writeback from changing independent acceptance.
- `*-board-diff.json`: all nonroute AST additions/removals, original copper preservation, snapshot differences and output-project changes.
- `*-width-inspection.json`: complete native track/via inventory and static width distribution.
- `*-independent.json`, `smoke-gate.json`: independent outcome and Stage 1 gate.

The KRT source checkout, native binary and Python/KiCad installations are temporary
and are excluded from the submission. KRT's own diagnostics are telemetry only.
