"""S2.1 donor inventory: footprints, pads->nets, outline, netclasses, stackup."""
import json
import sys
from collections import Counter, defaultdict

sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-wmatrix/.issue288-runtime')
from k288env import apply_env, DONOR, RT, KICAD
apply_env()
sys.path.insert(0, str(KICAD / 'usr/lib/python3/dist-packages'))

import pcbnew

b = pcbnew.LoadBoard(str(DONOR))
out = {}

# stackup / general
out['thickness'] = b.GetDesignSettings().GetBoardThickness() / 1e6
out['copper_layers'] = b.GetCopperLayerCount()

# outline segments
edges = []
for d in b.GetDrawings():
    if d.GetLayerName() == 'Edge.Cuts':
        s = d.GetShape()
        if s == pcbnew.SHAPE_T_SEGMENT:
            edges.append([d.GetStart().x / 1e6, d.GetStart().y / 1e6,
                          d.GetEnd().x / 1e6, d.GetEnd().y / 1e6])
        else:
            edges.append(['shape', str(s)])
out['outline_segments'] = edges
xs = [c for e in edges if isinstance(e[0], float) for c in (e[0], e[2])]
ys = [c for e in edges if isinstance(e[0], float) for c in (e[1], e[3])]
out['outline_bbox'] = [min(xs), min(ys), max(xs), max(ys)]

# netclasses from the .kicad_pro (KiCad 9 API no longer exposes them on DS)
import pathlib
pro = json.loads(pathlib.Path(str(DONOR).replace('.kicad_pcb', '.kicad_pro')).read_text())
ns = pro.get('net_settings', {})
nc = {}
for c in ns.get('classes', []):
    nc[c['name']] = dict(track=c.get('track_width'), clearance=c.get('clearance'),
                         via_d=c.get('via_diameter'), via_drill=c.get('via_drill'))
out['netclasses'] = nc
out['netclass_patterns'] = ns.get('netclass_assignments') or ns.get('meta')
na = {}
for code, net in b.GetNetInfo().NetsByNetcode().items():
    na[net.GetNetname()] = net.GetNetClassName()
out['netclass_assignments'] = na

# footprints
fps = []
for fp in b.GetFootprints():
    pads = []
    for p in fp.Pads():
        pos = p.GetPosition()
        pads.append(dict(num=p.GetNumber(), net=p.GetNetname(),
                         x=pos.x / 1e6, y=pos.y / 1e6,
                         w=p.GetSize().x / 1e6, h=p.GetSize().y / 1e6,
                         layer='B' if p.IsFlipped() else 'F'))
    c = fp.GetCenter()
    fps.append(dict(ref=fp.GetReference(), value=fp.GetValue(),
                    fp=str(fp.GetFPID().GetLibItemName()),
                    x=c.x / 1e6, y=c.y / 1e6, rot=fp.GetOrientationDegrees(),
                    flipped=fp.IsFlipped(), pads=pads))
out['footprints'] = fps
out['fp_refs'] = Counter(f['fp'] for f in fps)

# tracks/vias counts per net
tc = Counter()
for t in b.GetTracks():
    tc[t.GetNetname()] += 1
out['track_items_per_net'] = dict(tc)
out['zones'] = len(list(b.Zones()))

(RT / 'donor-inventory.json').write_text(json.dumps(out, indent=1, ensure_ascii=False))
print('footprints:', len(fps), dict(out['fp_refs']))
print('bbox:', out['outline_bbox'], 'thickness:', out['thickness'], 'cu layers:', out['copper_layers'])
print('nets:', len(out['netclass_assignments']))
