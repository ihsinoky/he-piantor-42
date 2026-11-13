#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export TMPDIR="$PWD/.issue238-runtime/tmp" XDG_CACHE_HOME="$PWD/.issue238-runtime/cache" MPLCONFIGDIR="$PWD/.issue238-runtime/mpl"
export PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1
mkdir -p "$TMPDIR" "$XDG_CACHE_HOME" "$MPLCONFIGDIR"
export PYTHONPATH="${GEOMETRY_SITE:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages}${PYTHONPATH:+:$PYTHONPATH}"
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-238-bay-study/study.py
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" hardware/case/issue-238-bay-study/sections.py
"${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}" -c 'import sys,json; from pathlib import Path; p=Path("hardware/case/issue-238-bay-study"); sys.path.insert(0,str(p)); from drawings import draw; draw([json.loads((p/f"{i}mm-measurements.json").read_text()) for i in (16,17)],json.loads((p/"main-inventory.json").read_text()))'
python3 hardware/case/issue-238-bay-study/write_report.py
python3 hardware/case/issue-238-bay-study/verify.py
python3 hardware/case/issue-238-bay-study/manifest.py --write
