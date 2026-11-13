#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export TMPDIR="$PWD/.issue240-runtime/tmp" MPLCONFIGDIR="$PWD/.issue240-runtime/mpl" PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR" "$MPLCONFIGDIR"
export PYTHONPATH="${GEOMETRY_SITE:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-240-bay-cover/study.py "${1:-17}" "${@:2}"
