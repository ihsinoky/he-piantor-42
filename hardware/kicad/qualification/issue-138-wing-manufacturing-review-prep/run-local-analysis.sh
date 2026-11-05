#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../../../.."
task_runtime="$PWD/.issue138-runtime"
mkdir -p "$task_runtime"/{tmp,config,cache,data,state}
export TMPDIR="$task_runtime/tmp"
export PYTHONDONTWRITEBYTECODE=1
export XDG_CONFIG_HOME="$task_runtime/config"
export XDG_CACHE_HOME="$task_runtime/cache"
export XDG_DATA_HOME="$task_runtime/data"
export XDG_STATE_HOME="$task_runtime/state"
export OPENBLAS_NUM_THREADS=1
export PYTHONPATH="$PWD/.issue129-runtime/kicad/usr/lib/python3/dist-packages:$PWD/.issue129-runtime/geometry/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$PWD/.issue129-runtime/kicad/usr/lib/x86_64-linux-gnu:$PWD/.issue129-runtime/kicad/usr/lib/kicad"
task_evidence="hardware/kicad/qualification/issue-138-wing-manufacturing-review-prep"
/usr/bin/python3 "$task_evidence/inspect-boards.py"
/usr/bin/python3 "$task_evidence/evaluate-electrical.py"
/usr/bin/python3 "$task_evidence/estimate-dc-drop.py"
