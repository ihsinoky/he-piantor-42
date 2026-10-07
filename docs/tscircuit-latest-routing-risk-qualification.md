# EDA-003C — latest-stock routing risk qualification

**WRONG_NET_FIXED_LOWER_RISKS_REMAIN.** Stock **tscircuit 0.0.2748** produces
zero independent wrong-net copper components on the unchanged EDA-003B
strategy-3 Main/Wing fixture. Both boards have zero electrically required
unrouted connections. Both still fail physical validation. This bounded result
qualifies neither production adoption nor full Rev.M1 implementation.

The highest-risk Kill Gate is resolved for this representative fixture.
Under Issue #63 Case B, stop after Stage 1. No Stage 2 reduction, upstream-issue
comparison, root-cause investigation, repair estimate or disposable patch is
needed or performed. No lower-risk defect is fixed here.

## Authority, isolation and comparability

Mandatory preflight passed before edits at `506ad1828e1f7fa460fc5d10bbc2998f7c2997fc`,
on `eda-003c-latest-tscircuit-wrong-net-triage`, with a clean tree and the same
merge-base with `origin/main`. Issue #63 was read completely (zero comments).
The routing-proof report, project status, decisions, G0B freeze, production
manifest/lock, representative source, final EDA-003B classification/attempts/
Main/Wing summaries, physical verifier and generation/validation scripts were
read. No applicable repository AGENTS.md exists. EDA-003B remains accepted
historical **BLOCKED — ROUTING_CAUSED_PHYSICAL_ERRORS** evidence, unchanged.

Authoritative npm registry metadata queried on 2026-10-07 selected the `latest`
dist-tag **0.0.2748**, published 2026-10-06. The experiment exact-pins that
aggregate in a dedicated manifest/lock under
[`latest-stock`](../hardware/tscircuit/qualification/eda-003c/latest-stock/).
A clean `npm ci --ignore-scripts` installed the committed resolution. No fork,
override or upstream package patch was installed. npm's ordinary peer-resolution
warnings were retained as installation observations; no peer override was added.
Bun 1.2.22 runs TSX and the stock CLI; Node 24.21.0/npm 11.19.0 resolved the lock.

| Package | EDA-003B resolved | EDA-003C resolved |
| --- | --- | --- |
| tscircuit | 0.0.2646 | 0.0.2748 |
| @tscircuit/core | 0.0.1971 | 0.0.2097 |
| @tscircuit/capacity-autorouter | 0.0.919 | 0.0.958 |
| @tscircuit/checks | 0.0.208 | 0.0.241 |
| circuit-json | 0.0.499 | 0.0.516 |
| @tscircuit/cli | 0.1.2170 | 0.1.2253 |
| @tscircuit/props | 0.0.666 | 0.0.689 |

[`prepare.py`](../hardware/tscircuit/qualification/eda-003c/latest-stock/prepare.py)
copies the four original fixture files and existing verifiers beneath the
isolated dependency root. All fixture/verifier bytes remain identical. The
copied generation runner changes only its package-pin guard from production
0.0.2646 to experiment 0.0.2748: **mechanical environment adaptation**. There
are no TSX/API adaptations and no behavior-affecting design changes.

Main remains 48 × 44 mm, Wing 44 × 44 mm, two layers/1.2 mm, strategy 3/5x.
No placement, net, interface, component, topology, keepout or DRC rule is changed.
Generated placement, pads, mechanical/keepout geometry and source requirements
match EDA-003B exactly after the existing ID normalization. Stock now explicitly
emits `min_trace_to_hole_edge_clearance: 0.2` in `pcb_board`; EDA-003B omitted
that field while its hole check used 0.20 mm. This is recorded stock metadata
behavior, not a source rule relaxation. No generated Circuit JSON or Gerber
is modified. The five existing local source-authored ground bonds are retained.

## Stage 1 results

Counts below are records, not necessarily distinct violating pairs. Diagnostics
and independent connectivity findings are preserved separately. Both stock
router processes settled without timeout or autorouting error; completion alone
is insufficient for PASS.

| Metric | Main 003B | Main latest | Wing 003B | Wing latest |
| --- | ---: | ---: | ---: | ---: |
| Electrically required unrouted | 0 | 0 | 0 | 0 |
| Wrong-net copper components | 7 | **0** | 0 | **0** |
| Traces | 128 | 128 | 56 | 56 |
| Vias | 135 | 126 | 51 | 55 |
| Pad-pad errors | 2 | 1 | 0 | 0 |
| Pad-trace errors | 11 | 19 | 0 | 0 |
| Via-trace errors | 44 | 32 | 0 | 0 |
| Trace errors | 19 | 17 | 1 | 0 |
| Placement/routing-created errors | 0 | 2 | 12 | 18 |
| Via/keepout errors | 0 | 0 | 12 | 16 |
| Hole/trace errors | 0 | 0 | 1 | 0 |
| Autorouting errors | 0 | 0 | 0 | 0 |

The unchanged independent copper graph proves the absence of wrong-net joins
using physical geometry, rather than route endpoint annotations. Both latest
boards retain the baseline 167/69 required endpoints, 37/13 nets and 30/25 NC
ports. There are zero unassigned non-NC ports, unsupported copper geometries or
invalid layer transitions. All 12 verifier fault fixtures pass. Rechecking the
retained EDA-003B raw boards through the production stack reproduces its
accepted counts, including seven Main short components.

