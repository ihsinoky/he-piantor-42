# Issue #228 — Phase B production case data

Consumes the ROUND 4 silhouette approved by the PO on 2026-11-12, including
its accepted shelf trade-off. `17mm/` is primary; `16mm/` is independently
fitted from its own Wing/pocket geometry. Phase A remains reproducible in
`../issue-228-outline/` and is not modified by this generator.

- `inputs/`: byte-identical copies of the #198 final Rev.3 CSVs and geometry.
- `generate.py`, `base.py`, `details.py`: full #198 interior design with the
  approved outline integrated. `details.py` changes only STL tessellation.
- `outline.py`: approved 17 mm coefficients; a per-input cached SLSQP
  minimum-area fit of the same quadratic/R5 family for the other pitch.
  The seed uses coefficients in that pitch's own envelope frame, never
  copied 17 mm XY coordinates. North controls follow each PCB's datums;
  the USB opening follows that outline and the unchanged seat datum.
- `native_curves.py`: exact quadratic Bézier and circular BRep edges.
  Analytic curves replace thousands of sampled edges; clipped endpoints
  project onto the same analytic curves at every height. See the report
  for measured deviation, rejected spline attempt and mesh refinement.
- `verify.py`: every #198 assertion retained, plus face/edge count reporting.
- `check_outline.py`: independent CSV reconstruction, containment, walls,
  curvature, dense shelf profiles and the 17 mm Phase A equality check.
- `check_3d.py`: exported STEP sections, USB height/material probes, BRep
  counts, and a top-view PNG rendered from the actual assembly tessellation.

Each pitch contains five printable parts (`tray-left`, `tray-right`,
`splice-1`, `splice-2`, `cable-rack`) in both STEP and STL, plus
`assembly.step`, `harness.step`, `storage-200mm.step`, `dimensions.json`,
`verification.json`, `exports-sha256.json`, `review.svg`,
`outline-check.json`, `shelf-profile.csv`, `3d-check.json` and
`assembled-top.png`. Assembly includes reference electronics, hardware and
harness envelopes; the storage STEP is the unchanged separate service-loop
reservation. Print only the five printable parts.

The pocket, all 15 fixing points, harness, rack, X=3.5 mm split, splice
plates, heights and daughterboard seat are unchanged. USB is provisional:
W12 × H4 mm, open top Z=11.2..15.2, at the existing X=-0.002 mm seat datum.
The Fly seat rework is a future task.

Reproduce from the checkout root, keeping every writable runtime path local:

```bash
mkdir -p .issue228-runtime/tmp .issue228-runtime/mplconfig
export TMPDIR="$PWD/.issue228-runtime/tmp"
export XDG_CACHE_HOME="$PWD/.issue228-runtime/cache"
export MPLCONFIGDIR="$PWD/.issue228-runtime/mplconfig"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
# Use the prepared local .issue228-runtime/cad-venv, or create a local venv
# and install requirements.txt into it. The prepared venv reads existing
# shared CAD packages and .issue228-runtime/pydeps through cad-runtime.pth.
CAD_PY="$PWD/.issue228-runtime/cad-venv/bin/python"
"$CAD_PY" hardware/case/issue-228-final/check_outline.py
for pitch in 17 16; do
  "$CAD_PY" hardware/case/issue-228-final/generate.py --pitch "$pitch"
  "$CAD_PY" hardware/case/issue-228-final/verify.py "hardware/case/issue-228-final/${pitch}mm"
  "$CAD_PY" hardware/case/issue-228-final/check_3d.py "$pitch"
done
```

`generate.py` updates its baseline export hashes; `check_3d.py` creates
additional audit artifacts and refreshes the hashes to cover those files. Base STEP caches stay under `.issue228-runtime/`; never use `/tmp`.
See [Phase B report](../../../.issue228-runtime/REPORT.md) for all numeric
checks, limitations and export inventory. This is nominal mechanical CAD
with the same component-envelope qualifications as #198.
