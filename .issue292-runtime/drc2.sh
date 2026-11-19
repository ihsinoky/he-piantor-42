#!/bin/bash
# usage: drc2.sh <board> <outprefix> [nodru]
set -e
cd "$(dirname "$0")"
source kenv.sh
BOARD="$1"; OUT="$2"; MODE="${3:-dru}"
W=drcwork-$OUT
rm -rf "$W"; mkdir -p "$W"
python3 - "$BOARD" "$W" << 'PYEOF'
import pcbnew as p, sys
b = p.LoadBoard(sys.argv[1])
filler = p.ZONE_FILLER(b)
filler.Fill(list(b.Zones()))
b.Save(sys.argv[2] + '/wmain.kicad_pcb')
print('filled')
PYEOF
cp ../hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pro "$W/"
if [ "$MODE" = "nodru" ]; then
  grep -v "module_field" ../hardware/kicad/qualification/issue-292-wmain/wmain.kicad_dru > "$W/wmain.kicad_dru"
else
  cp ../hardware/kicad/qualification/issue-292-wmain/wmain.kicad_dru "$W/"
fi
$KICAD_CLI pcb drc --format json --severity-all -o "$OUT-drc2.json" "$W/wmain.kicad_pcb" 2>&1 | tail -1
python3 - "$OUT" << 'PYEOF'
import json, sys
from collections import Counter
d = json.load(open(sys.argv[1] + '-drc2.json'))
print('violations:', len(d['violations']), dict(Counter(v['type'] for v in d['violations']).most_common(8)))
print('unconnected:', len(d.get('unconnected_items', [])))
PYEOF
