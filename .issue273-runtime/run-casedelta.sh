#!/bin/bash
cd /home/hatch/workspace/projects/he-piantor-wingnotch
./.issue273-runtime/kpy.sh .issue273-runtime/case-delta-2e.py > .issue273-runtime/case-delta-2e.log 2>&1
echo "exit=$?" >> .issue273-runtime/case-delta-2e.log
