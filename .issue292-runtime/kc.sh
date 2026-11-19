#!/bin/bash
# KiCad 9.0.9 extracted-runtime environment (he-piantor-42 .issue129-runtime)
K="$HOME/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
export LD_LIBRARY_PATH="$K/lib/x86_64-linux-gnu:$K/lib"
export PYTHONPATH="$K/lib/python3/dist-packages"
export KICAD9_FOOTPRINT_DIR="$K/share/kicad/footprints"
exec "$@"
