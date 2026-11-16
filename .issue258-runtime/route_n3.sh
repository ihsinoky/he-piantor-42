#!/bin/bash
export KICAD_CLI=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/bin/kicad-cli
export KRT_HOME=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/KiCadRoutingTools
PY=/home/hatch/workspace/projects/he-piantor-north/.issue253-runtime/krt-venv/bin/python
for var in 17mm-right 17mm-left 16mm-right 16mm-left; do
  d=n3-$var
  echo "=== $var ==="
  $PY $KRT_HOME/py_router/route.py $d/input.kicad_pcb $d/routed.kicad_pcb \
    --track-width 0.1 --power-nets HALL_5V GND --power-nets-widths 0.3 0.3 \
    --escalation off --clearance 0.1 --via-size 0.6 --via-drill 0.3 \
    --same-net-pad-clearance 0.15 > $d/route.log 2>&1
  echo "$var route exit $?"
  $KICAD_CLI pcb drc --output $d/drc.json --format json $d/routed.kicad_pcb > $d/drc.log 2>&1
  echo "$var drc exit $?"
done
echo ALLDONE
