import pcbnew as p, math, itertools
from shapely.geometry import Polygon, LineString, Point
from shapely.geometry import box as sbox
def mm(v): return v / 1e6
def rect_poly(cx, cy, w, h, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return Polygon([(cx + dx * c + dy * s, cy - dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
field = sbox(69.3, 119.05, 80.9, 128.9)
shapes = []
for t in b.GetTracks():
    if t.GetLayer() != 0 and not isinstance(t, p.PCB_VIA): continue
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); c = (mm(q.x), mm(q.y))
        shapes.append((t.GetNetname(), f'via {c}', Point(c).buffer(0.3, quad_segs=16)))
    else:
        s, e = t.GetStart(), t.GetEnd()
        a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
        shapes.append((t.GetNetname(), f'trk {a}->{bb}', LineString([a, bb]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)))
for f in b.GetFootprints():
    for pad in f.Pads():
        if not pad.IsOnLayer(0): continue
        q = pad.GetPosition(); sz = pad.GetSize()
        cx, cy, w, h = mm(q.x), mm(q.y), mm(sz.x), mm(sz.y)
        g = Point(cx, cy).buffer(w / 2, quad_segs=16) if pad.GetShape() == p.PAD_SHAPE_CIRCLE else rect_poly(cx, cy, w, h, pad.GetOrientationDegrees())
        shapes.append((pad.GetNetname(), f'pad {f.GetReference()}.{pad.GetNumber()}', g))
sub = [(n, d, g) for n, d, g in shapes if g.intersects(field)]
res = []
for (n1, d1, g1), (n2, d2, g2) in itertools.combinations(sub, 2):
    if n1 == n2: continue
    if g1.bounds[2] < g2.bounds[0] - 0.2 or g2.bounds[2] < g1.bounds[0] - 0.2: continue
    if g1.bounds[3] < g2.bounds[1] - 0.2 or g2.bounds[3] < g1.bounds[1] - 0.2: continue
    res.append((round(g1.distance(g2), 4), n1, d1, n2, d2))
res.sort()
for r in res[:5]: print(r)
