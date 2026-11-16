#!/bin/bash
export LD_LIBRARY_PATH=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/lib/x86_64-linux-gnu:/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/lib
CLI=/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/kicad/usr/bin/kicad-cli
for var in 17mm-right 17mm-left 16mm-right 16mm-left; do
  d=n3-$var
  $CLI pcb drc --output $d/drc.json --format json $d/routed.kicad_pcb > $d/drc.log 2>&1
  echo "$var drc exit $?"
done
echo DRCDONE
