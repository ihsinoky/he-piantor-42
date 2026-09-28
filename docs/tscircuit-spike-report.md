# tscircuit Hall-key technical spike (Issue #13)

Status: **REPRODUCIBILITY GATE — PASS IN GITHUB ACTIONS; PMO / Product Owner review required**

This checkpoint is limited to making the tscircuit dependency bootstrap
reproducible. It does not make the Product Owner's GO / NO-GO decision and does
not proceed to Hall-key implementation, footprint import, geometry validation,
board design, DRC, or manufacturing outputs.

## Execution context and source protection

- Execution date: 2026-09-28 (UTC).
- Checkpoint starting commit: `89a760f3a5aeb02d578dbf6066bde1e77995da48`.
- Existing PR: #14 for Issue #13.
- The committed `hardware/tscircuit/package-lock.json` is the authoritative
  dependency lockfile. Its expected SHA-256 is
  `a6bd33cc9d0cfdd6f9f60fa343bf413fae4de33b62a8f4c26141857763cf9d33`.
- Existing KiCad files remain unchanged. In particular, this checkpoint does
  not modify the sensor-test schematic, PCB data, libraries, or the
  authoritative Marbastlib Hall-key footprint.

## Reproducible dependency bootstrap

A fresh GitHub Actions checkout now uses the committed lockfile directly. The
normal dependency flow is:

1. check out the repository;
2. set up Node.js 22;
3. set up Bun 1.2.22;
4. require `package-lock.json`, record its SHA-256, and verify the expected
   SHA-256;
5. run `npm ci`;
6. run `git diff --exit-code -- package-lock.json`;
7. run and validate `bun --version`;
8. run and validate `./node_modules/.bin/tsci --version`;
9. capture dependency diagnostics; and
10. upload the lockfile and bootstrap evidence artifact.

The workflow no longer runs `npm install --package-lock-only`. It neither
regenerates nor updates the lockfile during CI. Every command piped through
`tee` retains `set -euo pipefail`, so logging cannot conceal a failure.

The runtime versions validated by the workflow are:

- Bun: **1.2.22**;
- tscircuit CLI (`tsci`): **0.0.2646**.

## GitHub Actions evidence

PMO-confirmed bootstrap history:

- bootstrap Run #2: **PASS**;
- bootstrap Run #3: **PASS**;
- GitHub Actions dependency installation (`npm ci`): **PASS**;
- Bun 1.2.22 runtime check: **PASS**;
- `tsci` 0.0.2646 runtime check: **PASS**;
- bootstrap artifact upload: **PASS**;
- tscircuit spike workflow: **Green**;
- engineering-ci: **Green**.

Run #3 demonstrated that GitHub Actions can install the committed dependency
set and execute both pinned runtimes. The workflow change in this checkpoint
adds the final lockfile-integrity gate: it verifies the committed SHA-256 before
installation and requires a clean lockfile diff after `npm ci`. The new run
number and artifact ID produced for this commit must be recorded from PR #14
before merge; they cannot exist until GitHub Actions executes the committed
workflow.

## Dependency diagnostics and residual risk

`npm ls --all --json` continues to report peer-dependency metadata mismatches
and exits with code 1 for the committed graph. This is a known diagnostic, not
a STOP condition for this reproducibility checkpoint. CI preserves all three
outputs in the artifact:

- `dependency-tree.json`;
- `dependency-tree.stderr.txt`; and
- `npm-ls-exit-code.txt`.

The install also reports **8 moderate / 3 high** npm audit findings. The peer
metadata diagnostics and audit findings remain dependency-health risks for
later review. No dependency versions were independently changed, and the
workflow does not use `--legacy-peer-deps` or `npm audit fix --force`.

Codex Cloud local npm access remains blocked by its network policy. GitHub
Actions execution succeeds, so the local restriction is an environment
limitation rather than evidence that the committed lockfile cannot reproduce
the toolchain.

## STOP-condition assessment

**STOP 4 is not reached.** A fresh GitHub Actions environment successfully runs
`npm ci` from the committed lockfile and runs the pinned Bun and tscircuit CLI
versions. The workflow now additionally makes lockfile existence, SHA-256
integrity, and a clean post-install diff mandatory.

STOP 1 (footprint integrity), STOP 2, STOP 3, and STOP 5 are outside this
checkpoint and remain unassessed. No claim about tscircuit's Hall-key, footprint
import, board, DRC, or manufacturing-output capabilities is made here.

## Reproducibility acceptance status

- committed `package-lock.json` exists: **PASS**;
- `npm install --package-lock-only` removed from normal CI: **PASS**;
- fresh checkout bootstrap: **PASS in GitHub Actions**;
- `npm ci`: **PASS**;
- lockfile unchanged after install: **required by CI for this commit**;
- lockfile SHA-256 matches the committed expected value: **required by CI for
  this commit**;
- Bun 1.2.22: **PASS**;
- tsci 0.0.2646: **PASS**;
- dependency diagnostics saved: **PASS**;
- artifact upload: **PASS**;
- engineering-ci: **Green**;
- tscircuit spike workflow: **Green**;
- existing KiCad files unchanged: **PASS**.

## Human Gate

This checkpoint stops at the reproducibility Gate. Do not merge PR #14 or close
Issue #13 until PMO / Product Owner review. Hall-key TSX, KiCad footprint import,
geometry verification, four-layer board work, DRC, and Gerber / drill / BOM /
CPL generation remain explicitly deferred.
