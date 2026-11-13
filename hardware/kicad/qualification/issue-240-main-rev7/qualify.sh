#!/bin/bash
set -euo pipefail
E=hardware/kicad/qualification/issue-240-main-rev7
cli=/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/bin/kicad-cli
run(){ bash "$E/env.sh" "$E/common.py" "$@"; }
run snapshot python3 "$PWD/hardware/kicad/qualification/eda-004g/resume-02/read-pcb.py" "$PWD/$E/inspection/final/main.kicad_pcb" "$PWD/$E/inspection/final/snapshot.json"
run native-drc "$cli" pcb drc --format json --severity-all --exit-code-violations -o "$PWD/$E/inspection/final/drc.json" "$PWD/$E/inspection/final/main.kicad_pcb"
run native-erc "$cli" sch erc --format json --severity-all --exit-code-violations -o "$PWD/$E/schematic/erc-final.json" "$PWD/$E/schematic/main.kicad_sch"
run physical-connectivity python3 "$E/connectivity.py" final
run via-pad-audit python3 "$E/run-audit.py"
run positive-extraction python3 "$E/extract-power.py" final
run ground-extraction python3 "$E/extract-ground.py" final
bash "$E/env.sh" "$E/summarize-resistance.py"
bash "$E/env.sh" "$E/verify-ground-model.py"
bash "$E/env.sh" "$E/power-budget.py"
bash "$E/env.sh" "$E/geometry-diff.py"

bash "$E/env.sh" "$E/check-invariants.py"
