#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export TMPDIR="$PWD/.issue246-runtime/tmp" MPLCONFIGDIR="$PWD/.issue246-runtime/mpl" PYTHONDONTWRITEBYTECODE=1 XDG_CACHE_HOME="$PWD/.issue246-runtime/cache"
mkdir -p "$TMPDIR" "$MPLCONFIGDIR"
export PYTHONPATH="${GEOMETRY_SITE:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages}"
export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
export HEIGHT_DELTA="${1:-6}"
args=("${@:3}")
audit_only=false
for arg in "${args[@]}"; do if [[ "$arg" == --audit-only ]]; then audit_only=true; fi; done
if ! "$audit_only"; then
  "${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-246-delta6-tuning/study.py "${2:-17}" --build-only
  "${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-246-delta6-tuning/study.py "${2:-17}" --export-only
fi
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-246-delta6-tuning/study.py "${2:-17}" --audit-only "${args[@]}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-246-delta6-tuning/finish.py "${2:-17}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-246-delta6-tuning/check-invariants.py "${2:-17}"

"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-246-delta6-tuning/service.py "${2:-17}"
python3 hardware/case/issue-246-delta6-tuning/evaluate.py
