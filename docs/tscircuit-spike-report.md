# tscircuit Hall-key technical spike (Issue #13)

Status: **STOP 1 — FOOTPRINT INTEGRITY: REACHED; PMO / Product Owner Human Gate required**

The reproducibility gate is complete. The current checkpoint is limited to
STOP 1 Hall-footprint conversion and machine-readable geometry inspection. It
does not proceed to Hall-key electrical TSX, board design, routing, DRC, or
manufacturing outputs.

## Execution context and source protection

- Execution date: 2026-09-28 (UTC).
- Checkpoint starting commit: `89a760f3a5aeb02d578dbf6066bde1e77995da48`.
- Existing PR: #16 for Issue #13.
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
- Run #5: **PASS**;
- Run #5 artifact ID: **11003505777**;
- committed lockfile reproducibility Gate: **PASS**;
- Run #6: **RED** (verification harness failed before geometry evaluation);
- engineering-ci #127: **PASS**;
- Run #7 converter invocation: **PASS**;
- Run #7 geometry verification: **completed**;
- Run #7 artifact ID: **11020587967**;
- Run #7 tscircuit spike bootstrap: **RED because the STOP 1 Gate intentionally failed**;
- engineering-ci #128: **PASS**;
- GitHub Actions dependency installation (`npm ci`): **PASS**;
- Bun 1.2.22 runtime check: **PASS**;
- `tsci` 0.0.2646 runtime check: **PASS**;
- bootstrap artifact upload: **PASS**;
- tscircuit spike workflow through Run #5: **Green**;
- engineering-ci: **Green**.

Run #5 demonstrated that GitHub Actions can install the committed dependency
set and execute both pinned runtimes. The workflow verifies the committed
SHA-256 before installation and requires a clean lockfile diff after `npm ci`.

## STOP 1 — Hall footprint integrity checkpoint

The workflow now passes the authoritative
`hardware/lib/third_party/marbastlib-he.pretty/SW_MX_HE_0deg_1u.kicad_mod`
source text directly to the installed `kicad-to-circuit-json` 0.0.117
`KicadFootprintToCircuitJsonConverter`. It writes the unedited converter result,
stderr/warnings, a detailed geometry report, and a compact machine-readable
decision to the evidence artifact.

Run #6 did not produce a footprint-capability conclusion. Its converter step
failed before geometry evaluation because the evidence directory did not yet
exist when shell redirections were opened and because the harness called a
nonexistent `convert()` method. For Run #6, this was a verifier/converter
execution failure, not a STOP 1 result; STOP 1 was not evaluated in that run.
The corrected harness
creates the evidence directory before redirection and uses the converter's
documented `addFile()`, `runUntilFinished()`, and `getOutput()` lifecycle.

Run #7 successfully exercised that corrected lifecycle. The converter ran to
completion, and CI generated the raw Circuit JSON, converter diagnostics,
geometry report, and `verification-result.json`. The final Gate then failed as
designed because that machine-readable result established STOP 1. This is not
a verifier failure, CI infrastructure failure, reproducibility failure, or
geometry-checker false negative.

### Run #7 geometry result

The following authoritative geometry was preserved:

- Hall SMD pads 1, 2, and 3;
- plated through-hole pad 3;
- duplicate pad-number 3 semantics across the SMD and through-hole pads;
- both non-plated switch holes;
- the plated/non-plated distinction; and
- relative Hall-sensor and switch-hole alignment.

The observed coordinate transform was **y-inverted**. This was a consistent
converter coordinate-system transform, so the relative alignment is preserved
even though the numeric Y coordinates are transformed.

The authoritative footprint contains two keepout zones, **HE keepout_bot** and
**HE keepout_top**. The converted Circuit JSON contains no keepout elements, so
both keepout geometry and semantics are **lost**. The converter emitted no
warning for this drop.

The verifier checks SMD pads 1/2/3, both instances of pad number 3, the plated
through-hole dimensions, the two non-plated holes, and a consistent observed
coordinate transform. Keepouts receive a deliberately strict check: their
Circuit JSON elements must expose layer scope and all track, via, pad,
footprint, and copper-pour permissions. Polygon survival alone is not treated
as semantic equivalence. A missing or incomplete representation is reported as
`STOP 1 — FOOTPRINT INTEGRITY`, never replaced with inferred geometry.

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

**STOP 1 — FOOTPRINT INTEGRITY: REACHED.** The authoritative
`SW_MX_HE_0deg_1u.kicad_mod` keepout semantics cannot be carried into Circuit
JSON by `kicad-to-circuit-json` 0.0.117. Because these keepouts are important
authoritative geometry, their silent loss prevents footprint-integrity
equivalence even though the pads, holes, plating distinction, and relative
alignment were preserved.

No workaround is attempted. In particular, this checkpoint does not add
handwritten keepout geometry, inject keepouts through TSX, edit generated
Circuit JSON, create a replacement footprint, modify the authoritative KiCad
footprint, weaken the verifier, or downgrade STOP 1 to a warning.

**STOP 4 is not reached.** A fresh GitHub Actions environment successfully runs
`npm ci` from the committed lockfile and runs the pinned Bun and tscircuit CLI
versions. The workflow now additionally makes lockfile existence, SHA-256
integrity, and a clean post-install diff mandatory.

STOP 2, STOP 3, and STOP 5 remain outside this checkpoint. No claim about
tscircuit's complete Hall-key, board, DRC, or manufacturing-output capabilities
is made here.

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
- Run #7 converter invocation: **PASS**;
- Run #7 raw Circuit JSON generation: **PASS**;
- Run #7 geometry report generation: **PASS**;
- Run #7 `verification-result.json` generation: **PASS**;
- Run #7 tscircuit workflow: **RED by intentional STOP 1 Gate**;
- converter warnings: **none**;
- SMD pads 1/2/3: **preserved**;
- plated through-hole pad 3: **preserved**;
- duplicate pad-number 3 semantics: **preserved**;
- NPTH switch holes: **preserved (2)**;
- plated/non-plated distinction: **preserved**;
- coordinate transform: **y-inverted**;
- relative alignment: **preserved through the consistent transform**;
- keepouts: **lost**;
- STOP 1: **REACHED**;
- existing KiCad files unchanged: **PASS**.

## Human Gate

This checkpoint stops at **PMO / Product Owner Human Gate**. Keep PR #16 as the
STOP 1 evidence PR; do not merge it or close Issue #13. Hall-key electrical
TSX, full migration, four-layer board work, routing, DRC, and Gerber / drill /
BOM / CPL or pick-and-place generation remain explicitly deferred.
