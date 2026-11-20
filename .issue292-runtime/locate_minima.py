import pcbnew as p, math, itertools
from shapely.geometry import Polygon, LineString, Point
def mm(v): return v / 1e6
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
targets = {('MUX_A0', 'USB_DP'), ('GND', 'MUX_A0')}
items = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); c = (mm(q.x), mm(q.y))
        items.append((t.GetNetname(), 'via', c, None, Point(c).buffer(0.3, quad_segs=16)))
    else:
        s, e = t.GetStart(), t.GetEnd()
        a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
        items.append((t.GetNetname(), f'trk L{t.GetLayer()}', a, bb, LineString([a, bb]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)))
for (n1, k1, a1, b1, g1), (n2, k2, a2, b2, g2) in itertools.combinations(items, 2):
    if {n1, n2} not in targets or n1 == n2: continue
    if g1.bounds[2] < g2.bounds[0] - 0.2 or g2.bounds[2] < g1.bounds[0] - 0.2: continue
    if g1.bounds[3] < g2.bounds[1] - 0.2 or g2.bounds[3] < g1.bounds[1] - 0.2: continue
    d = g1.distance(g2)
    if d < 0.05: print(round(d, 4), n1, k1, a1, b1, 'x', n2, k2, a2, b2)
