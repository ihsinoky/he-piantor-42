#!/bin/bash
# Requalify saved candidates. Nonzero design findings remain in JSON; the final
# audit checks truthful evidence, not a fabricated all-gates-pass verdict.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
E=hardware/kicad/qualification/issue-250-df52
mkdir -p .issue250-runtime/tmp
run(){ bash "$E/run.sh" "$@"; }
for name in main wing-rev4-16mm-left wing-rev4-16mm-right wing-rev4-17mm-left wing-rev4-17mm-right; do
  args=()
  if [ "$name" = main ]; then args=(--schematic-parity); fi
  run kicad-cli pcb drc --format json --severity-all "${args[@]}" -o "$E/$name/drc.json" "$E/$name/main.kicad_pcb"
done
run kicad-cli sch erc --format json --severity-all -o "$E/main/erc.json" "$E/main/main.kicad_sch"
run kicad-cli sch export netlist --format kicadxml -o "$E/main/netlist-final.xml" "$E/main/main.kicad_sch"
run python3 "$E/verify.py" main wing-rev4-16mm-left wing-rev4-16mm-right wing-rev4-17mm-left wing-rev4-17mm-right
if [ "${1:-}" = --extract ]; then
  bash "$E/extract-main.sh"
  for name in wing-rev4-16mm-left wing-rev4-16mm-right wing-rev4-17mm-left wing-rev4-17mm-right; do run python3 "$E/extract-wing.py" "$name"; done
fi
run python3 "$E/verify-ground-model.py"
run python3 "$E/power-budget.py"
run python3 "$E/scope.py"
python3 "$E/audit-evidence.py"
