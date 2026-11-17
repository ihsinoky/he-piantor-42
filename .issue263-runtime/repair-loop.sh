#!/bin/bash
cd ~/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation
RT=~/workspace/projects/he-piantor-boards/.issue263-runtime/run
PY=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3
LOG=~/workspace/projects/he-piantor-boards/.issue263-runtime/repair-loop.log
for i in 1 2 3 4; do
  cp main-rev8/routed.kicad_pcb main-rev8/repair-in.kicad_pcb
  $RT $PY route-main-repair.py >> $LOG 2>&1
  for t in 1 2 3; do
    $RT $PY audit-main.py >> $LOG 2>&1
    M1=$(stat -c %Y inspection/final/audit.json); M0=$(stat -c %Y main-rev8/routed.kicad_pcb)
    [ "$M1" -gt "$M0" ] && break
  done
  U=$(python3 -c "import json;d=json.load(open('inspection/final/audit.json'));print(d['unconnected'],d['material_violations'],round(d['via_pad_min_mm'],4))")
  echo "repair $i: unconnected/material/via_min = $U" >> $LOG
  case "$U" in "0 "*) echo "CLOSED at repair $i" >> $LOG; break;; esac
done
echo "REPAIR LOOP DONE" >> $LOG
