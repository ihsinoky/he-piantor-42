#!/usr/bin/env bash
set -euo pipefail
root="$(cd "$(dirname "$0")/../../../.." && pwd)"
runtime=/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime
export TMPDIR="$root/../tmp" PYTHONDONTWRITEBYTECODE=1
export XDG_CONFIG_HOME="$root/../config" XDG_CACHE_HOME="$root/../cache" XDG_DATA_HOME="$root/../data" XDG_STATE_HOME="$root/../state"
export PYTHONPATH="$runtime/kicad/usr/lib/python3/dist-packages:$runtime/geometry/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$runtime/kicad/usr/lib/x86_64-linux-gnu:$runtime/kicad/usr/lib/kicad"
export KICAD_STOCK_DATA_HOME="$runtime/kicad/usr/share/kicad"
exec python3 "$@"
