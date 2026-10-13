# EDA-004F evidence bundle

The completed Issue #83 evaluation is isolated here. Authoritative report:
[headless-schematic-qualification.md](../../../../docs/headless-schematic-qualification.md).
Do not launch another experiment from these scripts without separate PO authorization.

- `contract.json`: manually frozen independent pin/value/net/NC oracle.
- `generate.py`: only public external-library calls, unchanged after first generation.
- `reconcile.py`: independent read-only source/XML checks; no generator import.
- `run-evaluation.py`: gated conditional negative/value/fresh trials actually executed.
- `capture.py`: thin adapter to unchanged EDA-004D process recorder, now also blocks
  experiments after terminal completion. `verify-`, `record-`, `git-`, `ci-` remain allowed.
- `requirements-lock.txt`: exact resolved runtime distributions with download hashes.
- `library/`: losslessly gzip-wrapped, unchanged official 9.0.9 package libraries and license; attributable to
  the KiCad library community. See package/source identities in preparation metadata.
- `evidence/library-source.tar.gz`: unchanged pinned external-library Git archive,
  including MIT license; retained built wheel allows build-free reinstallation.
- `evidence/executed-scripts/`: exact initial orchestration source, including failed
  preparation steps. These are chronology evidence, **not** a successful setup recipe.
- `evidence/processes/<name>/record.json`: command/cwd/env/time/status/artifact hashes.
  `stdout.gz` / `stderr.gz` decompress to recorded SHA-256 bytes. Later verification
  records may retain raw stdout/stderr. Missing `.gz` does not mean missing data.
- `normal-generate`, `disconnect-generate`, `conflict-generate`, `value-generate`,
  `fresh-generate`: raw schematic artifacts. Matching `*-netlist`, `*-erc`,
  `*-reconcile` directories retain KiCad XML/JSON and comparisons. Normal corrected
  ERC is in `normal-erc-configured`; initial failed report stays in `normal-erc`.
- `*-acceptance.json`: individual fixed-contract results, separate from first acceptance.
- `file-comparison.json`, `*-raw.diff.gz`, `*-uuid-normalized.diff`: read-only differences.
- `immutable-sha256.json`: input/raw-evidence hashes; ledger and submission notes
  remain mutable reporting records, not scientific inputs.

Safe evidence verification (no new KiCad/generation experiment):

```sh
/tmp/eda004f/venv/bin/python -B hardware/kicad/qualification/eda-004f/validate.py
node --check task/data/project-status.js
node --check task/dashboard.js
git diff --check 3ed5558855c7d95951ea4a728f755707061279b4
```

If the prepared environment is unavailable, `validate.py` only needs `sexpdata==1.0.2`
in addition to Python's standard library. It replays saved source/XML/ERC results,
verifies hashes, the pre-generation freeze, and unchanged protected baseline files.
It does not establish whole-environment reproduction or authorize a new trial.

The evaluated runtime preparation used the existing EDA-004D KiCad installer with
`EDA004D_WORK_DIR=/tmp/eda004f` and `EDA004D_EVIDENCE_DIR` pointing to this bundle.
For a future separately authorized reconstruction, the retained wheel and hashed
runtime lock avoid rebuilding the external library. Exact temporary build-backend
versions from the original install remain unknown. Configure the fixed library
paths in isolated `XDG_CONFIG_HOME/kicad/9.0/sym-lib-table` before standalone ERC.
Before a separately authorized generation, restore the exact input filenames with
`gzip -dk hardware/kicad/qualification/eda-004f/library/*.kicad_sym.gz`.
Fresh generation here reused the already prepared environment; it was not a second
installation of KiCad or dependencies.
