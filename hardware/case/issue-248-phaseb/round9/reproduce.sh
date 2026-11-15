#!/usr/bin/env bash
set -euo pipefail
root="$(git --git-dir=.issue248-runtime/git rev-parse --show-toplevel)"
cd "$root"
export TMPDIR="$root/.issue248-runtime" PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
export MPLCONFIGDIR="$TMPDIR/mpl" XDG_CACHE_HOME="$TMPDIR/cache"
cad_python="${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}"
tree=hardware/case/issue-248-phaseb
"$cad_python" "$tree/cache_sources.py"
python3 "$tree/recover_frozen_operands.py"
python3 "$tree/derive_routes_round6.py"
"$cad_python" "$tree/verify_pinmap.py"
pitches=("$@")
if ((${#pitches[@]} == 0)); then pitches=(17 16); fi
for pitch in "${pitches[@]}"; do bash "$tree/run_round6_pitch.sh" "$pitch"; done
"$cad_python" "$tree/report.py"
python3 "$tree/verify_round6_framework.py"
python3 "$tree/verify_package.py"
