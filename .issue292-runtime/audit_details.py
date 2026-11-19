import pcbnew as p, math, sys
from shapely.geometry import Polygon, LineString, Point
def mm(v): return v / 1e6
b = p.LoadBoard(sys.argv[1])
ant = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); c = (mm(q.x), mm(q.y))
        g = Point(c).buffer(0.3, quad_segs=24)
        if g.intersects(ant) and g.intersection(ant).area > 1e-6:
            print('ANT via', t.GetNetname(), c, 'area', round(g.intersection(ant).area, 4))
    else:
        s, e = t.GetStart(), t.GetEnd()
        g = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)
        if g.intersects(ant) and g.intersection(ant).area > 1e-6:
            print('ANT trk', t.GetNetname(), 'L', t.GetLayer(), (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y)), 'area', round(g.intersection(ant).area, 4))
# GND x BTN zero pairs in field
def rect_poly(cx, cy, w, h, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return Polygon([(cx + dx * c + dy * s, cy - dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
shapes = []
for t in b.GetTracks():
    if t.GetNetname() not in ('GND', 'BTN'): continue
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition(); c = (mm(q.x), mm(q.y))
        shapes.append((t.GetNetname(), 'via', c, Point(c).buffer(0.3, quad_segs=24)))
    else:
        s, e = t.GetStart(), t.GetEnd()
        shapes.append((t.GetNetname(), 'trk', (mm(s.x), mm(s.y)), LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)))
for f in b.GetFootprints():
    for pad in f.Pads():
        if pad.GetNetname() not in ('GND', 'BTN'): continue
        q = pad.GetPosition(); sz = pad.GetSize()
        cx, cy, w, h = mm(q.x), mm(q.y), mm(sz.x), mm(sz.y)
        g = Point(cx, cy).buffer(w / 2, quad_segs=24) if pad.GetShape() == p.PAD_SHAPE_CIRCLE else rect_poly(cx, cy, w, h, pad.GetOrientationDegrees())
        shapes.append((pad.GetNetname(), 'pad', f"{f.GetReference()}.{pad.GetNumber()}", g))
import itertools
for (n1, k1, a1, g1), (n2, k2, a2, g2) in itertools.combinations(shapes, 2):
    if n1 == n2: continue
    if max(g1.bounds[0], g2.bounds[0]) > 81 or min(g1.bounds[2], g2.bounds[2]) < 69: continue
    if max(g1.bounds[1], g2.bounds[1]) > 129 or min(g1.bounds[3], g2.bounds[3]) < 119: continue
    d = g1.distance(g2)
    if d < 0.02: print('ZERO', n1, k1, a1, 'x', n2, k2, a2, 'd', round(d, 4), 'overlap', round(g1.intersection(g2).area, 4))
