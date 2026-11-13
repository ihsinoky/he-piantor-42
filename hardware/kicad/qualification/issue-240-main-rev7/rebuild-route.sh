#!/bin/bash
# Reconstruct the studied electrical routing; all intermediate boards are scratch.
set -euo pipefail
cd "$(dirname "$0")/../../../.."
E=hardware/kicad/qualification/issue-240-main-rev7
T="$PWD/.issue240-runtime"
mkdir -p "$T/rebuild"
RP=${ROUTER_PYTHON:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3}
RS=${ROUTER_SCRIPT:-/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools/py_router/route.py}
CLI=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/bin/kicad-cli
py(){ bash "$E/env.sh" "$E/$1" "${@:2}"; }
route(){ KICAD_RIP_PREEXISTING=0 bash "$E/router-env.sh" "$RP" "$RS" "$@" --track-width .1 --escalation off --clearance .1 --via-size .6 --via-drill .3 --same-net-pad-clearance .15 --keep-thermal --keep-input-copper --no-stub-layer-swap --max-iterations 100000; }
drc(){ bash "$E/router-env.sh" "$CLI" pcb drc --format json --severity-all -o "$E/inspection/final/drc.json" "$E/inspection/final/main.kicad_pcb"; }
py build.py
py prepare-route.py
route "$T/route-input.kicad_pcb" "$T/route-outward10.kicad_pcb" --power-nets HALL_5V GND VBUS V5V2 --power-nets-widths .5 .3 .5 .5 > "$T/rebuild/route10.log" 2>&1
py finalize.py "$T/route-outward10.kicad_pcb"
py refill.py
drc > "$T/rebuild/drc10.log" 2>&1
py trim-debris.py
route "$PWD/$E/inspection/final/main.kicad_pcb" "$T/route-outward11.kicad_pcb" --power-nets HALL_5V GND VBUS V5V2 --power-nets-widths .5 .3 .5 .5 > "$T/rebuild/route11.log" 2>&1
py finalize.py "$T/route-outward11.kicad_pcb"
py refill.py
py widen-power.py
route "$PWD/$E/inspection/final/main.kicad_pcb" "$T/route-power13.kicad_pcb" --nets V5V2 --force-reroute --layers F.Cu In2.Cu B.Cu --power-nets V5V2 --power-nets-widths 1.0 > "$T/rebuild/power13.log" 2>&1
py finalize.py "$T/route-power13.kicad_pcb"
py refill.py
bash "$E/reproduce.sh"
