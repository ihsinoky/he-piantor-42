# EDA-004E — disposable native KiCad fixture

**PCB_IO_PASS / FRONTEND_UNQUALIFIED**. See
[report](../../../../docs/native-kicad-authoring-feasibility.md),
[history](../../../../docs/eda-path-history.md),
[contract](fixture.json) and [STOP](evidence/stop-decision.json).
Initial fixture acceptance **FAIL**; effective-rule probe and conditional fresh
trial **NOT ENTERED**. Do not infer migration, ERC, routing or Main qualification.

Read-only validation: `python3 -B hardware/kicad/qualification/eda-004e/validate.py`.
The original EDA-004D capture and installer are imported unchanged; baseline
commit/path/hash references are in `evidence/references.json`. `prepare.py`
recreated KiCad 9.0.9 once in new `/tmp/eda004e`. It requires network access,
the same Debian/Ubuntu-compatible host and an absent work root. Dependency
closure hashes are recorded but APT repositories may change. No Codex or GUI
setup was performed. Per-package commands/times/exits/raw are losslessly grouped
in `package-extractions.json.gz`; nonempty process stdout/stderr are losslessly gzip compressed.

`author.py /absolute/empty/new/directory` loads the unchanged official footprint
and saves only through public KiCad functions. `inspect.py input.kicad_pcb
snapshot.json [roundtrip.kicad_pcb]` checks saved objects against the frozen
contract; the optional final argument requests a KiCad resave/project save.
Both run under `/usr/bin/python3` with overrides in `evidence/kicad-env.json`.
The recorded initial creation and separate reload/inspection/CLI commands are
in `evidence/processes/*/record.json`. `evaluation-sequence.py.txt` is the actual
orchestration used after the checker correction, retained as a sequence record;
it is not a new automated frontend or a fresh replay PASS.

Any later experiment requires separate authorization and fresh evidence/work
locations: the unchanged capture rejects experiment calls after this STOP.
Do not execute authoring against retained artifacts, patch KiCad output or treat
CLI exit 0 as acceptance. DRC ran all default severities without exclusions;
its report must distinguish the two planned unconnected links and both real
unexpected warnings. The predeclared clearance-negative probe was never run.

The KiCad Libraries footprint is attributed to the KiCad library contributors,
repository `https://github.com/KiCad/kicad-footprints`, commit
`7ebfa6b23cc292a56f751b7b5f4a0e12eeef69dd`. Its original
[license and generated-design exception](library/LICENSE.md) are retained;
[immutable provenance/hash](evidence/official-footprint.json) identifies the
unmodified file. No other footprint libraries are vendored.
