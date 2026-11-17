#!/bin/bash
cd /home/hatch/workspace/projects/he-piantor-matrix4
export PYTHONHASHSEED=0
for i in 1 2 3 4 5 6; do
  git checkout HEAD -- hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb
  rm -f .issue268-runtime/step2.json
  .issue268-runtime/kpy.sh .issue268-runtime/step15.py > /dev/null 2>&1
  .issue268-runtime/kpy.sh .issue268-runtime/build2.py > .issue268-runtime/build2.log 2>&1
  if grep -q 'saved; routes:' .issue268-runtime/build2.log; then
    echo "SUCCESS on attempt $i"; tail -3 .issue268-runtime/build2.log; exit 0
  fi
  echo "attempt $i failed: $(grep DIAG .issue268-runtime/build2.log | tail -1)"
done
echo "ALL ATTEMPTS FAILED"; exit 1
