# Issue #228 — outline proposal, Phase A round 4

**Pending PO approval.** This directory is the working generator variant of
`../issue-198-final/`. The Wing input CSVs and geometry JSON remain there,
unchanged. `base.py` consumes the pure 2D construction in `outline.py`;
`details.py`, `verify.py` and `requirements.txt` are unchanged baseline copies.
No 3D files have been generated here.

Approval evidence:

- `17mm-outline-overlay.png`: both trays assembled, current #198 vs faint rejected round 3 vs solid round 4.
- `17mm-south-edge-zoom.png`: complete left thumb-to-pinky edge; right is mirrored.
- `17mm-north-center-zoom.png`: smooth north center and 12 × 4 mm open-top USB access.
- `17mm-outline.json`: exact 2D polygon coordinates and measurements.
- `17mm-shelf-profile.csv`: full 20,001-row shelf profile and nearest-point witnesses.
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

Round 4 uses one strictly convex quadratic Bézier per wing with tangent
R5 endpoint fillets. Curvature sign changes: 0; minimum sweep radius
1831.186829 mm. The round-2/3 north geometry and USB slot remain unchanged.
Quadratics use 512 chords; fillets use 128. Added area versus #198 is
2,981.489903 mm², within the 3,500 mm² guideline.

**Shelf conflict requires PMO/PO resolution:** maximum shelf is
16.801255 mm (sampling upper bound 16.804645 mm), above the 13 mm allowance.
A necessary convex-hull/wall lower bound is 15.643664 mm, so convexity,
unchanged pocket and 2 mm wall cannot meet 13 mm together. The report's
round-4 section supersedes round 3 for the south and details all conflicts.
This is a 2D review candidate, not an all-target pass or Phase B approval.

`round2_outline.py` and `round3_outline.py` preserve their original modules
byte for byte. Round 1 remains available through `round1_outline()`. The
JSON includes all historical polygons plus the active round-4 polygon,
curvature, shelf profile, area comparisons and distance witnesses. Complete
historical evidence/scripts remain in commits `d720f5e9` and `078b1e35`.
`base.py` consumes the active round-4 module without Phase B source changes.
Final USB alignment still belongs to the pending Fly seat rework.
