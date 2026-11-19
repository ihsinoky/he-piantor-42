"""Restore original stub chains for stranded connector pads (shape-based).

Reads the ADOPTED board (tree), finds every track/via of the pad's net whose
shape intersects the pad shape, then grows by shape intersection, keeping
items whose centre is within RADIUS of the pad; adds copies to the work board.
Usage: kpy.sh restore_stubs.py NET:REF.PAD [NET:REF.PAD ...]
"""
import pcbnew as p, math, sys
from shapely.geometry import Point, LineString
from shapely.strtree import STRtree

SRC = 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'
DST = '.issue292-runtime/wmain-work.kicad_pcb'
RADIUS = 4.5

def mm(v): return v / 1e6

src = p.LoadBoard(SRC)
work = p.LoadBoard(DST)

def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + dx * c + dy * s, cy - dx * s + dy * c)
            for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))]

def pad_and_pos(bd, ref, padno):
    for f in bd.GetFootprints():
        if f.GetReference() == ref:
            for pad in f.Pads():
                if pad.GetNumber() == padno:
                    q = pad.GetPosition(); sz = pad.GetSize()
                    cx, cy = mm(q.x), mm(q.y)
                    if pad.GetShape() == p.PAD_SHAPE_CIRCLE:
                        from shapely.geometry import Point as Pt
                        return Pt(cx, cy).buffer(mm(sz.x) / 2, quad_segs=16), (cx, cy), pad.GetNetname()
                    from shapely.geometry import Polygon
                    return Polygon(rect_poly(cx, cy, mm(sz.x), mm(sz.y),
                                             pad.GetOrientationDegrees())), (cx, cy), pad.GetNetname()
    return None, None, None

def shape_of(t):
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        return Point(mm(q.x), mm(q.y)).buffer(mm(t.GetWidth(p.F_Cu)) / 2, quad_segs=12)
    s, e = t.GetStart(), t.GetEnd()
    return LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, quad_segs=6)

for spec in sys.argv[1:]:
    net_ref, padno = spec.rsplit('.', 1)
    net, ref = net_ref.split(':')
    pshape, (px, py), pnet = pad_and_pos(src, ref, padno)
    assert pnet == net, (spec, pnet)
    items = [t for t in src.GetTracks() if t.GetNetname() == net]
    shapes = [shape_of(t) for t in items]
    tree = STRtree(shapes)
    chosen = set(int(i) for i in tree.query(pshape, predicate='intersects'))
    frontier = list(chosen)
    while frontier:
        nxt = []
        for i in frontier:
            for j in tree.query(shapes[i], predicate='intersects'):
                j = int(j)
                if j in chosen: continue
                c = shapes[j].centroid
                if math.hypot(c.x - px, c.y - py) <= RADIUS:
                    chosen.add(j); nxt.append(j)
        frontier = nxt
    print(f'{spec}: restoring {len(chosen)} items')
    netobj = work.FindNet(net)
    for i in chosen:
        t = items[i]
        if isinstance(t, p.PCB_VIA):
            v = p.PCB_VIA(work)
            v.SetPosition(t.GetPosition())
            v.SetWidth(t.GetWidth(p.F_Cu)); v.SetDrill(t.GetDrill())
            v.SetNet(netobj); work.Add(v)
        else:
            nt = p.PCB_TRACK(work)
            nt.SetStart(t.GetStart()); nt.SetEnd(t.GetEnd())
            nt.SetWidth(t.GetWidth()); nt.SetLayer(t.GetLayer())
            nt.SetNet(netobj); work.Add(nt)
p.SaveBoard(DST, work)
print('saved')
