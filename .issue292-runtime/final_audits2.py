import pcbnew as p, math, sys, itertools
from shapely.geometry import Polygon, LineString, Point
from shapely.geometry import box as sbox
def mm(v): return v / 1e6
def rect_poly(cx, cy, w, h, deg):
    r = math.radians(deg); c, s = math.cos(r), math.sin(r)
    return Polygon([(cx + dx * c + dy * s, cy - dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
def pad_poly(pad):
    q = pad.GetPosition(); sz = pad.GetSize()
    cx, cy, w, h = mm(q.x), mm(q.y), mm(sz.x), mm(sz.y)
    if pad.GetShape() == p.PAD_SHAPE_CIRCLE: return Point(cx, cy).buffer(w / 2, quad_segs=24)
    return rect_poly(cx, cy, w, h, pad.GetOrientationDegrees())

def audit(path):
    b = p.LoadBoard(path)
    pads, vias, tracks = [], [], []
    for f in b.GetFootprints():
        for pad in f.Pads():
            pads.append((f"{f.GetReference()}.{pad.GetNumber()}", pad.GetNetname(), pad_poly(pad)))
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            q = t.GetPosition(); c = (mm(q.x), mm(q.y))
            vias.append((t.GetNetname(), c, Point(c).buffer(mm(t.GetWidth(p.F_Cu)) / 2, quad_segs=24)))
        else:
            s, e = t.GetStart(), t.GetEnd()
            tracks.append((t.GetNetname(), t.GetLayer(),
                           LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=8)))
    # via-pad (different net), true shapes
    worst = []
    for net, c, vp in vias:
        for ref, pnet, pp in pads:
            if pnet == net: continue
            if abs(pp.bounds[0] - c[0]) > 4 or abs(pp.bounds[1] - c[1]) > 4: continue
            d = vp.distance(pp)
            if d < 0.13: worst.append((round(d, 4), net, tuple(round(v, 2) for v in c), ref, pnet))
    worst.sort()
    # trackpad: pads inside r20 (100,118)
    tp = Point(100, 118).buffer(20, quad_segs=48)
    tp_pads = [ref for ref, pnet, pp in pads if pp.intersects(tp) and pp.intersection(tp).area > 1e-6]
    # antenna strip: tracks/vias
    ant = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
    bad_ant = [n for n, l, g in tracks if g.intersects(ant) and g.intersection(ant).area > 1e-6]
    bad_ant += [n for n, c, vp in vias if vp.intersects(ant)]
    # census
    cen = {}
    for f in b.GetFootprints():
        if f.GetReference() in ('J2', 'J3'):
            cen[f.GetReference()] = {pad.GetNumber(): pad.GetNetname() for pad in f.Pads()}
    # in-field minima
    field = sbox(69.3, 119.05, 80.9, 128.9)
    shapes = [(n, g) for n, l, g in tracks if g.intersects(field)]
    shapes += [(n, vp) for n, c, vp in vias if vp.intersects(field)]
    shapes += [(pn, pp) for ref, pn, pp in pads if pp.intersects(field)]
    best = (9, None)
    for (n1, g1), (n2, g2) in itertools.combinations(shapes, 2):
        if n1 == n2: continue
        if g1.bounds[2] < g2.bounds[0] - 0.25 or g2.bounds[2] < g1.bounds[0] - 0.25: continue
        if g1.bounds[3] < g2.bounds[1] - 0.25 or g2.bounds[3] < g1.bounds[1] - 0.25: continue
        d = g1.distance(g2)
        if d < best[0]: best = (d, (n1, n2))
    print('==', path)
    print('via-pad worst (<0.13):', worst[:8])
    print('trackpad pads inside r20:', tp_pads)
    print('antenna strip track/via violations:', len(bad_ant))
    for r in ('J2', 'J3'):
        print(r, [cen.get(r, {}).get(str(i)) for i in range(1, 15)], 'MP:', cen.get(r, {}).get('MP'))
    print('in-field min clearance:', round(best[0], 4), best[1])

audit(sys.argv[1])
