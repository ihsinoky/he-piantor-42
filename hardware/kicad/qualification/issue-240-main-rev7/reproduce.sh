#!/bin/bash
# Requalify the frozen study board. No CAM or manufacturing output.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
E=hardware/kicad/qualification/issue-240-main-rev7
R=.issue240-runtime
mkdir -p "$R/tmp" "$R/reproduction"
if [ -d "$E/processes" ]; then
  stamp=$(date -u +%Y%m%dT%H%M%S)
  mv "$E/processes" "$R/reproduction/processes-$stamp"
fi
bash "$E/qualify.sh"
bash "$E/env.sh" "$E/scope-summary.py"
bash "$E/env.sh" "$E/plot-data.py"
MPLCONFIGDIR="$PWD/$R/mpl" TMPDIR="$PWD/$R/tmp" /usr/bin/python3 "$E/draw.py"
python3 "$E/verify.py"
