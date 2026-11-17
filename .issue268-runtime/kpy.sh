#!/bin/bash
# Issue #268 KiCad environment wrapper: run a python script with pcbnew available.
K=$HOME/workspace/projects/he-piantor-42/.issue129-runtime/kicad
V=$HOME/workspace/projects/he-piantor-42/.issue182-runtime/venv/bin/python
cd "$HOME/workspace/projects/he-piantor-matrix4" || exit 1
exec env -i PATH=/usr/bin:/bin \
  PYTHONPATH=$K/usr/lib/python3/dist-packages \
  LD_LIBRARY_PATH=$K/usr/lib/x86_64-linux-gnu:$K/usr/lib/kicad \
  KICAD_STOCK_DATA_HOME=$K/usr/share/kicad \
  KICAD_CLI=$K/usr/bin/kicad-cli \
  HOME=$PWD/.issue268-runtime TMPDIR=$PWD/.issue268-runtime/tmp \
  $V "$@"
