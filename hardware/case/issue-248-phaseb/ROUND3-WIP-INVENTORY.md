# Round 3 restart inventory

Starting checkpoint: 70023e4, runtime Git directory `.issue248-runtime/git`.

Kept the three interrupted generated 17 mm files: assembly-index.json, measurements.json and surface-plan.geojson. All 374 indexed BRep files exist in the runtime geometry17 cache and their SHA256 hashes match; the cache index equals the tracked assembly index. This is the seam-rule **build-stage checkpoint only**, not a qualified assembly. It predates floor restoration, geometry finishing, hardware tuning and all round-3 gates. The shorter measurements deliberately lack downstream-stage evidence; those stages must regenerate it. The unchanged tuning routes remain fitted at this checkpoint.

Python __pycache__ files are excluded. Runtime round3 contains rejected high-route and ongoing low-route optimization experiments, fields and diagnostic plots; none is adopted as qualified geometry. Prior tuning geometry and evidence remain frozen under tuning-round/ and runtime round3/tuning-geometry{16,17}.

Read REPORT.md, the original round-3 log brief, and current `gh issue view 248 --comments` on restart. The plate-boundary seam authorization is unchanged. All eight gates must be rerun for both pitches; no cached tuning PASS transfers to changed geometry.