Main retains **71** material error records: 1 pad-pad, 19 pad-trace, 32
via-trace, 17 trace-clearance, and 2 via-hole/SMD-pad placement errors. The
latter involve U_FLASH.CS at approximately (3.55, 8.25) mm and J_USB.A4_B9 at
(−17.45, 14.96) mm. Wing retains **18** material error records: 16 via/keepout
records and 2 via-hole/SMD-pad errors at U_MUX_A.GND and U_MUX_C.GND. The keepout diagnostics omit via IDs, so their record count is not presented
as a distinct-via count. Thus stock routing still generates
behavior rejected by stock validation; the specific internal semantic cause
was not investigated after the Case B STOP. The prior Wing hole/trace error
is absent in this fixture's latest runs. Warnings remain in full summaries,
including missing courtyard/manufacturer/power/ground metadata and connector
access interpretation. No diagnostic is suppressed.

## Diagnostic manufacturing export and repeatability

The stock CLI successfully exports both boards. Wing passes the unchanged
manufacturing geometry verifier: 547 route segments, 55 vias on both copper
layers and in drill, 90 SMT lands, four plated lands, 16 connector lands,
outline and assembly rows survive. Supplier PnP orientation/procurement identity
limitations remain. This is diagnostic evidence, not a release package.

**Main's segment-survival check fails.** The unchanged manufacturing verifier
cannot find this exact expected draw in F_Cu:

- Circuit JSON trace `source_net_9_mst1_0`;
- top-layer 0.20 mm wire from (1.8, 3.4375) to (1.8, 3.671562) mm.

The export command succeeds, but the existing acceptance assertion does not.
This does not establish whether geometry was lost or represented differently;
that distinction is left for a separately authorized export qualification.
No compatibility adjustment, generated-data repair or exporter investigation
is performed to make the check pass. Its exit status and exact assertion are
retained. Export verification stops at the first failed assertion, so Main's
remaining manufacturing checks are not claimed to pass.

Two fresh generator processes per board use identical fixture/lock hashes.
The existing six-check metamorphic reproducibility verifier compares physical
geometry/connectivity and normalized copper/drill/BOM/PnP output. Repeat results
are PASS for both boards: raw Circuit JSON is byte-identical, and normalized
manufacturing outputs match. There is no material nondeterminism across the
two runs. Hashes and elapsed times are retained in the per-board evidence.
Reproducibility does
not waive physical errors or Main's failed manufacturing assertion.

## Stop, cost and Human Gate

Case B ends this issue at Stage 1. Stage 2/3 were **not entered**; there is no
minimal reproducer, likely-root-cause claim, upstream issue match, regression
fixture for a wrong-net repair, repair-scope estimate, upstream-fix viability
assessment or project/fork-patch viability assessment. Corresponding evidence
files are intentionally absent. The serious wrong-net root-cause-pass cost
checkpoint is inapplicable because that pass was not authorized by the result.

The cost decision is to stop: the unchanged representative fixture has no
observed latest-stock shorts, and another wrong-net investigation cycle has
no justified value here. Remaining clearance, via-pad, keepout and export
questions require separately scoped work, rather than expanding this issue.
The fixture result does not prove general absence of shorts in tscircuit.

**Next Human Gate question:** after PMO review, should the PO authorize a
separate latest-stock qualification of Main clearance/via-pad blockers,
followed by Wing keepout/via behavior and Main export-survival acceptance,
while retaining the production pin, or choose another backend path?

Production `hardware/tscircuit/package.json` and `package-lock.json` remain
byte-identical to baseline, with **tscircuit 0.0.2646**. There is no production
upgrade, upstream Issue/PR, permanent fork, full Rev.M1 implementation, merge,
order or manufacturing release. Historical EDA-003B, JITX, importer and G0B
records remain unchanged.

## Reproduction and evidence

With Bun 1.2.22, Node/npm and Python available:

```sh
cd hardware/tscircuit/qualification/eda-003c/latest-stock
npm ci --ignore-scripts
BUN=bun python3 screen.py /tmp/eda-003c-fresh
python3 collect.py /tmp/eda-003c-fresh
```

The screening driver retains physical-verifier exit 1 as a failed qualification,
and retains manufacturing-verifier exit 1 as an assertion failure; inspect its
logs as well as summaries. It does not infer PASS or a terminal classification.
The run uses only public stock circuit generation and stock CLI export.

[`evidence`](../hardware/tscircuit/qualification/eda-003c/evidence/) includes
preflight, authoritative npm metadata, exact versions, source comparability,
normalized generated-fixture comparison, baseline/latest metrics, both runs'
physical summaries/events, scope, manufacturing results, reproducibility and
terminal classification. Run-1 raw boards and export ZIPs are retained in
lossless gzip wrappers with uncompressed hashes. No second raw copy is needed
when normalized physical/manufacturing comparisons match. Read-only checks can
restore those bytes into `/tmp` and reuse the copied verifier scripts.

Validation: clean isolated install, four stock generations, independent physical/
wrong-net checks, 12 physical fault fixtures, scope, baseline verifier reuse,
and two six-check reproducibility comparisons completed. Wing manufacturing
geometry passes; Main fails the retained segment-survival assertion in both
runs. JSON parse, Python syntax, compressed-artifact integrity, production/
history byte checks and `git diff --check` pass. Physical verification remains
FAIL on both boards; this is the supported terminal classification, not a PASS.
