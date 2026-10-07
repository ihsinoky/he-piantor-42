#!/usr/bin/env bash
# Reproduce only the recorded scripts-disabled module-load failure.
# No board generation, routing, automatic repair, or environment qualification.
set -euo pipefail
qualification_dir="$(cd -- "$(dirname -- "$0")" && pwd)"
reproduction_dir="${1:?Supply a NEW disposable directory under /tmp}"
case "$reproduction_dir" in /tmp/*) ;; *) echo 'Use a new /tmp directory' >&2; exit 2 ;; esac
test ! -e "$reproduction_dir"
mkdir -- "$reproduction_dir"
cp "$qualification_dir/converter-package.json" "$reproduction_dir/package.json"
cp "$qualification_dir/converter-package-lock.json" "$reproduction_dir/package-lock.json"
cd -- "$reproduction_dir"
test "$(node --version)" = v24.21.0
test "$(npm --version)" = 11.19.0
npm ci --ignore-scripts --cache "$reproduction_dir/npm-cache" > install.log 2>&1
set +e
node --input-type=module -e 'import "circuit-json-to-kicad"' > module-load.log 2>&1
module_status=$?
set -e
cat module-load.log
printf 'module-load exit=%s\n' "$module_status"
# Expected nonzero is a reproduced environment failure, never a qualification PASS.
test "$module_status" -ne 0
