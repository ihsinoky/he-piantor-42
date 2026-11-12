# Issue #228 — outline proposal, Phase A round 2

**Pending PO approval.** This directory is the working generator variant of
`../issue-198-final/`. The Wing input CSVs and geometry JSON remain there,
unchanged. `base.py` consumes the pure 2D construction in `outline.py`;
`details.py`, `verify.py` and `requirements.txt` are unchanged baseline copies.
No 3D files have been generated here.

Approval evidence:

- `17mm-outline-overlay.png`: both trays assembled, current #198 vs faint rejected round 1 vs round 2.
- `17mm-south-edge-zoom.png`: complete left thumb-to-pinky edge; right is mirrored.
- `17mm-north-center-zoom.png`: smooth north center and 12 × 4 mm open-top USB access.
- `17mm-outline.json`: exact 2D polygon coordinates and measurements.
- [Phase A report](../../../.issue228-runtime/REPORT.md).

Recreate ONLY the 2D evidence from the checkout root:

```bash
mkdir -p .issue228-runtime/tmp
TMPDIR="$PWD/.issue228-runtime/tmp" PYTHONDONTWRITEBYTECODE=1 \
  /home/hatch/workspace/tools/cad-venv/bin/python -m pip install \
  --target .issue228-runtime/pydeps --no-cache-dir \
  -r hardware/case/issue-228-outline/requirements-phase-a.txt
TMPDIR="$PWD/.issue228-runtime/tmp" \
  XDG_CACHE_HOME="$PWD/.issue228-runtime/cache" \
  MPLCONFIGDIR="$PWD/.issue228-runtime/mplconfig" \
  PYTHONPATH="$PWD/.issue228-runtime/pydeps" PYTHONDONTWRITEBYTECODE=1 \
  /home/hatch/workspace/tools/cad-venv/bin/python \
  hardware/case/issue-228-outline/phase_a.py
```

The 2D script uses the existing #198 17mm dimensions for the unchanged
Main/UDB geometry and independently checks both Wing polygons against the
original CSVs and recorded transforms. It reconstructs the exact pocket
algorithm and includes the unchanged floor splice reinforcement footprints.
It imports no CAD code and calls neither `generate.py` nor `verify.py`.

After PO approval and a separate Phase B dispatch, use this directory's
`generate.py` (defaults already point at the unchanged #198 inputs).
The new outline source participates in cache invalidation and input hashes;
base STEP caches now stay under `.issue228-runtime/`.
See the report for the required Phase B checks and limitations.

Round 2 uses one tangent cubic Bezier per south run and one quadratic
Bezier across the north. All spans use 512 chords, shared with Phase B.
The report’s round-2 section supersedes historical round-1 design/numbers.
`base.py` also consumes the shared extended north USB opening; final port
alignment belongs to the pending Fly seat rework.
