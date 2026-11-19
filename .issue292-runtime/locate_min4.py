import pcbnew as p, itertools
from shapely.geometry import LineString, Point
def mm(v): return v / 1e6
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
items = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); c = (mm(q.x), mm(q.y))
        if 69 < c[0] < 81 and 119 < c[1] < 129:
            items.append((t.GetNetname(), 'via', c, Point(c).buffer(0.3, quad_segs=16)))
    else:
        if t.GetLayer() not in (2, 6): continue
        s, e = t.GetStart(), t.GetEnd()
        a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
        if max(a[0], bb[0]) < 69 or min(a[0], bb[0]) > 81 or max(a[1], bb[1]) < 119 or min(a[1], bb[1]) > 129: continue
        items.append((t.GetNetname(), f'trk{t.GetLayer()}', a, LineString([a, bb]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)))
for (n1, k1, a1, g1), (n2, k2, a2, g2) in itertools.combinations(items, 2):
    if n1 == n2 or {n1, n2} != {'GND', 'MUX_A0'}: continue
    d = g1.distance(g2)
    if d < 0.06: print(round(d, 4), n1, k1, a1, 'x', n2, k2, a2)
