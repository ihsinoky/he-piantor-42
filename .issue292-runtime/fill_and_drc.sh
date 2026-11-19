#!/bin/bash
# usage: fill_and_drc.sh <board.kicad_pcb> <outprefix>
set -e
cd "$(dirname "$0")"
source kenv.sh
BOARD="$1"; OUT="$2"
python3 - "$BOARD" << 'EOF'
import pcbnew as p, sys
b = p.LoadBoard(sys.argv[1])
filler = p.ZONE_FILLER(b)
zones = list(b.Zones())
filler.Fill(zones)
b.Save('/home/hatch/workspace/projects/he-piantor-wmain/.issue292-runtime/filled-check.kicad_pcb')
print('filled zones:', len(zones))
EOF
cp "$(dirname "$BOARD")"/*.kicad_pro filled-check.kicad_pro 2>/dev/null || true
$KICAD_CLI pcb drc --format json --severity-all -o "$OUT-drc.json" filled-check.kicad_pcb 2>&1 | tail -1
python3 - "$OUT" << 'EOF'
import json, sys
from collections import Counter
d = json.load(open(sys.argv[1] + '-drc.json'))
c = Counter(v['type'] for v in d['violations'])
print('violations:', len(d['violations']), dict(c.most_common(8)))
print('unconnected:', len(d.get('unconnected_items', [])))
EOF
