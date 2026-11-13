#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")/../../.."
export TMPDIR="$PWD/.issue242-runtime/tmp" MPLCONFIGDIR="$PWD/.issue242-runtime/mpl" XDG_CACHE_HOME="$PWD/.issue242-runtime/cache" PYTHONDONTWRITEBYTECODE=1
mkdir -p "$TMPDIR" "$MPLCONFIGDIR" "$XDG_CACHE_HOME"
bash hardware/case/issue-242-bay-final/reproduce.sh 16
bash hardware/case/issue-242-bay-final/reproduce.sh 17
python3 hardware/case/issue-242-bay-final/mechanics.py
python3 hardware/case/issue-242-bay-final/drawings.py
python3 hardware/case/issue-242-bay-final/write-report.py
python3 hardware/case/issue-242-bay-final/finalize.py
python3 hardware/case/issue-242-bay-final/verify.py
