#!/usr/bin/env bash
set -euo pipefail
root="$(git --git-dir=.issue248-runtime/git rev-parse --show-toplevel)"
cd "$root"
export TMPDIR="$root/.issue248-runtime" PYTHONDONTWRITEBYTECODE=1 OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2
export MPLCONFIGDIR="$TMPDIR/mpl" XDG_CACHE_HOME="$TMPDIR/cache"
cad_python="${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}"
tree=hardware/case/issue-248-phaseb
"$cad_python" "$tree/cache_sources.py"
"$cad_python" "$tree/verify_pinmap.py"
pitches=("$@")
if ((${#pitches[@]} == 0)); then pitches=(17 16); fi
for pitch in "${pitches[@]}"; do
  for stage in build restore_floor finalize_geometry blend remake_joints tune_hardware regularize_shell finalize_geometry rebuild_splice_boss seam audit retention_check metrology qualify_lengths caps_only local_measures export drawings verify_exports witnesses shell_diagnostics tuning_blockers verify_hardware; do
    if [[ "$stage" == metrology ]]; then
      # Separate processes bound OCCT memory and retain each completed audit.
      # caps_only below supplies the independent certified cap check.
      for section in length usb service invariants; do
        if [[ "$section" == service ]]; then
          for side in left right; do SERVICE_SIDE="$side" "$cad_python" "$tree/metrology.py" "$pitch" service; done
        else "$cad_python" "$tree/metrology.py" "$pitch" "$section"; fi
      done
    elif [[ "$stage" == audit ]]; then
      while true; do
        if "$cad_python" "$tree/audit.py" "$pitch"; then break; else code=$?; [[ "$code" == 75 ]] || exit "$code"; fi
      done
    else
      "$cad_python" "$tree/$stage.py" "$pitch"
    fi
  done
done
"$cad_python" "$tree/report.py"
"$cad_python" "$tree/verify_package.py"
