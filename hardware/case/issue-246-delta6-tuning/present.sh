#!/bin/bash
# Regenerate drawings/report only from completed CAD evidence.
set -euo pipefail
cd "$(dirname "$0")/../../.."
export TMPDIR="$PWD/.issue246-runtime/tmp" MPLCONFIGDIR="$PWD/.issue246-runtime/mpl" XDG_CACHE_HOME="$PWD/.issue246-runtime/cache" PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR" "$MPLCONFIGDIR" "$XDG_CACHE_HOME"
python3 hardware/case/issue-246-delta6-tuning/drawings.py
python3 hardware/case/issue-246-delta6-tuning/finalize.py
python3 hardware/case/issue-246-delta6-tuning/verify.py
