# EDA-003F — strict via-clearance A/B intervention

**INTERVENTION_UNSAFE_REGRESSION.** The single predeclared intervention changed
via-to-segment repair's effective material target from **0.115 to 0.200 mm**.
B completed routing with zero required unrouted connections, but introduced
**two wrong-net copper components**. K1 terminated the experiment. A lower raw
DRC count and disappearance of the numeric signature cannot qualify an unsafe
route. **Does this justify another engineering cycle on tscircuit? NO.**

[Issue #69](https://github.com/ihsinoky/he-piantor-42/issues/69) was read completely
through the GitHub connector; it had zero comments. Preflight passed before
editing: requested cwd, clean tree, branch `eda-003f-clearance-intervention-ab`,
HEAD and merge-base with `origin/main` both
`15f3b222b1b0d2caaeda4c66befaa6364910d24e`, production **tscircuit 0.0.2646**.
Required reports and EDA-003C/D/E evidence were read. No applicable AGENTS.md
exists. All 86 protected tracked production and EDA-003B/C/D/E files retain
their preflight hashes.

## Trustworthy control A

Bun **1.2.22**, matching accepted EDA-003C, was downloaded into `/tmp` because
this Codespace lacked Bun. Its archive hash is recorded. A and B are separate
copies of the accepted exact-pinned **0.0.2748** manifest, lock, fixtures,
verifiers and dependency tree. Before patching, all **17,243 dependency files**
have identical tree fingerprints. Neither accepted dependencies nor production
files were modified. Independent clean installs can use the original committed
EDA-003C lock; no dependency re-resolution or override is involved.

The unchanged EDA-003C runner generated Main with strategy **3/5x**. The raw
A Circuit JSON SHA-256 is
`97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131`,
exactly matching accepted EDA-003C. Replayed checks reproduce all 71 records;
EDA-003D's unchanged geometric classifier reproduces all **54 cluster identities**,
including their locations, minima and primitive membership. The independent
physical verifier reports zero unrouted and zero wrong-net components; its
12 fault fixtures pass. A is a valid control, stronger than merely comparable
aggregate metrics.

## Predeclared intervention B

The exact installed `@tscircuit/capacity-autorouter 0.0.958` ESM bundle embeds
local `high-density-repair01` and global `high-density-repair03` implementations.
Source semantics and installed JavaScript AST inspection establish:

- Local `projectViaSegmentClearance`: via radius + trace radius +
  `RELAXED_TRACE_CLEARANCE` (0.100) + `CLEARANCE_SLACK` (0.015).
- Global `pushViaSegmentPair`: via radius + trace radius +
  (`RELAXED_DRC_OPTIONS.traceClearance ?? 0.100`) + slack (0.015).
- Slack adds positive overshoot to the nominal relaxed threshold **before**
  penetration and movement calculation. Effective A material target is 0.115 mm.

B changes only the clearance term in these **via-segment expressions** to
**0.185**, retaining slack **0.015**, so the effective target is **0.200 mm**.
For the representative 0.300 mm via copper radius and 0.100 mm trace half-width,
centerline targets are A **0.515 mm**, B **0.600 mm**. The target is not a
guarantee of final clearance after movement limits, rounding and later stages.

Changing the shared clearance constant/preset would also affect trace-to-trace
repair. Those shared settings remain unchanged. Global and joint Pipeline9
repair use the same live global helper. The source map contains an older
repair04 embedded helper, but exhaustive installed-function inspection finds
no separate live runtime copy of that helper. The joint solver imports the
branch portfolio solver from top-level `high-density-repair03`. Thus the
coherent patch has **two expression edits in one runtime file**,
`node_modules/@tscircuit/capacity-autorouter/dist/index.js`; one installed package,
two logical upstream source modules, **−17 bytes** net. No source-map or checker
file is changed. The installed map has 182,678 mapping lines against 64 minified
JS lines, so its positional mappings cannot place the edits; embedded source
semantics and exact installed expressions establish them instead.

[Definition](../hardware/tscircuit/qualification/eda-003f/evidence/intervention-definition.json)
and [patch manifest](../hardware/tscircuit/qualification/eda-003f/evidence/intervention-patch-manifest.json)
retain formulas, contexts, source hashes, exact replacements and before/after
artifact hashes. `apply-intervention.py` recreates B only from the exact stock
hash. No second candidate was defined or tried.

## Observed outcome and STOP

Both generators settled in approximately 91 seconds. Counts are stock error
records; they are not interchangeable with conservative physical conflicts.

| Metric | A | B | B − A |
| --- | ---: | ---: | ---: |
| Required unrouted | 0 | 0 | 0 |
| Wrong-net copper components | 0 | **2** | **+2** |
| Material DRC records | 71 | 49 | −22 |
| Conservative physical conflicts | 54 | Not entered | — |
| Pad-pad records | 1 | 3 | +2 |
| Pad-trace records | 19 | 24 | +5 |
| Via-trace records | 32 | 4 | −28 |
| Trace-clearance records | 17 | 16 | −1 |
| Via-hole/SMD-pad records | 2 | 2 | 0 |
| Approximately 0.115 mm signature records | 15 | 0 | −15 |
| Traces | 128 | 128 | 0 |
| Vias | 126 | 128 | +2 |
| Minimum reported via-trace material clearance (mm) | 0.084676659 | 0.141757277 | +0.057080618 |

B's independent physical copper graph finds these two multi-net components:

1. V3V3 / USB_DM / USB_DP / QSPI_SD3.
2. QSPI_SD0 / QSPI_SD2.

K1 was checked first and failed. Routing had settled and required unrouted
remained zero; those observations do not make the electrical graph safe.
The stock verifier result remains **FAIL**. B's generated material type/message
multiset matches the stock check replay, independently of record ordering.

Physical conflict-level comparison is **NOT ENTERED** because the required
safe-and-complete prerequisite failed. Removed/new physical counts, percentage
removed, net physical reduction and migration correspondences are **unknown**,
not zero. The evidence records REMOVED/RETAINED/NEW/MOVED/UNMATCHED as null with
the K1 reason. **Zero physical conflicts have been demonstrated fixed.**
Signature disappearance does not establish absence of equivalent migrated
errors or overall severity improvement; the new shorts establish an electrical
regression. No B confirmation run was performed or authorized for this unsafe
result. Exactly one A and one B generator process ran. Failure was preserved;
there was no further repair, tuning or attribution investigation.

## Cost and backend decision

The policy could be upstream-general, but this literal/minified-bundle patch is
an experiment, not an upstream-ready repair. An upstream solution would need
design-rule propagation and topology-preserving movement. A full representative
routing regression is feasible at roughly 90 seconds per run; a small regression
fixture remains unqualified. No reduction or upstream submission was attempted.
A permanent fork is unsuitable: the observed edit is unsafe, minified identities
change by release, and bundled helper coverage requires renewed inspection.
Small patch size does not establish low repair cost.

A retains 54 physical conflicts. B still has 49 material records across
pad-pad, pad-trace, trace-clearance, via-trace and SMD drill-intrusion families,
plus two new shorts; its physical cluster count was not measured after K1.
**Wing keepout and Main manufacturing export remain unresolved**, outside scope.
Do not advance to Wing because its work might be easier.

**NO**: the final bounded Main-clearance exploration reintroduces the higher
priority electrical failure. The evidence supports returning to backend
selection rather than another tscircuit engineering cycle.

**Next Human Gate question:** after PMO review of the K1 regression, should PO
choose alternate routing architecture/backend evaluation or tscircuit NO-GO?

## Reproduction and validation

With Bun 1.2.22 and the accepted EDA-003C dependencies available, prepare an
absent environment with `prepare.py`, then install using `npm ci --ignore-scripts`.
Alternatively copy the accepted installation into separate A/B directories as
recorded here. All experiment scripts are under
[EDA-003F](../hardware/tscircuit/qualification/eda-003f/).

```sh
python3 hardware/tscircuit/qualification/eda-003f/prepare.py /tmp/eda003f-fresh-a
cd /tmp/eda003f-fresh-a
npm ci --ignore-scripts
bun scripts/generate-revm1-routing-proof.tsx main 3 /tmp/eda003f-fresh-a-run
bun scripts/verify-revm1-routing-proof.ts /tmp/eda003f-fresh-a-run/circuit.json /tmp/eda003f-fresh-a-run/summary.json
```

From repository root, replay A checks with `capture-checks.mjs ENV RUN`, classify
with `classify-run.py RUN`, then collect with `measure.py RUN`. Validate A before
patching. Prepare B independently, apply `apply-intervention.py B_ENV`, and use
the same generator/verifier commands in B. Check K1 first and STOP on any
wrong-net component. `summarize-ab.py A_RUN B_RUN OUTPUT` records this terminal
failure without running either router or entering physical comparison.

Validation passes A raw/cluster reproduction, all 431 primitive observations
and 377 merge witnesses, independent physical/wrong-net verification, 12 verifier
fault fixtures, stock DRC replay, deterministic A clustering and comparison
calculations, JSON/gzip parsing, exact patch reconstruction, dependency-tree
isolation and `git diff --check`. Safety acceptance for B **fails K1**, as required
by the evidence. This is evidence validation, not a board PASS.

Production manifest/lock remain byte-identical, production **tscircuit 0.0.2646**
remains pinned in both, and accepted EDA-003B/C/D/E files retain all protected
hashes. Fixture/verifier bytes, placement, 48 × 44 mm outline, nets, strategy,
0.20 mm project rule, via/trace dimensions and stock checker are unchanged.
No external router, generated-data edit, permanent fork, production upgrade,
Wing/export investigation, manufacturing release or merge occurred. B's raw
Circuit JSON is retained as a lossless gzip; A reuses its byte-identical accepted
artifact. Disposable dependency copies remain in `/tmp` and are not committed.
