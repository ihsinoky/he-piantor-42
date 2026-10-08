# EDA-004D bounded converter repair

**CONVERSION_BLOCKED / D1_FOOTPRINT_LIBRARY_ID_COLLISION**, Issue #77.
Limited object parity passes after three source-file repairs. Complete pre-route
acceptance fails: distinct footprints share `tscircuit:chip`; real ERC still has
three errors and sixteen warnings. Smoke initial/fresh routes 0/0; Main 0.

See [report](../../../../docs/alternate-physical-backend-converter-repair.md),
[frozen acceptance](acceptance.md), [STOP](evidence/stop-decision.json),
[patch](converter.patch) and [source/build provenance](evidence/patch-provenance.json).
Original converter source is retained once as the downloaded commit archive.
Existing locks, fixture, original release archive and checkers are referenced by
baseline commit/path/hash in `evidence/references.json`; none are overwritten.

Read-only validation: `python3 -B validate.py`. `reconcile.py` only reads saved
artifacts and performs in-memory fault checks; it never launches KiCad or repairs
a generated file. The process wrapper rejects experiment launch after STOP.

`python3 -B replay.py` prints the recorded procedure without execution. A separately
authorized reproduction can use `--execute --work-dir /absolute/new/work
--evidence-dir /absolute/new/evidence`; both directories must not exist. It verifies
retained archives/locks, applies the patch to an isolated copy, builds, replays
the unchanged EDA-004C raw and captures KiCad reports. It does not use an existing
unrecorded `/tmp` tree. Network access is required for exact npm dependencies and
the isolated APT extraction. APT dependency closure is recorded by hashes, but
mutable repository availability is a portability limit. Complete replay/fresh
qualification was **NOT ENTERED** in this Issue; the procedure is recorded and
syntax-checked, not represented as tested fresh acceptance.

Converter runtime build uses `tsup-node lib/index.ts --format esm` from the exact
EDA-004C kicadts build lock (tsup 8.5.1). Declaration generation is omitted because
it is not a runtime input. Converter runtime lock is unchanged; built same-source
kicadts is attached only inside the isolated runtime. `setup-js.py`,
`build-converter.py`, `install-kicad.py` and `evaluate.py` record each child command,
UTC times, exit status, stdout/stderr and artifact SHA-256 before content checks.
No full converter declaration/typecheck or upstream suite PASS is claimed.
