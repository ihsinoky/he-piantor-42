"""Cheap diagnostic: for one net, which layers block via placement
at candidate points? Indices built once."""
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
idx = {}
for L in ('F','I1','I2','B'):
    shapes = [s.buffer(0.05) for n, s in raw[L] if n != net]
    idx[L] = (STRtree(shapes), shapes)
def blockers(x, y):
    vc = Point(x, y).buffer(0.3)
    res = []
    if any(ALL_PADS[i].intersects(vc) for i in PADTREE.query(vc)): res.append('PAD')
    for L in ('F','I1','I2','B'):
        st, shapes = idx[L]
        if any(shapes[i].intersects(vc) for i in st.query(vc)): res.append(L)
    return res or ['LEGAL']
tests = json.loads(sys.argv[2])
for (x, y) in tests:
    print((x, y), blockers(x, y))
