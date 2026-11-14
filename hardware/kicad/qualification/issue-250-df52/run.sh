#!/bin/bash
set -eu
ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
KR=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$KR/kicad/usr/lib/python3/dist-packages:$KR/geometry/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$KR/kicad/usr/lib/x86_64-linux-gnu:$KR/kicad/usr/lib/kicad"
export KICAD_STOCK_DATA_HOME="$KR/kicad/usr/share/kicad"
export KICAD_CLI="$KR/kicad/usr/bin/kicad-cli"
export TMPDIR="$ROOT/.issue250-runtime/tmp"
export XDG_CONFIG_HOME="$ROOT/.issue250-runtime/config" XDG_CACHE_HOME="$ROOT/.issue250-runtime/cache" XDG_DATA_HOME="$ROOT/.issue250-runtime/data" XDG_STATE_HOME="$ROOT/.issue250-runtime/state"
export PATH="$KR/kicad/usr/bin:$PATH"
unset DISPLAY WAYLAND_DISPLAY
exec "$@"
