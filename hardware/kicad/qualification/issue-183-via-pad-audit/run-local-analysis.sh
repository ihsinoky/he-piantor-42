#!/usr/bin/env bash
set -euo pipefail
E=$(cd "$(dirname "$0")" && pwd)
TASK_ROOT=$(cd "$E/../../../.." && pwd)
TASK_RUNTIME="$TASK_ROOT/.issue183-runtime"
BASE=${KICAD_RUNTIME_ROOT:-/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime}
mkdir -p "$TASK_RUNTIME"/{tmp,config,cache,data,state}
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$BASE/kicad/usr/lib/python3/dist-packages:$BASE/geometry/lib/python3.12/site-packages${PYTHONPATH:+:$PYTHONPATH}"
export LD_LIBRARY_PATH="$BASE/kicad/usr/lib/x86_64-linux-gnu:$BASE/kicad/usr/lib/kicad${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
export TMPDIR="$TASK_RUNTIME/tmp"
export XDG_CONFIG_HOME="$TASK_RUNTIME/config" XDG_CACHE_HOME="$TASK_RUNTIME/cache" XDG_DATA_HOME="$TASK_RUNTIME/data" XDG_STATE_HOME="$TASK_RUNTIME/state"
unset DISPLAY WAYLAND_DISPLAY
case ${1:-resume} in
  audit) /usr/bin/python3 "$E/audit.py" --runtime "$TASK_RUNTIME" ;;
  resume) /usr/bin/python3 "$E/feasibility.py" --runtime "$TASK_RUNTIME" ;;
  verify) /usr/bin/python3 "$E/verify.py" ;;
  check) /usr/bin/python3 "$E/check-move-candidates.py" --runtime "$TASK_RUNTIME" ;;
  render) /usr/bin/python3 "$E/render-overviews.py" --runtime "$TASK_RUNTIME" ;;
  *) echo 'Usage: run-local-analysis.sh [resume|audit|verify|check|render]' >&2;exit 2 ;;
esac
