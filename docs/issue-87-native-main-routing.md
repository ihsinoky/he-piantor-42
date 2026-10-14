# Issue #87 — fixed Main routing qualification

<a id="resume-01"></a>
## Latest: limited resume and utilization-interruption recovery

- **Established:** the authorized DSN repair restores exactly one `smd_smd` numeric token per input from **0.05 to0.20 mm**. Separate AST/byte comparison passes for small/Main. Public fixed-JAR readback confirms both-layer effective matrix values, NC/required-net class relationships and unchanged other loaded objects. Individual Main DSN/input reconciliation passes.
- **Actual trials:** small **1 — PASS WITH SCOPE**; Main initial **1 — incomplete, run contract unqualified**; confirmation **0 — NOT ENTERED**. Old two DSN exports remain preparation, not route attempts. No new route was launched during recovery.
- **Terminal result:** **ROUTING_BLOCKED / MAIN_OUTPUT_INCOMPLETE / RUN_CONTRACT_UNQUALIFIED / MAIN_UNQUALIFIED**. The existing Main wrapper exited0 at **2026-10-14 21:41:53.512901 UTC**, with a saved SES and final router **35 incomplete connections**. Logs reach **512 passes**, despite declared100. This violates the intended run contract; the public settings-parser check did not prove the effective pass cap. The fixed-100-pass condition was not demonstrated. No general method or placement infeasibility is inferred.
- **Four metrics:** small return has **required unconnected0 / actual wrong-net contacts0 / targeted material violations0 / unexplained transfer changes0**. Main post-return physical metrics are **null / null / null / null (not measured)**; router35 incomplete and its reported clearance0 are not independent physical metrics. Under recovery caseC, the incomplete result/contract discrepancy triggers STOP before a new Main SES-import/DRC/graph experiment. Main input transfer parity is established; returned Main parity is unqualified.
- **Printing/product:** baseline61 known printing warnings and exact glyph uncertainty remain unresolved manufacturing work; no suppression/removal/exception. No new Main DRC was run, so no post-route warning/material PASS is claimed. USB NPTH DFM, product design, Wing, manufacturing/adoption/Gates remain open.
- **Time:** prior13min is carried forward. Resume work starts21:13:54 UTC; router continues unattended and finishes21:41:53.513. Recovery starts22:21:46 UTC. The uncertain utilization-wait boundary is represented by lower/upper totals in the [new effort ledger](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/effort-ledger.json); **the upper bound is used against6h**. Commit/push/report/CI add to both totals. No utilization reset is a time reset. A retrospective checkpoint is recorded, not a fabricated contemporaneous1h update.
- **Next PO decision:** PMO reviews the bounded DSN/small success, incomplete Main, runtime pass-cap failure and interruption/time uncertainty; PO decides whether any new scope/investment is justified. This report authorizes no retry, setting search, confirmation, adoption or product start. Same Draft [PR #88](https://github.com/ihsinoky/he-piantor-42/pull/88), no merge.

### Authority, start and recovery state

The current PO limited-resume instruction explicitly lifted the earlier STOP
only for bounded typed-rule restoration and the remaining Issue87 stages.
[Authority scope](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/authority.md).
At21:13:54 UTC the same branch/HEAD `47bb0e62f4e60b469139bd4584383e67f5de8eaf`
and clean worktree matched GitHub; 966 prior tracked code/evidence files were
frozen by hash. The existing KiCad/Java/router/geometry environment and previous
Main parity/actual-gap/via proofs were reused. No unaffected PCB tests were rerun.

The later PO recovery instruction identifies the interruption as a Codex
utilization limit. At22:21:46 UTC cwd/branch/HEAD were unchanged; uncommitted
resume code, raw logs, generated objects and temporary environment were preserved.
No checkout/reset/clean or environment rebuild occurred. GitHub still showed the
same open Draft PR and HEAD. The completed original wrapper handle37396 was
recovered, its command/start/end/input/output paths and raw hashes matched, and
its completion was returned without launching another process. The original
recorder has **no PID field**; no router/wrapper PID is invented or inferred from
a reused PID. Current sandbox process visibility alone is not treated as a
cross-namespace census.

Wrapper execution: **21:21:49.756590–21:41:53.512901 UTC**, elapsed1203.752s,
outer timeout1260s **not triggered**, exit0. Configured router job timeout1200s;
the duration is consistent with that bound, but no explicit final timeout/job
state was captured, so the precise reason for process termination is not certified.
The output is technically incomplete regardless. The first terminal disposition
was recorded on recovery at22:23:18.672066 UTC. The utilization interruption,
process exit and technical STOP are separate events.

### Bounded restoration and independent input reconciliation

`restore-clearance.py` uses the existing pinned sexpdata parser to establish
`unit um`, resolution10/um, one global `structure/rule` target with exactly50um,
then writes a separate corrected file by patching only that numeric token to200.
It records AST index path, line/column/byte span, units/values and both hashes.
Unexpected unit/resolution/count/value/location fails closed. Six such negative
cases were detected, and an unrelated literal50 remained unchanged. Raw DSNs
remain immutable at prior commit/path/hash, without needless new copies.

A separate checker imports no mutation code: raw/fixed AST differ at one allowed
value, and the byte diff is confined to `5`→`20` within50→200. No reserialization,
shape/net/placement change or other rule change occurs. Both ordinary and
netclass rules remain200um; the complete rule inventory contains no other layer/
type/class override. [Mutation and independent-diff records](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/README.md).

A small Java reader calls **public** HeadlessBoardManager and BoardRules getters
from the unmodified, hash-verified2.1.0 JAR. It loads raw and corrected DSNs
without routing. Exactly two matrix entries change: F.Cu/B.Cu smd–smd .05→.20mm;
all other loaded pins/nets/shapes/obstacles/traces/widths are identical. All actual
non-sentinel class pairs are>=.20mm. Sentinel `null` class0 has0 entries and is
not used by any actual input pad, obstacle or track. Net-associated pins use
`kicad_default`, while NC pins use `smd`; the class override relationships are
observed in readback rather than assumed from the edited string.

Fixed official `Structure.set_clearance_rule` splits the type pair and assigns
the symmetric matrix on all layers; `Network` maps explicit netclass rules to
real items. Source inspection records and exact bytes are retained. No KiCad/
router internal source or JAR was changed, compiled as a replacement, or forked.
The inspector only compiles a small public-API caller.

Individual DSN reconciliation covers all49 component poses/PN values and197
physical pin geometries/net/NC memberships, including four shield13 variants and
both mechanical15 variants. Shape-sharing image aliases are identified explicitly;
original KiCad footprint/SourceID/electrical-role identity remains in the import
target. Rect/circle/oval geometry, both layers, complete outline edges, three USB
bond centerlines/width/net/layer, via600:300 definition and four NPTH layer
obstacles reconcile. The existing2nm numeric tolerance is unchanged and is not
a spacing waiver. Raw/fixed effective readback also matches each pad and obstacle.

DSN does not serialize all native KiCad information. Thickness1.2mm, print/paste/
mask/typed schematic and actual PTH drilling/annuli remain in the original board;
SES is imported into that board rather than used to replace it. Each .65mm NPTH
becomes a1.05mm circular obstacle on both layers (original hole plus .20mm radial
margin), and public readback confirms those obstacles. Plated drill geometry is
not independently encoded in the DSN outer-pad shapes; it remains in KiCad and
requires final hole/material checking. This is an explicit boundary, not silent
loss acceptance. Main post-return checking remains unperformed after its STOP.

### Small roundtrip and checker corrections

One small route process ran for5.437s. The fixture includes duplicate-number
required lands, existing local copper, an NC SMD, a PTH and NPTH. Its SES imports
through the public API into the original board copy. All nonroute native PCB
semantics (including physical drills/NC and other retained information) match,
KiCad DRC/unconnected are0, and the independent actual pad/track/layer graph has
no required disconnection or wrong-net contact. All four acceptance metrics are0
**within this fixture only**. The via positive/missing/short proof from the
previous epoch is reused; this tiny returned route contains no new via.

Two ordinary checker corrections preserve their original failures and old code:

- Standard Lisp sexpdata treats bare `Rect[T]Pad...` brackets as list syntax;
  Specctra treats them as identifier characters. The bounded checker quotes these
  known identifiers **in reader memory only**. Raw/fixed DSN bytes are untouched,
  and the independent fixed-JAR reader confirms the actual interpretation.
- A new junction splits the existing small local trace into two collinear
  segments. Comparing segment-record identity incorrectly reported a loss.
  Corrected verification requires complete original centerline coverage by
  same-width/layer/net returned copper; crossings or nearby tracks cannot hide a
  missing bond. Native nonroute parity and the independent graph/DRC still apply.
  No routing trial was repeated or expected geometry changed for this correction.

### Fixed Main initial and observed execution-contract failure

Before launch, raw/input/board/project/contract/JAR/Java/settings/code hashes,
command, passes100, routing thread1, optimizer threads0/disabled, neckdown off,
job timeout1200s and wrapper1260s were frozen. Public settings-parser inspection
returned those requested values. Seed was not exposed; the declared reproduction
strategy used fixed inputs/settings, one routing thread, no optimizer, fresh
process/config/temp and conditional semantic confirmation, without claiming bit
determinism. The prior budget allowed both bounded runs plus checking/reporting.

[Actual run contract](../hardware/kicad/qualification/issue-87-native-main-routing/resume-01/evidence/run-contract.json).
Corrected Main input SHA256:
`75b44553bf6c8cab8c7dba411ad83b11fd12b5416cd24055aa5b1a412fd54bb2`;
settings `3499c12f249de20b8eeae770e68b08b5518d4bc963bcb665df1fb4f48adc8181`;
returned partial SES
`75156694793b0aa7594dd0d310b228b2db9b755f429e01506801473a0e24e8e6`.

The requested100-pass cap was **not effective**: raw logs show pass100 at
21:26:39.837, pass101 at21:26:41.455 and pass512 at21:41:52.778. No executor
changed the command/input/settings or launched another trial. Nevertheless,
checking the public parsed field was insufficient to establish runtime cap
behavior. The executor's earlier “fixed100passes” progress statement therefore
needs this explicit limitation; it is not evidence that the actual trial honored
that cap. The exact runtime cause is unqualified; no speculative fix, further
router investigation/experiment or retry follows this result.

Main log also records internal maze-search NullPointerExceptions. A separate
asynchronous update-check network error appears under the restricted environment;
small post-return acceptance still passed. These diagnostics are retained and
are **not printing warnings**. Router-reported accumulated CPU/memory values are
not certified physical resource measurements. Final router connections35 and
reported clearance0 are telemetry, not independent acceptance.

The latest PO instruction's caseC explicitly applies to incomplete output. After
recovery established that result and the pass discrepancy, a new Main SES import/
DRC/graph run was not launched. Prepared import/inspection code is retained as
**unexecuted**; no “0”, PASS or successful post-return preservation is inferred
from its existence. Initial1 is consumed; confirmation0 and no fresh generation.
A valid fixed100-pass layout outcome and all four physical Main metrics remain
unqualified. No placement change, hand routing, setting exploration, additional
Main trial, manufacturer exception, product source/dependency/CI change or merge.

### Time and submission limits

Prior13min is charged. The continuous21:13:54→21:41:53.513 interval is charged in
full, including unattended router time; operator stop time is not known precisely.
Last observed pre-limit tool21:26:03 bounds the possible unattended tail at
0–15m50.513s, already included rather than added twice. The following
21:41:53.513→22:21:46 interval39m52.487s is a candidate utilization-wait interval
with both processing and recorded work stopped. Its uncertainty is retained:
lower total excludes it, **conservative upper charges it**, plus all current
recovery/report/commit/push/CI time. No convenient exclusion of the whole unknown
period is used to enforce the cap. Final PR observation supplies later totals;
final-response seconds and exact interruption boundaries remain measurement limits.
The1h checkpoint is retrospective because no agent was available at its earlier
continuous-wall projection; it is labelled as such in the ledger.

Saved-evidence/static verification and final-head CI are submission checks only.
The final PR distinguishes management CI success, skipped engineering jobs and
technical Main failure. Earlier STOPs and raw artifacts remain immutable.

## Historical first Issue87 epoch — preserved original report

The following report describes only the earlier pre-resume epoch. Its statements
about zero routing attempts and unestablished DSN correction refer to that epoch;
they are retained as history and do not override the latest result above.


Submitted as Draft [PR #88](https://github.com/ihsinoky/he-piantor-42/pull/88);
review/merge and technical qualification remain separate.

- **Learned:** KiCad detects a real **0.10 mm** copper gap against the retained **0.20 mm** rule. Actual saved/reloaded PCB tests establish via connectivity, missing-via disconnection and wrong-net contact detection. However, both raw public DSN exports introduce **0.05 mm `smd_smd` clearance**. The fixed public API/configuration handoff remains **DSN_RULE_TRANSFER_UNQUALIFIED / MAIN_UNQUALIFIED**.
- **Attempts:** Main initial **0**, confirmation **0**, small DSN→router→SES roundtrip **0**. Two successful DSN exports are preparation, not roundtrip attempts. No router routing process, SES or routed Main exists.
- **First STOP:** stage C, rule reconciliation before any routing; **2026-10-14 20:52:37.127596 UTC**. The raw DSN relaxes a material condition; a supported configuration preserving it was not established. Individual DSN geometry, NC/duplicate/holes/local-copper reconciliation and SES return remain incomplete. This is neither a fixed-placement routing failure nor method-wide incapability.
- **Open printing/product work:** all **61 printing warnings** retained, exact glyph fidelity unqualified; USB NPTH pre-order DFM, product layout/power/pitch/Hall/cable, Wing/manufacturing and G1–G5 remain open. No manufacturing exception or adoption.
- **Time:** one session starts **2026-10-14 20:46:26 UTC**. Experiments stop after **6 min 11.128 s**; reporting/submission/CI time is additional and included in the [effort ledger](../hardware/kicad/qualification/issue-87-native-main-routing/evidence/effort-ledger.json). The closing observation is reported in the PR. No PO-wait interval or unattended exclusion; past budget compliance/remaining budget is not certified.
- **Next PO decision:** review this bounded STOP and decide whether to commission a specifically scoped, independently checked rule-transfer correction or hold further investment. No further experiment is authorized by this report. PMO reviews evidence; PO owns scope, investment, adoption and merge.

## Authority and retained inputs

Only [Issue #87](https://github.com/ihsinoky/he-piantor-42/issues/87), updated
20:40:34 UTC, and the current PO instruction authorize this run, with a new
six-hour elapsed-work cap including submission. [PR #86](https://github.com/ihsinoky/he-piantor-42/pull/86)
merged at 20:40:00 UTC as `49ebe146a586bf820a747b93951a29fe94f08623`.
It is an accepted historical STOP report, not retroactive authorization for the
prior scope excess or budget reinterpretation. [Its correction](native-main-routing-qualification.md)
is preserved. The concrete change in this evaluation is PO's exclusion of the
known printing/glyph issues as routing blockers, plus real-spacing/via/transport
qualification; electrical and material requirements remain fixed.

Initial cwd `/workspaces/he-piantor-42`, branch `main`, that HEAD and clean
worktree were recorded. After fetch, origin/main was identical; new branch
`issue-87-native-main-routing` was created. No existing changes were discarded.
Repository governance/development workflow, Dashboard rules and required reports,
plan, contracts and saved code were read. No applicable repository AGENTS.md was
found outside unrelated installed dependencies.

[Reuse hashes](../hardware/kicad/qualification/issue-87-native-main-routing/evidence/reuse-hashes.json)
identify commit/path/hash of retained resume-02 contracts, code, libraries and
artifacts. Saved PCB/project/schematic/netlist/snapshot hashes match their capture
records; main-contract-v2 is `edf053ba8d472408cf04b5583debf5a38ca718aeb68ce739f70c568d512d8246`.
The saved unrouted PCB is `46676e57e9618940a33c5e298244e97aaec61498a87aa7c58a264e444fc71e20`,
project `a5bc2aea160cc9a8b3035f77f0167c26a1de7ffdb749740c94fb7a9e9a3c87d5`.
The five immutable source/transitive/isolated-lock files were individually
rechecked against `b84585ecc2cf32000285bbf389d9fea255436980`:
[hashes](../hardware/kicad/qualification/issue-87-native-main-routing/evidence/immutable-inputs.json).
No old routed copper or old resume permission was reused.

Fixed scope: 49 components / 37 nets / 197 physical lands (167 required, 30 NC),
2 NPTH, 48×44 mm, strategy-3 placement/rotation, 2 copper layers, thickness
1.2 mm, width/spacing 0.20 mm, via 0.60/0.30 mm and source USB shield copper.
Counts supplement individual comparisons. Production tscircuit 0.0.2646 and
product source, dependencies, CI experimental conditions and D-014–18 are unchanged.

## Results and first terminal gate

| Stage | Evidence and actual scope |
| --- | --- |
| A: reuse | Saved native artifacts reused after hash check. Separate-process board read and original independent circuit/PCB checker pass all existing individual comparisons. No Main regeneration was necessary. |
| A: ERC/DRC | New raw ERC: **0 violations**. DRC: **61 known printing warnings** (44 text_height, 12 silk_overlap, 5 silk_over_copper); **127 pre-route unconnected items**, expected and retained. No additional baseline violations. Printing remains visible and no severity/rule/geometry suppression was applied. |
| B: effective clearance | A test copy of Main receives two 0.20 mm parallel tracks, center distance 0.30 mm; edge gap 0.10 mm. KiCad reports the exact pair's UUIDs as `clearance`, required 0.2000 / actual 0.1000 mm. Original project bytes unchanged. This proves this actual track-to-track violation, not every possible spacing class. |
| B: physical graph | Three tiny native PCBs are publicly authored, saved and reloaded. F.Cu→through-via→B.Cu physically joins two required lands; removing the via yields two N islands despite overlapping F/B endpoints; adding N copper to OTHER produces an actual wrong-net short. Main baseline output is identical after factoring its graph into a callable helper. These are actual PCB tests, not the old synthetic data. |
| C: small handoff | Fixture contains duplicate pad number with local copper, NC SMD, PTH and NPTH; public DSN export succeeds. **Rule prerequisite fails before routing.** No complete small roundtrip or post-SES reconciliation. |
| C: Main handoff | Public DSN export succeeds and exhibits the same typed-rule failure. Full individual Main DSN geometry/net/NC/duplicate/hole/layer/local-bond comparison is **not completed**; no SES return exists. |
| D/E | **NOT ENTERED**. Initial/confirmation **0/0**; four routed acceptance metrics **null**, never zero/PASS. No route contract, Main timeout/passes/threads/seed or fresh confirmation is claimed. |

The gap detection is retained in [effective-spacing.json](../hardware/kicad/qualification/issue-87-native-main-routing/evidence/effective-spacing.json),
actual PCB graph tests in [via-checker-acceptance.json](../hardware/kicad/qualification/issue-87-native-main-routing/evidence/via-checker-acceptance.json).
All raw CLI output, actual test boards and readback snapshots are under the
[new evidence root](../hardware/kicad/qualification/issue-87-native-main-routing/README.md).

Both raw DSNs contain `(clearance 200)` and
`(clearance 50 (type smd_smd))`, with `(unit um)`.
The [fixed KiCad 9.0.9 export source](https://github.com/KiCad/kicad/blob/9.0.9/pcbnew/specctra_import_export/specctra_export.cpp#L1133-L1154)
explicitly computes typed pad clearance as default clearance divided by four;
its exposed ExportSpecctraDSN overloads accept a filename or BOARD/filename,
without a rule-table parameter. This is an observed typed-rule change, not
printing or font uncertainty.

The retained Freerouting v2.1.0 CLI document describes `-dr`, but the
[matching GlobalSettings source](https://github.com/freerouting/freerouting/blob/v2.1.0/src/main/java/app/freerouting/settings/GlobalSettings.java#L74-L79)
explicitly says its function is removed. The
[CLI implementation](https://github.com/freerouting/freerouting/blob/v2.1.0/src/main/java/app/freerouting/Freerouting.java#L309-L345)
loads the input and clones RouterSettings; the inspected
[RouterSettings](https://github.com/freerouting/freerouting/blob/v2.1.0/src/main/java/app/freerouting/settings/RouterSettings.java)
exposes no material-clearance override. RulesFile.read targets GuiBoardManager;
a GUI path is outside scope. `-dr` was not speculatively invoked. These bounded
observations do not prove every possible public integration is impossible.

At this point the fixed public export/configuration route had **not established
faithful rules**, so the executor applied the stage-C prerequisite STOP. No
weakened-rule route, generated-DSN normalization, custom Java integration, router
patch, version change or alternative-setting trial followed. A future small
rule-transfer bridge would need explicit scope and independent proof, rather
than treating this report as evidence that large implementation is necessary.
[Decision and transfer details](../hardware/kicad/qualification/issue-87-native-main-routing/evidence/transfer-rule-check.json).

## Environment, corrections and verification limits

The disappeared temporary KiCad environment was restored to `/tmp/issue87` with
the unchanged pinned installer. KiCad **9.0.9**, binary package hash
`b7e6d33867631dc44385067b703b4c39eadede2037a260790b19495fe17e43f0`;
all downloaded dependency package hashes and effective environment are retained.
Mutable APT dependency availability remains a reconstruction limitation.
No display or GUI was used. Existing frozen symbol/footprint libraries were reused;
compressed symbols were expanded under /tmp and registered in the working copy.
No historical library/evidence was edited or duplicated as a new authority.

Geometry uses Python **3.14.2**, Shapely **2.1.2**, NumPy **2.5.4**, exact old
wheel hashes; the binding uses system Python **3.12.3**. Freerouting **2.1.0** JAR
hash `2c07d58f75dac03782664081e7a58b41c25400d871a9fcf166a2ea6fe60d5def`
was re-downloaded and verified. Every saved Java **Microsoft 21.0.12+1-ms** file
hash matches the prior freeze. Only router **help** ran; its success is not a
route. Complete environment reconstruction and same-condition Main reproducibility
remain unqualified. New frontend installation and model reauthoring were avoided.

Preparation corrections preserve failures independently of the terminal gate:

- System Python venv creation failed because ensurepip was absent. The prior
  geometry lock targets host Python 3.14; using a separate host-Python geometry
  venv preserves those exact wheel hashes and leaves pcbnew on system Python.
- First small fixture creation passed the generic result of `PAD.GetParent()`
  into `PAD(FOOTPRINT*)`, causing a public SWIG type error. Selecting the typed
  FOOTPRINT from `BOARD.GetFootprints()` fixes that call. The old script and raw
  failure remain; **no router had launched**, so this is a fixture-authoring
  correction, not a retried small routing trial.
- A read-only source fetch guessed RoutingJobScheduler's path and returned HTTP
  404. It provided no capability evidence and was not retried or generalized.
- The new Main checker only factors the existing copper graph and exposes its
  use for actual readback fixtures. No expected value or geometry contract changed.
  Existing per-land/role/shape/local-bond checks remain. Full routed-via Main and
  independent material-spacing acceptance remain untested.

Raw evidence integrity, old-file preservation, documentation links, JavaScript
syntax and Dashboard current-record substitution are submission checks, not
post-STOP EDA experiments. Final-head GitHub Actions results are reported in the
Draft PR, distinguishing successful management checks from skipped hardware jobs.
No backend adoption, product work, manufacturing output, Human Gate or merge.

## Time accounting

A single current session is charged from 20:46:26 UTC through the closing
submission observation; experiment STOP at 20:52:37.127596 UTC is **not** the
session end. Preparation, process waits, report, commit/push/PR and CI observation
are included. Process durations overlap the session and are not added again.
No interval was declared unattended; captured waits occurred during ongoing
implementation/review, and their wall time remains charged. Active engineer
minutes and historical human/review time cannot be independently measured.

The one-hour checkpoint would be due 21:46:26 UTC if still working. The original
new-frame deadline is 02:46:26 UTC next day, experiment cutoff 02:16:26 UTC to
reserve the final 30 minutes. The early technical STOP avoids spending the
remaining frame on unsupported scope. It does not certify historical compliance,
exact older remaining budget or any retrospective authorization.
