#!/bin/bash
set -eu
TASK_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
KICAD_ROOT=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad
export TMPDIR="$TASK_ROOT/.issue240-runtime/tmp" PYTHONDONTWRITEBYTECODE=1
export XDG_CONFIG_HOME="$TASK_ROOT/.issue240-runtime/config" XDG_CACHE_HOME="$TASK_ROOT/.issue240-runtime/cache" XDG_DATA_HOME="$TASK_ROOT/.issue240-runtime/data" XDG_STATE_HOME="$TASK_ROOT/.issue240-runtime/state"
export PYTHONPATH="$KICAD_ROOT/usr/lib/python3/dist-packages:/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$KICAD_ROOT/usr/lib/x86_64-linux-gnu:$KICAD_ROOT/usr/lib/kicad"
export KICAD_STOCK_DATA_HOME="$KICAD_ROOT/usr/share/kicad" KICAD_CLI="$KICAD_ROOT/usr/bin/kicad-cli"
unset DISPLAY WAYLAND_DISPLAY
exec "$@"
