#!/usr/bin/env bash
set -euo pipefail
root="$(git --git-dir=.issue248-runtime/git rev-parse --show-toplevel)"
cd "$root"
export TMPDIR="$root/.issue248-runtime" PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
export MPLCONFIGDIR="$TMPDIR/mpl" XDG_CACHE_HOME="$TMPDIR/cache"
cad_python="${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}"
tree=hardware/case/issue-248-phaseb
"$cad_python" "$tree/cache_sources.py"
pitches=("$@")
if ((${#pitches[@]} == 0)); then pitches=(17 16); fi
for pitch in "${pitches[@]}"; do
  for stage in build restore_floor finalize_geometry blend remake_joints tune_hardware regularize_shell finalize_geometry audit retention_check metrology qualify_lengths caps_only local_measures export drawings verify_exports witnesses shell_diagnostics tuning_blockers verify_hardware; do
    "$cad_python" "$tree/$stage.py" "$pitch"
  done
done
"$cad_python" "$tree/report.py"
