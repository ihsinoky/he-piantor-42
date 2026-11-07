#!/usr/bin/env bash
set -euo pipefail
study_dir="$(cd "$(dirname "$0")" && pwd)"
repo_root="$(cd "$study_dir/../../../.." && pwd)"
runtime_root="${KICAD_RUNTIME_PARENT:-/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime}"
study_scratch="${ISSUE196_SCRATCH:-$repo_root/../}"
mkdir -p "$study_scratch/tmp" "$study_scratch/config" "$study_scratch/cache" "$study_scratch/data" "$study_scratch/state"
export TMPDIR="$study_scratch/tmp" XDG_CONFIG_HOME="$study_scratch/config" XDG_CACHE_HOME="$study_scratch/cache" XDG_DATA_HOME="$study_scratch/data" XDG_STATE_HOME="$study_scratch/state"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONPATH="$runtime_root/kicad/usr/lib/python3/dist-packages:$runtime_root/geometry/lib/python3.12/site-packages"
export LD_LIBRARY_PATH="$runtime_root/kicad/usr/lib/x86_64-linux-gnu:$runtime_root/kicad/usr/lib/kicad"
exec python3 "$study_dir/analyze.py"
