"""Fast ASCII map: indices built ONCE per net.
F-blocked at inflate 0.075 (w=0.05 stub), via_legal(0.05) with
prebuilt per-layer indices inflated 0.05."""
import pcbnew as p, math, json, sys
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx*c - dy*s, cy + dx*s + dy*c) for dx, dy in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))])
raw = {'F': [], 'I1': [], 'I2': [], 'B': []}
LAYN = {p.F_Cu:'F', p.In1_Cu:'I1', p.In2_Cu:'I2', p.B_Cu:'B'}
ALL_PADS = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y), pad.GetOrientationDegrees())
        ALL_PADS.append(poly)
        if pad.IsOnLayer(p.F_Cu): raw['F'].append((pad.GetNetname(), poly))
        if pad.GetAttribute() == p.PAD_ATTRIB_PTH:
            for L in ('I1','I2','B'): raw[L].append((pad.GetNetname(), poly))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        c = Point(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2)
        for L in raw: raw[L].append((t.GetNetname(), c))
    else:
        L = LAYN.get(t.GetLayer())
        if L:
            s, e = t.GetStart(), t.GetEnd()
            raw[L].append((t.GetNetname(), LineString([(p.ToMM(s.x),p.ToMM(s.y)),(p.ToMM(e.x),p.ToMM(e.y))]).buffer(p.ToMM(t.GetWidth())/2)))
out = json.loads((E/'escapes_unified.json').read_text())
for net, e in out.items():
    if 'parts' in e:
        for part in e['parts']:
            path = [tuple(q) for q in part['path']]
            for i in range(len(path)-1):
                raw[part['layer']].append((net, LineString([path[i], path[i+1]]).buffer(part['width']/2)))
        vc = Point(*e['drop_via']).buffer(0.3)
        for L in raw: raw[L].append((net, vc))
    else:
        path = [tuple(q) for q in e['path']]
        for i in range(len(path)-1):
            raw['F'].append((net, LineString([path[i], path[i+1]]).buffer(e['width']/2)))
        vc = Point(*e['via']).buffer(0.3)
        for L in raw: raw[L].append((net, vc))
PADTREE = STRtree(ALL_PADS)
net = sys.argv[1]
def build(layer, inflate):
    shapes = [s.buffer(inflate) for n, s in raw[layer] if n != net]
    return STRtree(shapes), shapes
via_idx = {L: build(L, 0.05) for L in ('F','I1','I2','B')}
fidx = build('F', 0.075)
def hit(idx, geom):
    tree, shapes = idx
    return any(shapes[i].intersects(geom) for i in tree.query(geom))
def via_legal(x, y):
    vc = Point(x, y).buffer(0.3)
    if any(ALL_PADS[i].intersects(vc) for i in PADTREE.query(vc)): return False
    return not any(hit(via_idx[L], vc) for L in ('F','I1','I2','B'))
u1 = [f for f in b.GetFootprints() if str(f.GetReference())=='U1'][0]
padpos = {}
for pad in u1.Pads():
    padpos[(round(p.ToMM(pad.GetPosition().x),2), round(p.ToMM(pad.GetPosition().y),2))] = pad.GetNetname() or 'nc'
print('net', net, ' x: 70.0..80.8 step 0.2 (54 cols), y step 0.2; #=F-blocked .=free V=via_legal P=own pad')
for gy in range(48):
    y = round(119.3 + gy*0.2, 2)
    row = ''
    for gx in range(55):
        x = round(70.0 + gx*0.2, 2)
        ch = None
        for (px, py), nn in padpos.items():
            if abs(px-x) < 0.11 and abs(py-y) < 0.11 and nn == net: ch = 'P'
        if ch is None:
            if via_legal(x, y): ch = 'V'
            elif hit(fidx, Point(x, y)): ch = '#'
            else: ch = '.'
        row += ch
    print(f'{y:6.1f} {row}')
