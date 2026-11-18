#!/bin/bash
K=$HOME/workspace/projects/he-piantor-42/.issue129-runtime/kicad
cd "$HOME/workspace/projects/he-piantor-mainsym" || exit 1
exec env -i PATH=/usr/bin:/bin \
  LD_LIBRARY_PATH=$K/usr/lib/x86_64-linux-gnu:$K/usr/lib/kicad \
  KICAD_STOCK_DATA_HOME=$K/usr/share/kicad \
  HOME=$PWD/.issue275-runtime TMPDIR=$PWD/.issue275-runtime/tmp \
  "$@"
