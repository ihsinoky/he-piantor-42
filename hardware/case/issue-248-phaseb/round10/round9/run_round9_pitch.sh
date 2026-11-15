#!/usr/bin/env bash
set -euo pipefail
export TMPDIR="$PWD/.issue248-runtime" MPLCONFIGDIR="$PWD/.issue248-runtime/mpl" XDG_CACHE_HOME="$PWD/.issue248-runtime/cache" OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 PYTHONDONTWRITEBYTECODE=1
pitch="$1"
first="${2:-assemble_round9}"
started=false
py="${CAD_PYTHON:-/home/hatch/workspace/tools/cad-venv/bin/python}"
tree=hardware/case/issue-248-phaseb
for stage in assemble_round9 seam audit retention_check metrology qualify_lengths caps_only local_measures export drawings verify_exports witnesses shell_diagnostics tuning_blockers verify_hardware; do
 if [[ "$stage" == "$first" ]]; then started=true; fi
 if [[ "$started" == false ]]; then continue; fi
 echo "ROUND8 pitch=$pitch stage=$stage"
 if [[ "$stage" == audit ]]; then
  while true; do
   if "$py" "$tree/audit.py" "$pitch"; then break; else code=$?; [[ "$code" == 75 ]] || exit "$code"; fi
  done
 elif [[ "$stage" == metrology ]]; then
  for part in length usb service invariants; do
   if [[ "$part" == service ]]; then
    for side in left right; do SERVICE_SIDE="$side" "$py" "$tree/metrology.py" "$pitch" service; done
   else "$py" "$tree/metrology.py" "$pitch" "$part"; fi
  done
 else "$py" "$tree/$stage.py" "$pitch"; fi
 if [[ "$stage" == seam || "$stage" == audit || "$stage" == metrology || "$stage" == verify_hardware ]]; then
  git --git-dir=.issue248-runtime/git --work-tree=. add "$tree" ":(exclude)$tree/__pycache__"
  if ! git --git-dir=.issue248-runtime/git --work-tree=. diff --cached --quiet; then
   git --git-dir=.issue248-runtime/git --work-tree=. commit -m "Issue 248 round 9: checkpoint $pitch mm $stage evidence" > "$TMPDIR/round9/commit-$pitch-$stage.log"
  fi
 fi
done
