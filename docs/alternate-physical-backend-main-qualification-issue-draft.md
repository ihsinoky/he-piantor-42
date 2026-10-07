## Purpose and authority

Determine whether candidate B can faithfully transfer the fixed representative
Main into KiCad and achieve complete, safe, reproducible physical routing using
local headless Freerouting. This is an execution Issue **body draft for PO manual
creation**, not an existing Issue, an execution instruction or a backend adoption.
PO must create the Issue, confirm its number and give a subsequent instruction
before Codex starts. Do not assign a speculative number or create a Codex prompt
for this unnumbered draft.

Authority: [Issue #71 PO Human Gate comment](https://github.com/ihsinoky/he-piantor-42/issues/71#issuecomment-6046244229)
and D-018 in `docs/decisions.md`. The comment approves planning, ending additional
product-track exploration of the internal tscircuit router evaluated in EDA-003F,
candidate B first, two-workday budget and Kill Gates. Frontend retention remains
under evaluation; B is **not adopted**. EDA-003F remains
**INTERVENTION_UNSAFE_REGRESSION / K1** (two wrong-net components despite zero
required unrouted); B here denotes the alternate backend candidate, not that
unsafe intervention. See `docs/alternate-physical-backend-qualification-plan.md`.

Full Rev.M1 implementation, adoption, ordering and manufacturing release remain
blocked. G0A/G0B stay done; Codex does not reopen or pass Human Gates. D-014
historical frozen-fixture electrical authority, D-015/D-017 architecture/interface,
D-016 JITX physical backend NO-GO and production **tscircuit 0.0.2646** remain
unchanged. USB NPTH **OPEN — PRE-ORDER DFM REVIEW REQUIRED**, unselected production
pitch and all remaining product risks remain explicit.

## Scope

Candidate B only: native TSX -> genuinely unrouted Circuit JSON -> KiCad -> DSN
-> local headless Freerouting -> SES -> KiCad verification. Execute minimal
headless environment/interchange feasibility, faithful representative Main
transfer, meaningful ERC/independent graph parity and one initial Main routing
run. A fresh confirmation is permitted only after the initial run passes every
check. Small qualification-only source/configuration copies, existing converters,
narrow public-API glue and independently reviewed reconciliation are permitted
within the budget. Record every adaptation before relying on it.

Out of scope: Wing generation/keepout qualification; Gerber/Excellon/BOM/PnP or
other manufacturing investigations; maintenance source-change probe; full
frontend migration; extensive/product CI setup; candidate A/C attempts;
placement changes; routing retries/tuning; router internals modification;
private APIs; permanent forks; large custom interchange implementation; new
manufacturing exporter; dependency changes to production; ordering; upstream
contributions; changes to other Issues. Wing/export and maintenance work are
later separate PO-authorized work conditional on Main PASS and review.

## Exact baseline and invariants

Representative source commit:
**`b84585ecc2cf32000285bbf389d9fea255436980`** in `ihsinoky/he-piantor-42`.
Use `RepresentativeMain strategy={3}` at
`hardware/tscircuit/src/qualification/revm1-routing-proof.tsx`.

| Baseline input under hardware/tscircuit | SHA-256 |
| --- | --- |
| src/qualification/revm1-routing-proof.tsx | `0caa8e53eed298c3cf65715a15a1d671d91de715d4eb8f790eeb13e17a777008` |
| src/qualification/JstGh14.tsx | `ad23f75d53a917f8f43485b7fe887ff096ab0bdda244e3dc6e44fd73d93c787c` |
| src/qualification/native-support-footprints.tsx | `7b0efff9f5178b589c2ef7085625549bc4701ee24d2841ee7b46785921db55fe` |
| src/components/HallKey.tsx (transitive import only) | `0241daa3e2640bc870537ba3fa6571868858345f361456d80f73849dad32495c` |
| qualification/eda-003c/latest-stock/package-lock.json | `dec21cc020344ce8c8a769bd3ec92d99186546034974bcb702fc68f9dd7a455f` |

Use a qualification-only frontend installation from the accepted EDA-003C
isolated lock: tscircuit **0.0.2748**, core **0.0.2097**, props **0.0.689**,
circuit-json **0.0.516**, Bun **1.2.22**. Pin exact Node/npm and all transitive
resolutions. Production 0.0.2646 is separate and protected.

Keep all **49 components, 37 named nets, 167 required physical endpoints,
30 NC ports**, strategy-3 placement/rotations, **48 × 44 mm** outline,
**two copper layers / 1.2 mm / 0.20 mm** material clearance, **0.20 mm** trace
width, **0.60 mm** via copper / **0.30 mm** drill and effective source rules.
No product placement or architecture correction is authorized. This easier
non-product representative fixture does not qualify full Main/Wing or Rev.A.

EDA-003C/F control raw Main SHA-256:
`97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131`.
Use read-only for graph/placement/bond comparison; never as routing input.
Do not start from EDA-003B/F shorted copper or edit/strip accepted generated files.

## Protected files and allowed outputs

Do not alter any pre-existing design/source, accepted qualification source,
verifiers, raw evidence, historical report/verdict, production manifest/lock,
KiCad/JITX/reference artifacts, architecture/interface/DFM files or firmware/
mechanical/layout files. Preserve historical D-001–D-018 entries. New qualification
copies/scripts/manifests/evidence/report must live in a **new isolated directory**
under `hardware/tscircuit/qualification/` selected and recorded after the actual
Issue number exists; do not overwrite EDA-003B/C/D/E/F directories. Record all
original/isolated hashes. Status docs and Dashboard may be synchronized in the
same PR to report the actual terminal result; no heartbeat/automation/UI changes.

## Preflight and version-pinning gate

1. Read all applicable AGENTS.md, governance/workflow/decisions/project-status,
   Dashboard status, bounded qualification plan, this actual execution Issue and
   all its comments, the explicit Issue #71 PO comment, EDA-003B–F reports and
   final evidence, representative Main source/verifiers, and Rev.M1 architecture,
   interface and DFM policy. Verify execution Issue is open and PO instruction
   authorizes this exact scope. STOP on missing/conflicting authority.
2. Use cwd `/workspaces/he-piantor-42`; verify origin
   `https://github.com/ihsinoky/he-piantor-42`, clean worktree and the actual Issue
   branch/starting HEAD/origin-main supplied by PO **after Issue creation**.
   Those execution checkout values are not yet assigned. Fetch without reset,
   stash, clean or overwrite; STOP on mismatch/dirty worktree. Check baseline
   source hashes against the fixed commit above even if execution main has advanced.
3. Before installing/routing, record exact frontend lock/runtime, converter
   release/commit and package integrity, KiCad **9.0.9** build/package or container
   digest, standalone pcbnew/Python build, Freerouting release/JAR checksum and
   matching Java distribution/build, OS/architecture, install commands/URLs,
   symbol/footprint library snapshots, bridge/parser dependencies and hashes.
   Pin local project/netclass/custom rule/DSN/rules files, configs, locale/units,
   Java flags and environment paths. No `latest`/floating tags as pins, GUI state,
   unrecorded adjacent rules or cloud router. Record exact version/help output.
4. Predeclare and hash a run contract **before routing**: concrete wall-clock
   timeout, maximum passes, threads/seed or determinism strategy, optimizer and
   layer settings, all width/via/clearance tables, exact commands and config
   paths. These values must be selected in the created execution Issue/run
   contract before any run, with no repeated Main experiments to choose them.
   Unsupported settings, missing pins or unavailable packaging require STOP/new
   PO decision, not a silent tool/version/settings substitution.

Primary references (accessed 2026-10-07):
[KiCad 9.0.9 CLI manual](https://docs.kicad.org/9.0/en/cli/cli.html),
[pcbnew functions](https://docs.kicad.org/doxygen-python-9.0/namespacepcbnew.html),
[SWIG deprecation](https://dev-docs.kicad.org/en/apis-and-binding/pcbnew/index.html),
[IPC boundary](https://dev-docs.kicad.org/en/apis-and-binding/ipc-api/for-addon-developers/),
[converter public exports](https://github.com/tscircuit/circuit-json-to-kicad/blob/main/lib/index.ts),
[Freerouting CLI](https://github.com/freerouting/freerouting/blob/master/docs/command_line_arguments.md).
Feature/integration claims are not project PASS. KiCad CLI documents ERC/DRC
and CAM exports, **not DSN export/SES import**. Try only a small documented
standalone public `ExportSpecctraDSN(BOARD, file)` /
`ImportSpecctraSES(BOARD, file)` load/save bridge. pcbnew/SWIG is deprecated
and version-contained; this bridge is not a long-term adoption claim. KiCad
9/10 IPC requires a running GUI; do not assume it is GUI-free or switch major
versions/virtual-display automation to pass the headless gate.

## Execution sequence and transfer checks

**Stage 1 — minimal feasibility:** in the isolated pinned environment, one tiny
non-product roundtrip smoke fixture proves converter, DSN, local headless
Freerouting/SES and board reload without display, GUI, prompts or manual edits.
Exercise representative holes/plating, duplicate pads, local bond and meaningful
pin attributes. The smoke transport run is not a Main routing attempt or tuning
benchmark. STOP on headless failure, material loss, inadequate semantics or
extensive custom adapter work. Do not commence migration/CI before this gate.

**Stage 2 — faithful Main:** copy source into isolated dependency resolution and
record the source diff. Disable the current router using pinned public
`routingDisabled` or documented root `pcbRoutingDisabled`, checking actual
behavior. Keep logical `Wiring` traces as source net edges. Preserve exact
`USB_SHELL_BOND` source `pcbPath`, **17.00 mm** distinct GND bond copper,
including anchor-frame transform/endpoint attachment. If disabling routing also
suppresses it, use a small reviewed existing/public source/API bridge for this
exact bond only, or STOP. No hand-routed global signals or arbitrary retained
stock copper. Before DSN, inventory pads/bond and prove zero stock global
tracks/vias/pours/caches; nonlocal required connections must be genuinely unrouted.

Produce an independent source intent/geometry manifest and per-object maps.
Reconcile Circuit JSON -> KiCad -> DSN and SES -> KiCad for:

- Component/part/reference, pin aliases/numbers, endpoint/net identities, NC
  intent and internal logical connections, with no unexpected merges/additions.
- Every duplicate physical pad and separate GH return contact; local bonds
  remain physical obligations even when logical metadata shares a pin/net.
- Coordinates/rotations, origin/units/Y sign, pad shape/dimensions/radii,
  holes/drills/plating, annuli, layer membership/spans and 48 × 44 mm outline.
- Two layers, 1.2 mm, all existing keepouts (including explicit empty inventory),
  no-via-in-SMD-pad/hole/board constraints, 0.20 mm clearance and effective
  global/netclass/custom width/via rules at each boundary.

Counts alone are insufficient. Predeclare numerical reconciliation tolerances
as measurement resolution, never rule relaxation. Any unsupported object or
unexplained/material conversion loss is terminal; no silent data omission.

The TSX has **schematicDisabled true**. Assess electrical pin semantics against
verified part definitions/datasheets: input/output/bidirectional/power/passive,
NC, power domains and internal connections. A generated schematic or all-passive
symbol is not meaningful ERC. A minimal qualification-only semantic map may
use existing facilities without changing accepted graph/geometry. Missing or
guessed semantics -> **ERC_UNQUALIFIED / CONVERSION_BLOCKED**, not a waiver.
Require independent source/schematic/PCB endpoint/net parity and meaningful
KiCad ERC before Main routing. Parity between two equally wrong generated
artifacts cannot replace source comparison.

Review bounded independent KiCad geometry reconciliation before using it.
The existing Circuit JSON physical verifier is **not** a KiCad validator;
reuse its algorithms/fault cases only through a separately reviewed adaptation
with actual copper geometry, plating/transforms, unsupported-shape failure,
layer/via checks and injected short/missing-pad/missing-via/false-label/duplicate-
land/rule-loss cases. Stop if this needs large custom implementation or exceeds
budget. No reliance on router-reported connectivity/DRC alone.

**Stage 3 — one initial Main run:** after faithful transfer/meaningful ERC,
route once under the frozen contract. Import SES into a fresh copy of the
faithful unrouted KiCad input. Run KiCad DRC with full diagnostics/exclusions
recorded, schematic parity and independent electrical/geometry reconciliation.
Do not repair output, move components, retry or tune.

**Stage 4 — conditional confirmation:** only if all initial checks pass, recreate
the pinned environment and source/interchange from fresh state, with identical
settings and no prior SES/cache, and route Main once more. Compare raw and
normalized graph/geometry/rules, document all differences and rerun every check.
Material nondeterminism or failure terminates; no third attempt.

## Main Kill Gates, budget and acceptance

Required on both Main runs:

| Metric | Acceptance |
| --- | --- |
| Required unrouted, including every required physical land | **0** |
| Wrong-net copper components | **0** |
| Targeted material violations | **0** |
| Unexplained conversion loss | **0** |

Targeted violations include copper-pad/trace/via and NC-pad clearance,
hole/drill intrusion/clearance, layer transitions, board boundaries and all
applicable keepouts. Run KiCad checks plus independent source graph and actual
copper-island/short/clearance checks. Keep USB NPTH **OPEN — PRE-ORDER DFM REVIEW
REQUIRED** visible. No new exclusions or manufacturing exception may be approved
by the executor. Any routing/conversion-added USB conflict fails; if existing
source geometry triggers a KiCad conflict, retain it and STOP for PO disposition.
No CAM outputs or release investigation in this first Issue.

Aggregate maximum **two workdays**, counting preparation, installation,
interchange, semantic/geometry reconciliation, verifier adaptation, permitted
runs, analysis and reporting. Audit conservatively as **16 engineer-hours**.
Log task/operator/start/end/active minutes and cumulative effort, with unattended
process wall time separate. Checkpoints: P0 pin/run contract by 1 h; P1 headless
smoke/adapter feasibility by 4 h; P2 faithful Main/meaningful ERC/reconciliation
ready by 10 h; P3 initial run verified by 13 h; P4 conditional confirmation and
report within 16 h. Reserve reporting effort. Stop when a checkpoint cannot
proceed within its ceiling; unused budget does not permit extra routing attempts.

Permit **one initial Main route**, **one fresh confirmation only on initial
PASS**. Timeout/crash/partial result consumes that attempt; no resume/retry.
Stop immediately on material transfer loss, headless failure, shorts, incomplete
routing, targeted physical violations, non-reproducibility, excessive adapter/
router internals work or exceeded effort. Preserve first failure before any
further work. Candidate changes, placement changes, retries/tuning, conditions
or exceptions require a new PO decision.

## Evidence, validation and terminal classifications

Retain preflight/authority URLs; protected-byte manifest; tool/library/install/
settings hashes; effort ledger/checkpoint decisions; source-copy diff; semantic
coverage; conversion maps/warnings; raw unrouted Circuit JSON/KiCad/DSN and routed
SES/KiCad (lossless compression allowed with uncompressed hashes); commands,
stdout/stderr/exit status/timings, partial results and no-route provenance;
meaningful ERC/DRC reports; independent graph/geometry and fault-test results;
initial/conditional-confirmation differences, normalized comparison definition
and terminal first gate/reason. Evidence must show whether each stage ran or
was NOT ENTERED. No blank/zero metric may imply an unperformed check passed.

Final primary classification: **ENVIRONMENT_BLOCKED**, **CONVERSION_BLOCKED**
(including inadequate semantics), **ROUTING_BLOCKED** after faithful transfer,
**REPRODUCIBILITY_BLOCKED**, **BUDGET_OR_ADAPTER_BLOCKED**, or **MAIN_PASS** only
when both runs and all acceptance checks pass. Record additional failure categories,
ERC status and qualification completeness separately. BLOCKED is a valid completed
execution outcome; it does not mean routing qualified. Fixed-placement failure
is project-specific evidence, not general EDA/router incapability.

Validate new manifests/raw evidence integrity, protected byte identity, reviewed
reconciliation/fault checks, docs/evidence references, synchronized project-status
and Dashboard, `node --check task/data/project-status.js` and `git diff --check`.
Run existing applicable CI only; do not alter CI to mask unrelated failures.
CI success does not constitute Main/ERC/DRC/routing acceptance. Use one Issue
branch and early Draft PR linked to the actual Issue, complete the scoped checks,
then Ready for Review; do not merge or enable auto-merge.

## Review and subsequent work

PMO reviews scope/evidence/CI read-only and advises PO MERGE/HOLD. PO creates
Issues, instructs execution, owns candidate/exception/adoption/Human Gate and
merge decisions. Codex implements bounded work and records evidence only.

A B conversion failure may justify a separately approved minimal C trial.
A B routing failure after faithful transfer is not remedied merely by moving
the frontend to C with the same router. Do not automatically launch A/C.
Main PASS allows PO to consider later Wing/export and maintenance-probe Issues;
it does not authorize them or full migration/adoption/order.

Even on BLOCKED, retain reusable setup/pin manifests, source-intent/geometry maps,
semantic coverage, reviewed reconciliation and fault fixtures, boundary-specific
conversion losses and cost/run evidence. Reuse only demonstrated substeps with
compatible pins/limitations, never a failed board as a manufacturing package.
