#!/bin/bash
cd ~/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation
RT=~/workspace/projects/he-piantor-boards/.issue263-runtime/run
PY=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3
LOG=~/workspace/projects/he-piantor-boards/.issue263-runtime/roll-loop2.log
BEST=99
for i in 1 2 3 4 5; do
  $RT $PY route-main-esc.py >> $LOG 2>&1
  cp main-rev8/routed.kicad_pcb ~/workspace/projects/he-piantor-boards/.issue263-runtime/roll2-candidate.kicad_pcb
  M0=$(stat -c %Y main-rev8/routed.kicad_pcb)
  for try in 1 2 3; do
    $RT $PY audit-main.py >> $LOG 2>&1
    M1=$(stat -c %Y inspection/final/audit.json)
    [ "$M1" -gt "$M0" ] && break
    echo "audit stale (try $try), retrying" >> $LOG
  done
  U=$(python3 -c "import json;d=json.load(open('inspection/final/audit.json'));print(d['unconnected'],d['material_violations'],round(d['via_pad_min_mm'],4))")
  echo "esc attempt $i: unconnected/material/via_pad_min = $U" >> $LOG
  N=$(echo $U | cut -d' ' -f1)
  if [ "$N" -lt "$BEST" ]; then BEST=$N; cp ~/workspace/projects/he-piantor-boards/.issue263-runtime/roll2-candidate.kicad_pcb ~/workspace/projects/he-piantor-boards/.issue263-runtime/routed-best.kicad_pcb; cp inspection/final/audit.json ~/workspace/projects/he-piantor-boards/.issue263-runtime/audit-best.json; echo "new best: $BEST" >> $LOG; fi
  case "$U" in "0 0 "*) cp ~/workspace/projects/he-piantor-boards/.issue263-runtime/roll2-candidate.kicad_pcb ~/workspace/projects/he-piantor-boards/.issue263-runtime/routed-closed.kicad_pcb; echo "CLOSED on esc attempt $i" >> $LOG; break;; esac
done
echo "LOOP2 DONE best=$BEST" >> $LOG
