# Issue #103 evidence

The analysis is `docs/issue-103-fab-router-falsification.md`. `evidence/` holds frozen
instructions, pinned upstream provenance, the GPL-3.0-only test driver, execution
records, original DSN / resulting SES, self checkDrc, independent smoke results,
static SES measurements, comparisons and verification.

No dependency package bodies are included. The unmodified upstream checkout and
Bun/KiCad/Python dependencies were installed in disposable `.issue103-runtime/`,
with stable paths under `/tmp/issue-103-fab-router/`. Original Git metadata is
read-only; the working branch uses copied metadata at `/tmp/issue-103-fab-router/git`
and this repository as work-tree.

The exact routing commands are in `evidence/processes/{smoke,main}/record.json`.
`driver.ts` accepts `SOURCE INPUT_DSN OUTPUT_DIR`; it sets only `timeBudgetMs` to
1800000, calls `routeDsn` once, then independently re-reads the saved SES through
upstream `readDsn` / `applySes` / `checkDrc`. It never calls the SRJ adapter.
The driver exits 0 on successful API output; final connectivity is a separate field.

The historical stages must not be rerun or overwritten. For a fresh authorized
reproduction, provision a separate evidence destination and the pinned upstream
commit from `evidence/source-provenance.json`, install Bun 1.4.4 with the recorded
digest, and run `bun install` with a writable `BUN_INSTALL_CACHE_DIR`. The runner
refuses existing stage directories and requires the independent smoke gate before
Main. Run the SES scanner with a Python environment containing `sexpdata`.
`run-checks.py` uses KiCad 9.0.9, Shapely and the existing project oracles.

`setup-inspection.py` first provisions Ubuntu runtime dependencies; the retained
KiCad 9 package additionally needs `complete-inspection-runtime.py`. The initial
missing-library import failure is preserved separately. That failure did not load
or alter the board and did not cause a router rerun. The final inspection records
show the actual KiCad version and exit status.

Use `summarize.py` on completed saved results, then `verify.py` while the disposable
source runtime is present. `manifest.json` hashes the submitted artifacts (excluding
itself). `submission.json` records the pre-PR UTC time and deadline; the PR body
records the post-creation verification.
