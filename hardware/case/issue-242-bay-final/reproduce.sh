#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export TMPDIR="$PWD/.issue242-runtime/tmp" MPLCONFIGDIR="$PWD/.issue242-runtime/mpl" PYTHONDONTWRITEBYTECODE=1 XDG_CACHE_HOME="$PWD/.issue242-runtime/cache"
mkdir -p "$TMPDIR" "$MPLCONFIGDIR"
export PYTHONPATH="${GEOMETRY_SITE:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-242-bay-final/study.py "${1:-17}" "${@:2}"

"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-242-bay-final/cover-solid.py "${1:-17}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-242-bay-final/check-invariants.py "${1:-17}"

"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-242-bay-final/binding.py "${1:-17}"

"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-242-bay-final/collision-map.py "${1:-17}"
