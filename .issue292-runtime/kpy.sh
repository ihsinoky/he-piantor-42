#!/bin/bash
# KRT-venv python (shapely) + KiCad pcbnew
K="$HOME/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
export LD_LIBRARY_PATH="$K/lib/x86_64-linux-gnu:$K/lib"
export PYTHONPATH="$K/lib/python3/dist-packages"
exec /home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/venv/bin/python3 "$@"
