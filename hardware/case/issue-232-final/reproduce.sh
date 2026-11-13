#!/usr/bin/env bash
set -euo pipefail
TASK_ROOT=$(cd -- "$(dirname -- "$0")/../../.." && pwd)
cd "$TASK_ROOT"
CAD_PYTHON=${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}
GEOMETRY_SITE=${GEOMETRY_SITE:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages}
export PYTHONPATH="$GEOMETRY_SITE${PYTHONPATH:+:$PYTHONPATH}"
export TMPDIR="$TASK_ROOT/.issue232-runtime/tmp"
export XDG_CACHE_HOME="$TASK_ROOT/.issue232-runtime/cache"
export MPLCONFIGDIR="$TASK_ROOT/.issue232-runtime/mplconfig"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p "$TMPDIR" "$XDG_CACHE_HOME" "$MPLCONFIGDIR"
TREE=hardware/case/issue-232-final
for pitch in 16 17; do
  "$CAD_PYTHON" "$TREE/build.py" --pitch "$pitch"
  cp "$TREE/plate-package-notes.md" "$TREE/${pitch}mm/plate-package/NOTES.md"
  for side in left right; do
    cp "hardware/case/issue-230-mount-study/${pitch}mm-${side}/supports.csv" "$TREE/${pitch}mm/post-positions-${side}.csv"
  done
  "$CAD_PYTHON" "$TREE/check_invariants.py" "$pitch"
  "$CAD_PYTHON" "$TREE/check_plate.py" "$pitch"
  "$CAD_PYTHON" "$TREE/verify.py" "$pitch"
done
"$CAD_PYTHON" "$TREE/review.py"
"$CAD_PYTHON" "$TREE/report.py"
python3 "$TREE/manifest.py" --write
