# EDA-004B — bounded representative Main qualification

**ENVIRONMENT_BLOCKED — P1_CONVERTER_MODULE_LOAD.** Issue #73 reached an
environment STOP before a usable converter deployment or a transport roundtrip.
Main routing is unqualified. Initial Main attempts **0**, confirmations **0**,
Freerouting smoke routes **0**. No backend, Human Gate, manufacturing exception
or order is approved. USB NPTH **OPEN — PRE-ORDER DFM REVIEW REQUIRED**.

This is a completed terminal reporting deliverable with **PARTIAL evidence**,
including executor capture/sequence errors. It is not a completed technical
qualification or a converter-fidelity finding. PMO has not reviewed this work.

## Authority and preserved baseline

[Issue #73](https://github.com/ihsinoky/he-piantor-42/issues/73) was open and had
zero comments when read through the GitHub connector. The PO's execution
instruction satisfies the historical planning prerequisite; no additional approval
comment was requested. The complete Issue and comments, and the
[Issue #71 PO comment](https://github.com/ihsinoky/he-piantor-42/issues/71#issuecomment-6046244229),
are retained in [authority](../hardware/tscircuit/qualification/eda-004b/evidence/authority.json).
The [plan](alternate-physical-backend-qualification-plan.md) and
[incorporated execution conditions](alternate-physical-backend-main-qualification-issue-draft.md)
at `20b25914cc7515ab8ba191f5fdcbba6217a37d23` govern the evaluation.

Preflight found no applicable AGENTS.md. Cwd, origin and required branch were
correct; the worktree was clean. After `git fetch origin` (sandbox escalation
for read-only Git metadata), HEAD and origin/main both remained
`20b25914cc7515ab8ba191f5fdcbba6217a37d23`. No checkout reset, clean, stash or
baseline rollback occurred. Governance/workflow, D-014–D-018, status/Dashboard,
EDA-003B–F reports/final evidence/verifiers, representative source/supporting
footprints and Rev.M1 architecture/interface/DFM policy were inspected.

The separate design baseline remains
`b84585ecc2cf32000285bbf389d9fea255436980`, `RepresentativeMain strategy={3}`.
All five contract source/isolated-lock SHA-256 values match that commit and the
protected working-tree files. The accepted Main comparison artifact also retains
uncompressed SHA-256
`97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131`.
It was hashed read-only and never used as routing input. No Main source copy was
rendered. Required 49 components, 37 named nets, 167 physical endpoints, 30 NCs,
strategy-3 placement, 48 × 44 mm, two layers/1.2 mm, 0.20 mm clearance/width and
0.60/0.30 mm via dimensions are preserved source requirements; they were **not
measured across conversion boundaries** in this execution.

## Selected environment and observed setup

All installations/downloads were isolated under `/tmp/eda004b`. The accepted
EDA-003C frontend lock was copied unchanged; production dependencies were untouched.

| Tool | Exact selected/observed pin |
| --- | --- |
| Frontend | tscircuit 0.0.2748 / core 0.0.2097 / props 0.0.689 / circuit-json 0.0.516 |
| Bun | 1.2.22, official Linux x64 archive |
| Node / npm | 24.21.0 / 11.19.0 |
| Converter | circuit-json-to-kicad 0.0.230; published gitHead `8dee5b926f5db28800292b46b66a712c71aba055` |
| Converter's selected kicadts | upstream manifest Git commit `f3ea106bdc65ca901e9b23255ad3be0bd2a624ab`; package version 0.0.57 |
| KiCad | official PPA `9.0.9~ubuntu24.04.1` amd64, extracted with 106 resolved dependency archives |
| Freerouting | 2.5.0 JAR; Java 25 required by that release's build.gradle |
| Java | Microsoft OpenJDK 25.0.4.1+1-LTS, Microsoft-14951822 |
| Python | /usr/bin Python 3.12.3 for pcbnew; Python 3.14.2 for orchestration/reporting |
| OS | Ubuntu 24.04.5 LTS, x86_64; full uname/os-release retained |

[Environment](../hardware/tscircuit/qualification/eda-004b/evidence/environment.json),
[selected release metadata](../hardware/tscircuit/qualification/eda-004b/evidence/selected-package-metadata.json),
[converter lock](../hardware/tscircuit/qualification/eda-004b/converter-package-lock.json)
and [commands](../hardware/tscircuit/qualification/eda-004b/evidence/command-record.json)
record checksums, provenance and exact resolutions. Essential package hashes:

- KiCad deb: `b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0`.
- Converter tgz: `fcd699c7686ecd08c9fffcfa40807e958fd2beed259aec3c1a4fd3fb7161fdb4`.
- Freerouting JAR: `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7`.
- Bun archive: `4c446af1a01d7b40e1e11baebc352f9b2bfd12887e51b97dd3b59879cee2743a`.

The selected converter distribution has runtime imports absent from its production
dependency declaration. A separate exact-pinned qualification manifest supplied
those imports, using its upstream kicadts Git pin. `npm install --ignore-scripts`
completed, but installed kicadts contained only README, LICENSE and package.json.
That package's `main` points to `dist/index.js`; its referenced prepare script and
library sources were also absent from the installed packed tree. The converter's
first actual module load raised `ERR_MODULE_NOT_FOUND`, before input access.
The [failure](../hardware/tscircuit/qualification/eda-004b/evidence/converter-package-failure.json)
and original stderr preserve this exact deployment failure.

This establishes failure of the recorded **scripts-disabled installation**.
A scripts-enabled install, source build, alternative published kicadts package or
converter release was not tested after STOP. It does not establish that upstream
packaging is generally unusable, that B cannot work, or that a frontend change is
necessary. No dependency substitution, fork or converter/router patch was made.

KiCad CLI version/help and standalone pcbnew import worked without DISPLAY or
WAYLAND_DISPLAY. Public ExportSpecctraDSN/ImportSpecctraSES overloads were observed;
neither was called on a board. CLI help also emitted a missing schema path warning
from the extracted installation. Initial KiCad/Freerouting help probes used default
home paths and emitted permission warnings; isolated XDG paths were then used for
help only. No GUI, virtual display, IPC control, REST routing service or cloud
router ran. These help/import observations do not prove the roundtrip.

Primary source inspection used the
[KiCad 9.0 CLI manual](https://docs.kicad.org/9.0/en/cli/cli.html),
[converter's pinned exports](https://github.com/tscircuit/circuit-json-to-kicad/blob/8dee5b926f5db28800292b46b66a712c71aba055/lib/index.ts)
and [Freerouting 2.5.0 CLI documentation](https://github.com/freerouting/freerouting/blob/v2.5.0/docs/command_line_arguments.md).
Matching executable help is retained. pcbnew/SWIG remains a deprecated,
version-contained qualification dependency, not an adopted architecture.

## Stages, first gate and evidence limits

| Stage | Performed / outcome |
| --- | --- |
| P0 / setup | Checkout and fixed hashes passed; packages/runtime help inspected. Complete library/config/routing-contract freeze **not achieved**. |
| Stage 1 / P1 | One synthetic frontend render attempted; converter module load failed. No complete minimal roundtrip. |
| Stage 2 / P2 | **NOT ENTERED**: no Main generation, USB_SHELL_BOND bridge, source-intent/geometry maps, semantic map, meaningful ERC or source/schematic/PCB parity. |
| Stage 3 / P3 | **NOT ENTERED**: no initial Main routing/import/DRC or independent physical reconciliation. |
| Stage 4 / P4 | **NOT ENTERED**: initial PASS prerequisite absent; no fresh confirmation or reproducibility comparison. |

Two executor errors limit the evidence. The synthetic smoke fixture had explicit
local bond copper and `routingDisabled`; the capture guard incorrectly rejected
**every** pcb_trace, including permitted local copper, and threw before saving raw
JSON. Therefore global copper counts, local-bond shape and source pin semantics
cannot be verified from raw output. A converter command was then attempted despite
that preceding failure; its import failed before it could access the missing input.
The full raw frontend/Node exception logs and exact executed scripts are retained.
There was no regeneration/retry after the terminal STOP. The missing raw JSON cannot
be restored or given a fabricated hash. Shell command groups also did not preserve
individual numeric exits; those are unknown, not reported as zero.

The smoke render was attempted before a complete P0 freeze. This sequence deviation
is disclosed; P0 and Stage 1 are not claimed PASS. The erroneous copper assertion
is an executor guard failure, not evidence that `routingDisabled` loses source
intent or retains stock global routing. Source inspection suggests explicit pcbPath
is separate from ordinary routing; that is not a measured geometry result here.

[Attempt ledger](../hardware/tscircuit/qualification/eda-004b/evidence/attempt-ledger.json):
one frontend smoke generation invocation, one converter module-load invocation,
two Freerouting **help-only** invocations (no `-de`/`-do`), zero smoke routing,
zero Main initial and zero confirmation. No DSN, SES, KiCad board or schematic was
created. No initial/confirmation attempt was consumed. No resumed/tuned route ran.
The [run-contract record](../hardware/tscircuit/qualification/eda-004b/evidence/run-contract.json)
is hashed but explicitly **INCOMPLETE / NOT ENTERED**, with documentation-supported
proposed settings only. It was recorded after STOP and is not represented as a
pre-route freeze or permission to launch.

All four Main acceptance metrics are **null / NOT ENTERED**, including conversion
loss. ERC, DRC, reconciliation, numerical tolerances, semantic coverage and actual
copper checks are also NOT ENTERED. No generic/all-passive schematic is credited
with meaningful ERC. The existing Circuit JSON verifier was inspected but neither
adapted nor claimed to validate KiCad. Shape/transform/layer/plating/short/missing
pad/via/duplicate-land/false-label/rule-loss adversarial geometry tests were **NOT
ENTERED**. Reporting fault tests below do not substitute for those checks.

## Validation, effort and review

[validate.py](../hardware/tscircuit/qualification/eda-004b/validate.py) checks all
pre-existing protected tracked bytes against preflight and starting commit,
production 0.0.2646 in manifest/lock, the five fixed contract hashes, accepted raw
Main hash, retained JSON/package/log integrity including uncompressed archive
hashes, the failure/attempt ledger, null metrics, report/status/Dashboard agreement,
`node --check task/data/project-status.js` and `git diff --check`.
[test-evidence.py](../hardware/tscircuit/qualification/eda-004b/test-evidence.py)
rejects six adversarial **reporting** mutations (false PASS/zero/ERC, hidden attempts
or route count, false evidence completeness). Neither script installs or routes.

D-014–D-018, JITX NO-GO, production dependencies, all accepted EDA-003B–F evidence,
pre-existing designs, verifiers, architecture/interface/DFM and CI remain unchanged.
Changes are confined to the new qualification root, this report and the two
explicitly authorized status copies. Validation of these preserved bytes does
not erase the missing raw smoke capture or make the environment qualified.

Existing engineering-ci classifies these paths without layout/KiCad/firmware
changes; its relevant change-detection and engineering-gate jobs are checked on the
PR. The native-spike workflow's path filter does not match this new root/report.
CI success is evidence/PR hygiene, not routing/ERC/DRC qualification. CI status and
actual checks are retained in the validation/CI records and final PR body.

The [effort ledger](../hardware/tscircuit/qualification/eda-004b/evidence/effort-ledger.json)
separates observed UTC/file/process observations from estimates. AI active effort
is an estimate; no token/time observation is presented as measured engineer-hours.
Human effort and fully unattended process time are unobserved/null. Parallel
installation elapsed time is not added again as human or AI effort. The execution
STOP occurred well inside P1's four-hour ceiling; P0 was incomplete. Later technical
checkpoints were not entered. Reporting/validation is reserved within the aggregate
16-hour ceiling, with no further experimentation.

Reusable findings are the exact package/lock/hash record, standalone binding/help
observations, isolated APT extraction and preserved missing-dist package. No board,
route, pin-semantic map or independent geometry checker is qualified for reuse.
A portable rebuild/library snapshot, faithful converter behavior and meaningful
ERC remain unproved. Fixed-placement routing was never tested here.

Recommended PMO/PO question: after reviewing the partial evidence and executor
capture/sequence errors, should PO authorize a separately bounded correction of
the B environment packaging/capture workflow and a renewed smoke gate? This result
provides no routing evidence for adoption, candidate switching or placement changes.
No follow-up execution begins in this PR.
