# EDA-004B — Issue #73

**ENVIRONMENT_BLOCKED / P1_SMOKE_CAPTURE_GUARD_ERROR**, Main initial/confirmation 0/0,
smoke routing 0. See the [terminal report](../../../../docs/alternate-physical-backend-main-qualification.md).
Evidence is **PARTIAL**: the executor's guard rejected allowed local copper before
raw smoke JSON capture; the following converter invocation failed at module load.
First failure: executor verification/capture error, not EDA/backend incapability.
The subsequent converter invocation was a sequence deviation; its
P1_CONVERTER_MODULE_LOAD is a secondary environment obstacle. Immediate-stop
discipline was not followed. Terminal reporting is complete; technical
qualification is incomplete. No further experiment followed the secondary failure.
Stage 2–4, meaningful ERC/DRC,
geometry reconciliation/fault injection and all Main metrics are NOT ENTERED/null.

Execution checkout: `20b25914cc7515ab8ba191f5fdcbba6217a37d23`.
Fixed source baseline: `b84585ecc2cf32000285bbf389d9fea255436980`.
All pre-existing tracked files except the two authorized status copies are
protected in `evidence/protected-files.json`. Production remains 0.0.2646.
Dependencies/disposable installs live under `/tmp/eda004b` and are not committed.

Evidence scripts:

```sh
python3 hardware/tscircuit/qualification/eda-004b/validate.py
python3 hardware/tscircuit/qualification/eda-004b/test-evidence.py
node --check task/data/project-status.js
git diff --check
```

These read/validate the blocked record; they do not route. `reproduce-package-load.sh`
is an unexecuted convenience wrapper for the exact recorded installation failure
in a new /tmp directory, requiring network and the pinned Node/npm. Reproduction
of that error does not qualify a backend. It must not be used as an automatic retry.
The retained `evidence/executed-smoke.tsx` and `executed-convert.mjs` are the exact
failed scripts, not recommended launchers. The smoke guard is known wrong and
must not be credited with copper validation. The hashed run contract is explicitly
incomplete and post-STOP; it cannot authorize a route.

Raw evidence contains the selected converter package and the installed missing-dist
kicadts tree losslessly. `raw-manifest.json` records compressed and uncompressed
hashes. Full failure/install/help logs, selected metadata, converter lock, KiCad
package hashes/extracted file snapshot, authority, checkpoint/effort/attempt records
and evidence integrity manifest are retained. The missing smoke JSON is disclosed,
not reconstructed. No PCB/DSN/SES exists.

No backend adoption, Human Gate, manufacturing exception, merge or follow-up work.
USB NPTH OPEN — PRE-ORDER DFM REVIEW REQUIRED.
