#!/bin/bash
cd ~/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation
RT=~/workspace/projects/he-piantor-boards/.issue263-runtime/run
PY=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3
LOG=~/workspace/projects/he-piantor-boards/.issue263-runtime/roll-loop.log
: > $LOG
for i in 1 2 3 4 5 6; do
  $RT $PY route-main.py >> $LOG 2>&1
  RM=$(stat -c %Y main-rev8/routed.kicad_pcb)
  for t in 1 2 3; do
    $RT $PY audit-main.py >> $LOG 2>&1
    AM=$(stat -c %Y inspection/final/audit.json)
    [ "$AM" -ge "$RM" ] && break
    echo "attempt $i: audit stale (segfault?), retry $t" >> $LOG
  done
  U=$(python3 -c "import json;d=json.load(open('inspection/final/audit.json'));print(d['unconnected'],d['material_violations'],d['via_pad_min_mm'])")
  echo "attempt $i: unconnected/material/via_pad_min = $U" >> $LOG
  case "$U" in
    "0 "*) cp main-rev8/routed.kicad_pcb ~/workspace/projects/he-piantor-boards/.issue263-runtime/routed-closed.kicad_pcb
           cp inspection/final/main.kicad_pcb ~/workspace/projects/he-piantor-boards/.issue263-runtime/final-closed.kicad_pcb
           echo "CLOSED on attempt $i" >> $LOG; break;;
  esac
done
echo DONE >> $LOG
