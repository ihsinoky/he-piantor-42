#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export TMPDIR="$PWD/.issue244-runtime/tmp" MPLCONFIGDIR="$PWD/.issue244-runtime/mpl" PYTHONDONTWRITEBYTECODE=1 XDG_CACHE_HOME="$PWD/.issue244-runtime/cache"
mkdir -p "$TMPDIR" "$MPLCONFIGDIR"
export PYTHONPATH="${GEOMETRY_SITE:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages}"
export HEIGHT_DELTA="${1:-6}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-244-height-search/study.py "${2:-17}" "${@:3}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-244-height-search/finish.py "${2:-17}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-244-height-search/check-invariants.py "${2:-17}"
