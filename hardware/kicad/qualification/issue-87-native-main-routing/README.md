# Issue #87 evidence — DSN rule prerequisite STOP

See [new report](../../../../docs/issue-87-native-main-routing.md).
**CONVERSION_BLOCKED / DSN_RULE_TRANSFER_UNQUALIFIED / MAIN_UNQUALIFIED**.
Main initial/confirmation/small routing **0/0/0**. Raw public exports: small + Main
**2**, both lower typed SMD clearance to 0.05 mm. No SES or routed Main exists.

Reuse authority: commit `49ebe146a586bf820a747b93951a29fe94f08623`, paths/hashes
in `evidence/reuse-hashes.json`. Existing evidence and contracts are read-only.

Execution sequence retained for audit (STOP forbids automatic replay):
`prepare.py`, host geometry correction `prepare-geometry.py`, `stage-ab.py`,
`check-via.py` (geometry Python), `prepare-router.py`, `install-parser.py`,
`export-smoke.py`, read-only official-source discovery, `export-main.py`,
`record-stop.py`. Standard sexpdata was installed for anticipated individual DSN
inspection but that inspection was not completed after the rule prerequisite failed.
Only `verify-saved.py` and Dashboard checks may run for submission after STOP.

Key records: `start.json`, `issue87.json`, `pr86.json`, `immutable-inputs.json`,
`baseline-parity.json`, `effective-spacing.json`, `via-checker-acceptance.json`,
`router-reuse.json`, `transfer-rule-check.json`, `stop-decision.json`,
`attempt-ledger.json`, `effort-ledger.json`, raw `processes/*/record.json` with
commands, timeout/exit/timestamps/environment/raw-output/artifact hashes.
Downloaded official code is inspection evidence with original upstream headers;
its hashes/provenance are recorded in the submission manifest. No upstream
runtime source was changed or compiled.

Three raw logs with upstream trailing whitespace are losslessly gzip archived;
`evidence/exact-archives.json` preserves original/archive hashes. This is packaging,
not diagnostic suppression or byte editing. `verify-saved.py` checks expanded bytes.
