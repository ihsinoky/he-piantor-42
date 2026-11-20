#!/bin/sh
K=/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad
export LD_LIBRARY_PATH=$K/usr/lib/x86_64-linux-gnu:$K/usr/lib/kicad
export PYTHONPATH=$K/usr/lib/python3/dist-packages
export KICAD_STOCK_DATA_HOME=$K/usr/share/kicad
export PATH=$K/usr/bin:$PATH
exec python3 "$@"
