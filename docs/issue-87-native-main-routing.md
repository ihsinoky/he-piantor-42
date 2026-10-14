# Issue #87 — fixed Main routing qualification

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
