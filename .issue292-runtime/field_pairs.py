"""Replicates gates.py's in-field exception-pair method for a given
board; prints the pair list so two boards can be diffed.
Usage: field_pairs.py <board> <out.json>"""
import pcbnew as p, math, json, sys
from shapely.geometry import Polygon, LineString, Point
from shapely.strtree import STRtree
b = p.LoadBoard(sys.argv[1])
def sbox(x0, y0, x1, y1):
    return Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
FIELD = sbox(69.3, 119.05, 80.9, 128.9)
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(-rot)), math.sin(math.radians(-rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c) for dx, dy in
                    ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
LAYN = {p.F_Cu: 'F', p.In2_Cu: 'I2', p.B_Cu: 'B'}
objs = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y), pad.GetOrientationDegrees())
        if poly.intersects(FIELD):
            objs.append(('pad', pad.GetNetname(), 'F', poly, f"{f.GetReference()}.{pad.GetNumber()}"))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        shp = Point(p.ToMM(pos.x), p.ToMM(pos.y)).buffer(p.ToMM(t.GetWidth(p.F_Cu)) / 2)
        if shp.intersects(FIELD):
            for L in ('F', 'I2', 'B'):
                objs.append(('via', t.GetNetname(), L, shp, f"via@({p.ToMM(pos.x):.2f},{p.ToMM(pos.y):.2f})"))
    else:
        L = LAYN.get(t.GetLayer())
        if not L: continue
        s, e = t.GetStart(), t.GetEnd()
        shp = LineString([(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))]).buffer(p.ToMM(t.GetWidth()) / 2)
        if shp.intersects(FIELD):
            objs.append(('trk', t.GetNetname(), L, shp, f"trk({p.ToMM(s.x):.2f},{p.ToMM(s.y):.2f})-({p.ToMM(e.x):.2f},{p.ToMM(e.y):.2f})"))
tree = STRtree([o[3] for o in objs])
exc = []
for i, (k1, n1, l1, s1, id1) in enumerate(objs):
    for j in tree.query(s1.buffer(0.13)):
        if j <= i: continue
        k2, n2, l2, s2, id2 = objs[j]
        if n1 == n2 or l1 != l2: continue
        d = s1.distance(s2)
        cls = 'via-any' if 'via' in (k1, k2) else ('pad-pad' if k1 == k2 == 'pad' else ('trk-pad' if 'pad' in (k1, k2) else 'trk-trk'))
        if d < 0.0995:
            exc.append((cls, n1, n2, round(d, 4), l1, id1, id2))
exc.sort(key=lambda z: z[3])
json.dump(exc, open(sys.argv[2], 'w'), indent=0)
print(len(exc), 'pairs')
