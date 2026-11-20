"""Generate edge-items.md from edge-wmain.json + DRC cross-reference."""
import json, re
from collections import Counter, defaultdict

w = json.load(open('.issue292-runtime/edge-wmain.json'))
r10 = json.load(open('.issue292-runtime/edge-rev10.json'))
drc = json.load(open('/home/hatch/workspace/projects/he-piantor-wmain/.issue292-runtime/completion-final2-drc.json'))
drc_map = {}
for v in drc['violations']:
    if v['type'] != 'copper_edge_clearance': continue
    m = re.search(r'actual ([\d.]+) mm', v['description'])
    for it in v['items']:
        if 'Edge.Cuts' not in it['description']:
            drc_map[it['uuid']] = float(m.group(1)) if m else None

by_uuid = defaultdict(list)
for x in w['flagged']: by_uuid[x['uuid']].append(x)
RANK = {'CROSSING': 0, 'TOUCHING': 1, 'CLOSE': 2}
items = []
for u, lst in by_uuid.items():
    worst = sorted(lst, key=lambda z: RANK[z['cls']])[0]
    items.append(dict(uuid=u, cls=worst['cls'], kind=worst['kind'], net=worst['net'],
                      desc=worst['desc'], dist=worst['dist'], oa=worst['outside_area'],
                      layers=sorted({z['layer'] for z in lst}),
                      drc=drc_map.get(u), anchor=worst['anchor']))
items.sort(key=lambda z: (RANK[z['cls']], z['dist'], z['desc']))

def cluster(it):
    x, y = it['anchor']
    if x < 85: return 'W - west dent / module fanout'
    if it['desc'].startswith('pad JPAD') or (110 <= x <= 120 and y < 105): return 'T - north tab east shoulder / JPAD'
    if x > 125: return 'E - east slant'
    if y > 135: return 'S - south edge'
    if y < 105: return 'N - north-west shoulder / north edge'
    return 'C - central/other'

clusters = defaultdict(list)
for it in items: clusters[cluster(it)].append(it)

L = []
L.append('# Issue #292 edge-fix S1: copper-vs-outline enumeration (adopted board 509e52a7)')
L.append('')
L.append('Method: KiCad `GetBoardPolygonOutlines` outline (14 vertices) vs exact')
L.append('effective-shape geometry (tracks/vias/pads per layer, zone fills) via shapely.')
L.append('Cross-check vs completion round DRC (`completion-final2-drc.json`): all 114 DRC')
L.append('copper_edge_clearance items are contained in this list (0 missed); this list adds')
L.append('17 items DRC did not flag separately (all CROSSING, west fanout). Values agree')
L.append('to <=0.0001mm on shared items.')
L.append('')
L.append(f"Totals: {len(items)} unique items flagged "
         f"({Counter(i['cls'] for i in items)}); "
         f"{len(w['flagged'])} item-layer instances; {w['scanned']} copper instances scanned.")
L.append('')
L.append('Inherited vs introduced: Rev.10 board (same outline) has exactly 2 flagged items')
L.append('(MUX_OUT_C track, 2 segments, CLOSE 0.4414) and neither is flagged in the wireless')
L.append('board. No flagged wireless item matches a flagged Rev.10 item => **all items below')
L.append('are wireless-introduced** (new parts/routing or moved Rev.10 geometry).')
L.append('')
for name in sorted(clusters):
    lst = clusters[name]
    L.append(f"## Cluster {name} - {len(lst)} items ({Counter(i['cls'] for i in lst)})")
    L.append('')
    L.append('| cls | dist mm | outside mm2 | kind | net | layers | DRC actual | item |')
    L.append('|---|---|---|---|---|---|---|---|')
    for it in lst:
        L.append(f"| {it['cls']} | {it['dist']} | {it['oa']} | {it['kind']} | {it['net']} | "
                 f"{','.join(it['layers'])} | {it['drc'] if it['drc'] is not None else '-'} | {it['desc']} |")
    L.append('')
open('.issue292-runtime/edge-items.md', 'w').write('\n'.join(L))
print('items:', len(items), Counter(i['cls'] for i in items))
print({k: len(v) for k, v in clusters.items()})
