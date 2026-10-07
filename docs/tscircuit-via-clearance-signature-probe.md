# EDA-003E — recurring via-clearance signature fixability

**BACKEND_DECISION_REQUIRED.** The one authorized investigation cycle found a
source-supported numeric target: **0.10 + 0.015 = 0.115 mm**. This is a strong
correlation with the accepted signature, but does not demonstrate one localized,
economically fixable originating router defect. Stop at the first serious-pass
cost checkpoint. No reduction, upstream comparison or proof-of-fix was entered.

[Issue #67](https://github.com/ihsinoky/he-piantor-42/issues/67) and its complete
body were read through the GitHub connector (zero comments). Mandatory preflight
passed before editing: clean tree, requested cwd and branch, HEAD and merge-base
with origin/main both `c91fd8900f2ad9aa04cea1199abd01176472a7d2`, production
**tscircuit 0.0.2646**. No applicable AGENTS.md was found. Both accepted reports,
all required EDA-003D JSON, latest Main summary/raw JSON and isolated latest-stock
environment were read. Protected tracked file hashes are retained in
[preflight evidence](../hardware/tscircuit/qualification/eda-003e/evidence/preflight.json).

The deterministic extraction starts from accepted EDA-003D minimum material
gaps, filters only via-trace records within 0.0003 mm of 0.115, and independently
recomputes point-to-segment copper clearance. It reproduces the exact accepted
15 record IDs. The raw Circuit JSON's uncompressed SHA-256 remains
`97d51d510ecc7096261ad36297b48939609a14435a24926967b61197ed951131`.

| Signature population | Count |
| --- | ---: |
| Raw records | 15 |
| Distinct vias | 14 |
| Distinct PCB traces | 12 |
| Distinct net pairs | 14 |
| Conservative physical clusters touched | 16 |
| Top / bottom minimum witnesses | 8 / 7 |

Via `pcb_via_24` occurs in R044 and R046. R048 spans C033/C034, so 15 records
are not 15 independent faults. The retained count includes every accepted cluster
membership of each selected record, not only its minimum-gap witness. Via centers
span x −20.1023..18.0577 mm and y −17.5225..7.2383 mm: remote power/ground and
ADC routes as well as MCU escape copper. Minimum gaps are 0.114846549..0.115000000
mm. All minimum-witness traces have 0.20 mm width; all selected vias have 0.60 mm
copper diameter and 0.30 mm drill. Both sides are stock generated.
[Population evidence](../hardware/tscircuit/qualification/eda-003e/evidence/signature-population.json)
retains per-record IDs, clusters, both net identities, source trace/port identities,
via owner, geometry, drill/copper radii, closest segment and repeated-object counts.

The observed center-to-segment target is **0.30 + 0.10 + 0.115 = 0.515 mm**;
a valid 0.20 mm gap requires **0.600 mm**. Installed stock source maps expose
`high-density-repair01`'s `projectViaSegmentClearance`, with
`RELAXED_TRACE_CLEARANCE = 0.1` and `CLEARANCE_SLACK = 0.015`. They also expose
`high-density-repair03`'s `pushViaSegmentPair`, including a separately embedded
version under `@tscircuit/repair04`: both use a relaxed trace clearance plus the
same slack. These are exact source formulas, not numbers inferred solely from
final board geometry. Per-record attribution to an executed callback is still
unproved. The repeated lower target could be an attractor that repairs materially
different initial violations only partially.

[Numeric derivation](../hardware/tscircuit/qualification/eda-003e/evidence/numeric-derivation.json)
classifies that relationship **STRONG_CORRELATION**, and preserves inputs, formula,
expected result, every observed delta and source-map excerpts/hashes. It rejects
requested clearance alone, drill/copper-radius confusion, missing trace half-width,
router margin alone and annulus thickness. Local 0.001 mm rounding can perturb a
target, but cannot explain the 0.085 mm rule deficit. No generating grid/cell-size
relationship or common postprocessing offset was established; those remain UNKNOWN.

One observational stock run captured public Pipeline9 phase outputs. Bun is absent
in this Codespace session, so installed TypeScript transpiled the unchanged accepted
TSX copies into a disposable `/tmp` directory for Node. A wrapper around public
`Pipeline9._step` records results without changing solver arguments, results or
rules. Dependencies remain untouched. The captured SRJ retains 0.20 mm trace/pad
and trace/hole rules, 0.60 mm via copper and 0.30 mm drill; no finished selected
via/trace geometry exists in the initial obstacle input. Pipeline9 passes default
obstacle margin 0.15 mm when that SRJ field is absent. Individual inflated obstacle
geometry was not captured and its causal role remains unresolved.

Three selected cases cover remote VBUS/GND (R039), MCU QSPI (R044) and remote
ADC_C/GND (R055). Intermediate matching uses exact owner/conflicting connection
names and the closest via to the accepted final site. Before stitching that is a
**lineage candidate**, not a proved one-to-one ancestry through topology changes.
The observation does not establish the earliest internal instruction that fails.

| Boundary minimum gap (mm) | R039 | R044 | R055 |
| --- | ---: | ---: | ---: |
| Raw high-density output / via placement | 0.196160 | 0.006437 | 0.198230 |
| Local force improve | 0.156629 | −0.084996 | 0.114806 |
| Local repair | 0.156629 | −0.085000 | 0.115000 |
| Stitching | 0.106629 | −0.085000 | 0.115000 |
| Simplification / width / global force output | 0.084573 | −0.085000 | 0.101196 |
| Joint repair output | 0.114999 | 0.114847 | 0.114998 |
| Cleanup / length postprocessing | 0.114999 | 0.114847 | 0.114998 |

Negative intermediate values indicate copper overlap under the selected geometry
calculation; they are not additional accepted checker records. Raw high-density
output is the earliest **observed** invalid boundary for these lineage candidates.
R055 approaches the signature at local force improvement; the three final signature
gaps emerge together at joint repair output. Thus the final signature is already
present before Circuit JSON conversion. Neither copper diameter expansion during
conversion nor checker coordinate rounding explains these selected final failures.
The exact originating common defect and a single responsible callback remain UNKNOWN.
[Boundary evidence](../hardware/tscircuit/qualification/eda-003e/evidence/pipeline-boundary.json)
retains 30 observations with coordinates, widths, radii, gaps and source excerpts.

All 15 selected final gaps and via centers agree with accepted evidence within
`1e-10 mm`. The stock via checker reproduces all 15 errors against unmodified
0.20 mm on both accepted and captured JSON. The entire Node observation output is
**not byte-identical** to accepted Bun evidence and has changes outside this
population. No board-wide qualification or determinism conclusion is drawn from
this run; unrelated geometry was not investigated. Accepted EDA-003C repeatability
remains the qualification baseline. Captured snapshots are disposable; retained
hashes, geometry witnesses and capture tooling make the selected observations
reviewable and repeatable without replacing accepted raw evidence.

The [cost checkpoint](../hardware/tscircuit/qualification/eda-003e/evidence/cost-checkpoint.json)
was recorded after this first serious pass and before expansion. Confidence is high
in geometry and shared target correlation, low in one originating defect. Three
candidate responsibility modules implement local projection, global projection and
joint repair with embedded helpers. Six package/source contexts were inspected;
that does not establish how many packages would require changes. Fixing one target
constant is not yet shown to preserve route feasibility, remove the initial
violations or survive later transformations. Repair band and maintenance burden are
**UNKNOWN**. A stable small stock-routing regression is unqualified. Upstream and
temporary-fork viability are **unqualified**. No minimal fixture was attempted or
claimed unstable: the localization prerequisite was unmet at STOP. No upstream
search or patch evidence file is fabricated.

The selected population touches **16/54 = 29.63%** of Main physical clusters.
This is investigation scope, not expected repair coverage. **Zero conflicts have
been demonstrated fixed.** Even clearing every selected via/trace pair would not
necessarily clear every touched cluster, and cannot justify claims about all 54.
Other via clearances, MCU pad/trace and inter-route faults, same-net SMD drill
intrusions and NC-pad clearance remain independent unresolved risks. Wing keepout
and Main manufacturing acceptance remain accepted blockers outside this cycle.

Next Human Gate question: after PMO review, should PO choose alternate router/backend
evaluation or tscircuit NO-GO, or explicitly authorize another bounded callback
attribution/reduction cycle for the relaxed repair target? This investigation
requires no production upgrade, contribution, fork adoption or lower-priority work.

From the repository root, reproduce extraction/tests and, optionally, the one
observational routing process using installed EDA-003C dependencies:

```sh
python3 hardware/tscircuit/qualification/eda-003e/analyze.py
python3 hardware/tscircuit/qualification/eda-003e/test-analysis.py
node hardware/tscircuit/qualification/eda-003e/capture-pipeline.mjs /tmp/eda003e-fresh
node /tmp/eda003e-fresh/run.mjs
python3 hardware/tscircuit/qualification/eda-003e/collect-boundary.py /tmp/eda003e-fresh /tmp/eda003e-fresh-source
node hardware/tscircuit/qualification/eda-003e/check-selected.mjs /tmp/eda003e-fresh/circuit.json
python3 hardware/tscircuit/qualification/eda-003e/validate.py
```

Validation passes JSON parsing, deterministic extraction, numerical derivation and
boundary geometry consistency, four adversarial analysis tests, selected stock
checker replay, protected accepted-file hash checks and `git diff --check`.
It validates the evidence; Main clearance remains failed. Production
`hardware/tscircuit/package.json` and `package-lock.json` remain byte-identical,
including **tscircuit 0.0.2646**. All tracked EDA-003B/C/D files remain unchanged.
No full-board repair, rule relaxation, checker suppression, generated-data edit,
external router, upstream submission, permanent fork or Rev.M1 implementation occurred.

**BACKEND_DECISION_REQUIRED**
