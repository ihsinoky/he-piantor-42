# EDA-004C — candidate B headless smoke requalification

**CONVERSION_BLOCKED — C1_DUPLICATE_GND_PAD_NET_LOSS.** The second physical
U_TX pin2 land loses its GND assignment at Circuit JSON → KiCad. KiCad reports
`shorting_items` between the retained local GND bond and that no-net land.
Experiment stopped before DSN export. Initial/fresh smoke routes **0/0**;
Main routes **0**. Terminal reporting is complete; technical qualification is
incomplete. Main remains unqualified, candidate B is not adopted, and no Human
Gate, fabrication or order is approved. USB NPTH remains **OPEN — PRE-ORDER DFM
REVIEW REQUIRED**.

[Issue #75](https://github.com/ihsinoky/he-piantor-42/issues/75), saved in
[authority](../hardware/tscircuit/qualification/eda-004c/evidence/authority.json),
and the PO's execution instruction authorize this bounded correction. It does
not authorize Main generation or conversion. [PR #76](https://github.com/ihsinoky/he-piantor-42/pull/76)
was opened as an early Draft after process-control validation. The
[previous report](alternate-physical-backend-main-qualification.md), its unchanged
EDA-004B evidence, the [plan](alternate-physical-backend-qualification-plan.md)
and [execution draft](alternate-physical-backend-main-qualification-issue-draft.md)
were inspected. Issue #75 supplies the current scope and classifications.

## Checkout and protection

The first tool observation found cwd `/workspaces/he-piantor-42`, correct origin,
branch `eda-004c-headless-smoke-requalification`, clean worktree and a single
worktree. HEAD and origin/main were both
`ca0c98db53ddd22ca2365246d67589e42fb7c9a5`; a read-only fetch left origin/main
unchanged. No applicable repository/ancestor AGENTS.md was found. The downloaded
kicadts source's AGENTS.md was also read; its sources were not edited.
[Initial observations](../hardware/tscircuit/qualification/eda-004c/evidence/initial-observations.json)
separate the clean initial observation from the later timed preflight, which
already contains this new untracked evidence root. No changes were discarded;
no reset, clean, stash or branch deletion occurred.

[Start protection](../hardware/tscircuit/qualification/eda-004c/evidence/protected-start.json)
and the final read-only validator cover every starting tracked file except the
two authorized status files. Production tscircuit **0.0.2646**, existing designs,
EDA-004B and earlier evidence/verifiers/decisions, architecture/interface/DFM,
workflow/CI and D-014–D-018 remain byte-identical. The new root, this report and
the synchronized status files are the only deliverables.

## Capture and permitted preparation corrections

[process.py](../hardware/tscircuit/qualification/eda-004c/process.py) registers
command/cwd/start UTC before launch, then records end UTC, numeric return code,
stdout/stderr and timeout. Available artifacts are copied and SHA-256 recorded
before process/content checks; nonzero status raises before the caller's next
process. Routing registration uses an fsync'd ledger before Popen, counts a
failed launch/timeout/crash/partial result, and requires initial-all-conditions-PASS
before confirmation. That routing path was never exercised with Freerouting.

[Control fault tests](../hardware/tscircuit/qualification/eda-004c/evidence/control-fault-tests.json)
confirm exit 7 prevents the downstream launch, partial raw survives, and raw
remains after an intentionally failed content assertion. Numeric failure, times,
stdout and stderr are preserved for the successful corrected test procedure.
A real preparation checker failure also prevented converter launch until fixed.

All disclosed preparation corrections happened before routing, under Issue #75:

- Initial wrapper used ROOT-relative paths for temporary fault evidence, causing
  ValueError. The temporary context removed the original files; only the observed
  traceback description and v1 source are retained. Original individual exit/time
  are unknown. The correction uses EVIDENCE-relative paths and repeats the test.
- Initial Git commit was blocked by sandbox read-only metadata; the premature PR
  command then found no commits. Authorized metadata escalation completed commit,
  push and Draft PR. These are executor management failures, not EDA failures.
- Executor assumed pcbPath coordinates were global. The first new raw showed
  anchor translation applied twice. Pinned core source inspection established the
  component-frame transform and implicit starting port; source was corrected.
- Initial input checker used the wrong internal-connection field. It exited 1,
  saved its failure, and did not invoke conversion. The field was corrected to
  the pinned schema's `source_port_ids`; raw input was unchanged.

[Correction records](../hardware/tscircuit/qualification/eda-004c/evidence/preparation-corrections.json),
v1 sources, diffs and both generated inputs are retained. Initial management
commands lacked individual timing capture; unknown values are not fabricated.
All subsequent EDA install/build/generate/convert/inspect processes use the wrapper.

## Fixed environment and regular source build

All installations were isolated under `/tmp/eda004c`. Production packages were
not touched. [Environment](../hardware/tscircuit/qualification/eda-004c/evidence/environment.json),
[source/build provenance](../hardware/tscircuit/qualification/eda-004c/evidence/source-build-provenance.json),
locks, resolved APT package hashes and per-process records retain exact inputs.

| Tool | Retained pin / observation |
| --- | --- |
| Frontend | EDA-003C accepted lock unchanged; tscircuit 0.0.2748, core 0.0.2097, props 0.0.689, circuit-json 0.0.516 |
| Bun | 1.2.22, official archive SHA-256 `4c446af1a01d7b40e1e11baebc352f9b2bfd12887e51b97dd3b59879cee2743a` |
| Node/npm | 24.21.0 / 11.19.0 |
| Converter | 0.0.230, original archive SHA-256 `fcd699c7686ecd08c9fffcfa40807e958fd2beed259aec3c1a4fd3fb7161fdb4`; converter lock unchanged |
| kicadts | 0.0.57, exact Git source `f3ea106bdc65ca901e9b23255ad3be0bd2a624ab`, upstream regular build |
| KiCad | 9.0.9~ubuntu24.04.1, original deb SHA-256 `b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0` |
| Freerouting | 2.5.0, JAR SHA-256 `f6f51bb02245e8e717f9359bd260cc9c5c0b1bc0acc8b7cb2cd5b8ffeb5de3c7`; one help-only invocation |
| Java | Microsoft OpenJDK 25.0.4.1+1-LTS, Microsoft-14951822 |
| Python | 3.12.3 for pcbnew; 3.14.2 for orchestration |
| OS | Ubuntu 24.04.5 LTS / x86_64; uname and os-release retained |

The pinned [package manifest](https://github.com/tscircuit/kicadts/blob/f3ea106bdc65ca901e9b23255ad3be0bd2a624ab/package.json)
and [prepare script](https://github.com/tscircuit/kicadts/blob/f3ea106bdc65ca901e9b23255ad3be0bd2a624ab/scripts/prepare-git-dependency.ts)
were inspected before execution. Prepare only builds from a path containing
node_modules; a source checkout takes its no-op branch. The authorized same-source
regular build used `npm install --ignore-scripts --package-lock-only`,
`npm ci --ignore-scripts`, then Bun `run build`, executing upstream
`tsup-node lib/index.ts --format esm --dts`. Build dependency resolutions and
integrities are frozen in the new build lock. Only the resulting unmodified
`dist` was attached to the exact locked Git dependency in the isolated converter.
Source Git diff was empty; only the new build lock was untracked. No source patch,
dependency substitution, release change or permanent fork was used. Converter
module load succeeded. Upstream reference/demo download scripts were not build
dependencies and were not executed.

KiCad was extracted with its resolved public APT dependencies, using an isolated
APT status/index/archive root. All 106 previous dependency archive hashes
match; the empty status also resolves the remaining dependency closure. `KICAD_STOCK_DATA_HOME` points to the extracted
stock resources, including schemas; CLI help/version and standalone pcbnew probes
had empty stderr. The public
[standalone binding](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/index.html)
exposed board load and DSN/SES overloads, but DSN/SES functions were never called.
This deprecated, version-contained binding is not an adopted architecture.
DISPLAY/WAYLAND_DISPLAY were removed for every process. Java used headless mode.
No GUI, virtual display, IPC, cloud or router API ran.

This is **not a completely qualified environment**. Embedded synthetic symbols
and footprints loaded, but KiCad reported missing configured `tscircuit`, `Device`
and `Custom` libraries. Stock resource and isolated config hashes are saved;
external library snapshots were not installed. Freerouting help warned about
screen-resolution detection; it was help only, not proof of GUI-disabled routing.
Existing npm lock/peer warnings are retained. No warning is silently credited PASS.

## Synthetic source and boundary findings

The EDA-004B fixture was copied to the new root, with
[pre-route diff](../hardware/tscircuit/qualification/eda-004c/evidence/fixture.diff)
and [reasons/correction](../hardware/tscircuit/qualification/eda-004c/evidence/fixture-change.json).
Changes save raw/hash before checking, make the local bond a single source-derived
2 mm segment, explicitly set material clearances to 0.20 mm, and rotate U_RX
90 degrees to exercise transforms. Core prepends the first GND land at (-5,0);
component-local endpoint (1,0) transforms to the second land (-3,0). Source pin
attributes define synthetic OUT/output, IN/input and passive GND, not real parts.

[Input reconciliation](../hardware/tscircuit/qualification/eda-004c/evidence/input-reconciliation.json)
checks the logical graph and internal duplicate-pin relation independently of
converter connectivity labels. It identifies all five electrical lands, one
0.65 mm NPTH, the two oval plated drills, dimensions/plating/layers, component
anchors/rotations, 20 × 16 mm outline, two layers/1.2 mm and explicit rules.
Only one pcb_trace exists, sourced from LOCAL_BOND on top GND at 0.20 mm width;
stock global tracks, vias and pours are absent. Nonlocal SIG/GND remain unrouted.
Component centroids differ from placement anchors because of footprint extents;
that distinction is retained, not mistaken for placement loss. All raw warnings
are preserved. Defined source circuit checks pass; Main ERC is not established.

Conversion ran **once**, generating PCB/project/schematic raw before any boundary
acceptance check. Read-only pcbnew extraction and KiCad pre-route DRC/ERC captured
all outputs as one boundary-evaluation group. All completed before the STOP
decision; no experimental EDA process followed STOP.

[Boundary maps](../hardware/tscircuit/qualification/eda-004c/evidence/boundary-reconciliation.json)
compare identities and physical properties, not just counts. The coordinate map
is x=100+source x, y=100-source y; measurement tolerance is 0.000001 mm, not a
clearance relaxation. Square-pad rotations are physically equivalent modulo
90 degrees; vertical oval orientations and component rotations are checked.
KiCad's *.Cu pad masks are intersected with the actual two-layer stack.

| Observation | Result |
| --- | --- |
| Second U_TX pin2 at source (-3,0), KiCad (97,100) | **FAIL:** expected GND, actual empty net; physical land preserved but internal logical connection lost |
| Local GND bond | Net, layer, endpoints and 0.20 mm width retained; it touches the now no-net land |
| Other physical objects | Five electrical lands + NPTH, sizes, positions, oval drills, plating/layers, component rotation, outline and thickness reconcile |
| Explicit default netclass | 0.20 mm clearance/track width, 0.60/0.30 mm via retained; five explicit project rules reconcile |
| Full rule precedence / DSN rules | **NOT ENTERED / unqualified**; no full effective-rule PASS |
| KiCad DRC before routing | Two intentionally unrouted connections, one shorting_items error, one solder_mask_bridge error, two footprint-library warnings |
| Schematic semantics | **FAIL:** two Device:U_chip definitions share one identifier; all output/input pins become passive; source OUT/IN identity becomes ambiguous |
| KiCad synthetic ERC | Two pin_not_connected errors, 16 warnings including library/off-grid/endpoints; **ERC_UNQUALIFIED**, not meaningful ERC PASS |

The DRC short is specifically **GND versus an unassigned land**, not evidence of
an actual SIG–GND short or Main failure. It still fails faithful transfer and
cannot be waived. Geometry-count agreement and return code 0 of report-only
CLI commands do not mean acceptance. All 18 ERC and four DRC violation records
plus unconnected records are retained without exclusions.

[26 fault replays](../hardware/tscircuit/qualification/eda-004c/evidence/checker-fault-tests.json)
detect missing/duplicate lands, lost internal connection, wrong labels, geometry,
rotation, drill/plating/layer changes, local-copper changes, rule weakening and
output/output or passive semantic loss. These run on in-memory copies of saved
data, never repair/reconvert a board. A synthetic metadata-only positive control
checks the checker can pass its defined parity conditions. This is limited
per-object/circuit reconciliation. Full post-route physical island reconstruction,
independent geometric short/clearance checking and missing-via fault qualification
are **NOT ENTERED**. Router-reported completion is not used.

## Stop, attempts and unentered work

[Durable stop decision](../hardware/tscircuit/qualification/eda-004c/evidence/stop-decision.json)
records the first terminal boundary loss. The failed source-coordinate assumption
and checker schema field were allowed preparation errors; the observed converter
net/semantic loss and KiCad short were the technical STOP. No converter patch,
manual output net reassignment, library workaround, reroute or alternate candidate
was attempted after this finding.

[Attempt ledger](../hardware/tscircuit/qualification/eda-004c/evidence/attempt-ledger.json)
is empty for real routing: initial **0**, fresh **0**, Main **0**. Two frontend
renders (initial preparation error and corrected fixture), one converter invocation
and one Freerouting help invocation are distinguished from route attempts.
[Run-contract record](../hardware/tscircuit/qualification/eda-004c/evidence/run-contract.json)
and hash are explicitly **NOT ENTERED / not frozen for routing**. Timeout, pass,
thread, optimizer and routing command are null because the gate stopped before
selection; this post-STOP record cannot authorize launch. Source/rule hashes were
saved, but no claim of a completed pre-route contract is made.

KiCad→DSN, Freerouting→SES, SES→KiCad, post-route DRC/independent physical checks,
fresh recreation and both byte/normalized connection-shape reproducibility are
**NOT ENTERED**. All four required final-run metrics are null for initial and
confirmation, separate from observed pre-route errors. SMOKE_PASS is not claimed.
New raw JSON is exclusively EDA-004C evidence; EDA-004B's missing raw remains missing.

## Validation, effort and review

[validate.py](../hardware/tscircuit/qualification/eda-004c/validate.py) checks
starting protected hashes against actual bytes and the starting commit, exact
locks/pins, raw/process/artifact hashes, stop chronology, null acceptance metrics,
zero attempts, checker replay, docs/status links and scope. Existing EDA-004B's
16 reporting-fault tests are also retained and run; eight new reporting-fault
cases reject false PASS/zero/attempt/completion claims; its original validator has
historical branch-specific diff restrictions and is not modified to accept this
new scope. `node --check task/data/project-status.js` and `git diff --check` pass.
The first reporting validation failed because its no-route guard mistook the
JAR download command for a Java invocation. Its raw failure, v1 validator and
correction diff are retained; the guard now checks `-jar` invocations. This is
a post-STOP reporting correction and launches no EDA process. Reporting/fault
PASS never promotes the failed conversion to qualification PASS.

[Effort ledger](../hardware/tscircuit/qualification/eda-004c/evidence/effort-ledger.json)
separates a conservative AI continuous-session wall estimate, observed process
elapsed time and unobserved human/unattended time. Issue #75 remains within its
four-hour cap, including reporting/validation/PR completion. The original 16-hour
budget was not reset: EDA-004B records **0.286 h** estimated AI effort through its
historical checkpoint; its later reporting/review correction and human time were
not quantified in the final PR. Known cumulative estimate and nominal remaining
allowance are recorded separately; a measured total or exact remaining budget
cannot be inferred. Process elapsed overlaps active AI work and is not added as
engineer-hours; complete unattended elapsed and human effort remain null.

Current-HEAD engineering-ci is checked before Ready for Review. Unchanged path
filters run change detection and Engineering gate; layout, product KiCad and
firmware jobs are skipped for this evidence/status scope. Native-spike does not
match this root/report. CI validates PR hygiene, not smoke routing/ERC/DRC.
The final PR body and [CI record](../hardware/tscircuit/qualification/eda-004c/evidence/ci-record.json)
identify the actual reviewed HEAD and results. No merge/auto-merge or Human Gate
decision is performed. PMO/PO reviews this conversion STOP and owns any next work.
