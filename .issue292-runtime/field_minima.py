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
LAYN = {0: 'F', 4: 'In1', 6: 'In2', 31: 'B'}
by_layer = {}
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); c = (mm(q.x), mm(q.y))
        g = Point(c).buffer(0.3, quad_segs=16)
        for L in (0, 4, 6, 31): by_layer.setdefault(L, []).append((t.GetNetname(), g))
    else:
        s, e = t.GetStart(), t.GetEnd()
        g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)
        by_layer.setdefault(t.GetLayer(), []).append((t.GetNetname(), g))
for f in b.GetFootprints():
    for pad in f.Pads():
        q = pad.GetPosition(); sz = pad.GetSize()
        cx, cy, w, h = mm(q.x), mm(q.y), mm(sz.x), mm(sz.y)
        g = Point(cx, cy).buffer(w / 2, quad_segs=16) if pad.GetShape() == p.PAD_SHAPE_CIRCLE else rect_poly(cx, cy, w, h, pad.GetOrientationDegrees())
        for L in (0, 4, 6, 31):
            if pad.IsOnLayer(L) or pad.GetAttribute() == p.PAD_ATTRIB_PTH:
                by_layer.setdefault(L, []).append((pad.GetNetname(), g))
for L, shapes in sorted(by_layer.items()):
    sub = [(n, g) for n, g in shapes if g.intersects(field)]
    best = (9, None)
    for (n1, g1), (n2, g2) in itertools.combinations(sub, 2):
        if n1 == n2: continue
        if g1.bounds[2] < g2.bounds[0] - 0.3 or g2.bounds[2] < g1.bounds[0] - 0.3: continue
        if g1.bounds[3] < g2.bounds[1] - 0.3 or g2.bounds[3] < g1.bounds[1] - 0.3: continue
        d = g1.distance(g2)
        if d < best[0]: best = (d, (n1, n2))
    print(LAYN.get(L, L), 'in-field min diff-net clearance:', round(best[0], 4), best[1], f'({len(sub)} shapes)')
# ADC_B V2 drill to PAD_DR dogleg (F)
v2 = Point(75.90, 120.30).buffer(0.15, quad_segs=24)
for t in b.GetTracks():
    if t.GetNetname() != 'PAD_DR' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)
    d = v2.distance(g)
    if d < 0.3: print('V2 drill to PAD_DR track', (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y)), round(d, 4))
