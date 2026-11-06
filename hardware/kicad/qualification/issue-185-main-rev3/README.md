# Issue #185 evidence

[Report](../../../../docs/issue-185-main-rev3.md).
Qualified Main Rev.3, with 35 relocated vias, unchanged placement and no whole-board
routing. All four metrics zero / 44 nets; all 113 vias ≥0.10 mm from pad copper;
common and branch loops below 50 mΩ in the extraction model. No manufacturing GO.

- Final: [board](inspection/final/main.kicad_pcb), [assessment](inspection/final/assessment.json), [route delta](inspection/final/transfer-diff.json), [connectivity](inspection/final/connectivity.json).
- Progress: [33 moves](straight33/changes.json), [last two](local35/changes.json).
- Audit: [all 113 vias](local35/audit/via-pad/all-vias.csv), [summary](local35/audit/via-pad/summary.json), [paste](paste-via-check.json).
- Resistance: [summary](resistance-summary.json), [numerics](ground-model-verification.json).
- Manufacturing: [package](manufacturing/), [CAM](cam-check.json), [handoff](manufacturing/quote-handoff.md).
- Execution: [processes](processes/), [verification](verification.json), [publication](publication.json).

KiCad 9.0.9 is read from the existing he-piantor-42 runtime. All scratch files,
configuration, export staging and Git metadata are in `.issue185-runtime/` of
this worktree. `common.py` contains the runtime paths and environment. Run scripts
through `python3 <this-directory>/run.py <unique-process-name> /usr/bin/python3
<script-path> [arguments]` from the repository root. CAM parsing/rendering uses
the existing `.issue147-runtime/viewer-venv/bin/python` instead of system Python.

`source183/audit.py` is the unchanged #183 all-via audit. `audit-board.py` supplies
a snapshot of the new board. `source183/move-probes.json` preserves the 35 original
single-via probes; the implementation records and final qualification establish
simultaneous validity. `apply-straight.py` creates the 33-via board. `local-two.py`
adds only local segments for the final two vias, with no ripup. It searches via
positions within 3 mm at 0.025 mm resolution, with centerline routes in a local
6 × 6 mm box. Rerunning generation changes new track UUIDs; the saved changes.json
and transfer check bind this run's actual UUIDs and geometry.

`prepare-inspection.py final`, snapshot reader `eda-004g/resume-02/read-pcb.py`,
`connectivity.py final`, native `kicad-cli pcb drc`, and `assess.py` produce the
independent qualification. `extract-power.py final`, `extract-ground.py final`,
`verify-ground-model.py` and `summarize-resistance.py` reproduce model extraction.
Existing completed run directories are deliberately not overwritten by the
process wrapper. Use a separate evidence copy / new process labels for reruns.
