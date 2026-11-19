import pcbnew as p, itertools
from shapely.geometry import LineString, Point
def mm(v): return v / 1e6
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
items = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA): continue
    if t.GetLayer() not in (2, 6): continue
    s, e = t.GetStart(), t.GetEnd()
    a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
    if max(a[0], bb[0]) < 69 or min(a[0], bb[0]) > 81 or max(a[1], bb[1]) < 119 or min(a[1], bb[1]) > 129: continue
    items.append((t.GetNetname(), t.GetLayer(), a, bb, LineString([a, bb]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)))
res = []
for (n1, l1, a1, b1, g1), (n2, l2, a2, b2, g2) in itertools.combinations(items, 2):
    if n1 == n2 or l1 != l2: continue
    d = g1.distance(g2)
    if d < 0.055: res.append((round(d, 4), n1, l1, a1, b1, n2, a2, b2))
res.sort()
for r in res[:5]: print(r)
