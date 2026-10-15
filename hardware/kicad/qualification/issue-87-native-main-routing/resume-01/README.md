# Issue87 resume01 — PO-authorized typed clearance restoration

Authority: current PO instruction summarized in [authority.md](authority.md).
Same branch/PR88, starts2026-10-14T21:13:54Z at47bb0e6, clean, remote identical.
Prior STOP and all old code/contracts/evidence remain immutable; hashes of966
tracked prior-epoch files recorded in `evidence/preserved-files.json`.

The six-hour Issue87 frame is continued, not reset. Prior conservative13min
charged. Cumulative1h checkpoint22:00:54UTC; final session deadline03:00:54UTC
next day, with experiments cutoff02:30:54UTC for report reserve. The inter-session
PO wait is separate, with boundary uncertainty recorded in `start.json`.

Pipeline / bounded code:

- `session.py`: new evidence capture using unchanged repository process recorder.
- `restore-clearance.py`: sexpdata structural precheck, known unit um/resolution10,
  exactly one global smd_smd50→200 value. Patches only the numeric byte span;
  never reserializes or overwrites raw. Node path/location/values/hashes recorded.
- `check-clearance-change.py`: separate AST diff, complete other rule inventory,
  byte diff and hashes. No import from mutation code. `test-restoration.py`
  verifies six fail-closed cases and preservation of unrelated50.
- Raw DSNs remain at commit47bb0e6 under prior evidence/processes/{main,smoke}-dsn;
  corrected DSNs + mutation/diff records live in this resume's captured processes.
- `InspectDsn.java`: public HeadlessBoardManager load and BoardRules getters only;
  raw/fixed effective F/B matrix, all pins/nets/shapes and NPTH obstacles captured.
  No router or rule mutation; fixed official source is inspection evidence.
- `check-dsn.py`: fixed-fixture individual read-only graph/shape/placement/outline/
  rule/local-copper/NC/duplicate/hole reconciliation and public readback comparison.
  Existing2nm tolerance reused, no geometric/material relaxation. DSN shares image
  shapes and does not carry every KiCad property; retained properties and router
  obstacles are explicitly distinguished in parity output.
- `InspectSettings.java`: fixed public CLI settings parser probe, no routing.
- `route-small.py`, `route-main.py`: registered one-use processes; frozen inputs,
  versions/settings and bounded timeouts before launch. `import-small.py` /
  `import-main.py` use public ImportSpecctraSES on copies of original KiCad boards.
- `check-import.py` checks complete nonroute KiCad semantics, original local copper,
  independent graph and DRC for the small trial. `assess-main.py` preserves every
  terminal metric before verdict so failures are not reported as zero/unmeasured.

Correction history and failed raw logs are kept: sexpdata bracket-token adaptation
in checker memory; physically identical original trace split at a new junction
must not fail by segment-record identity. No expected geometry or source rule
was changed; no route was repeated for these checker corrections.

Known61 print warnings/glyph uncertainty are deferred manufacturing issues only.
Public-loading matrix class `null` is sentinel0, never assigned to physical input
pads/obstacles/traces; only that unused class is omitted from >=.20mm matrix check.
Net-associated pads are assigned kicad_default, NC pads use smd; all actual input
class pairs, including smd/smd, are checked. Raw rules and ordinary/netclass
relations are retained and read back, not inferred from edited text.
