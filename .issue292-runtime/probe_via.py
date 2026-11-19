"""Probe candidate via points: per-layer distance from via disc edge
(r=0.30) to nearest other-net copper; drill-edge distance to other
vias; distance to own-net copper (must overlap/touch for a tap).
Usage: probe_via.py <board> <net> x,y [x,y ...]"""
import pcbnew as p, sys, math
from shapely.geometry import Polygon, LineString, Point
b = p.LoadBoard(sys.argv[1])
filler = p.ZONE_FILLER(b); filler.Fill(list(b.Zones()))
NET = sys.argv[2]
LAYID = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
def mm(v): return p.ToMM(v)
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
obs = {L: [] for L in ('F', 'I1', 'I2', 'B')}
own = {L: [] for L in ('F', 'I1', 'I2', 'B')}
vias_other = []
for f in b.GetFootprints():
    for pad in f.Pads():
        net = pad.GetNetname()
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y), pad.GetOrientationDegrees())
        pth = pad.GetAttribute() == p.PAD_ATTRIB_PTH
        lays = ['F', 'I1', 'I2', 'B'] if pth else [LAYID[l] for l in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu) if pad.IsOnLayer(l)]
        for L in lays:
            (own if net == NET else obs)[L].append(poly)
for t in b.GetTracks():
    net = t.GetNetname()
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition(); cx, cy = mm(pos.x), mm(pos.y)
        poly = Point(cx, cy).buffer(mm(t.GetWidth(p.F_Cu)) / 2, resolution=12)
        if net == NET:
            for L in ('F', 'I1', 'I2', 'B'): own[L].append(poly)
        else:
            vias_other.append((cx, cy, mm(t.GetDrill()) / 2))
            for L in ('F', 'I1', 'I2', 'B'): obs[L].append(poly)
    else:
        s, e = t.GetStart(), t.GetEnd()
        poly = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, resolution=4, cap_style=1)
        (own if net == NET else obs)[LAYID[t.GetLayer()]].append(poly)
for z in b.Zones():
    net = z.GetNetname()
    for lid, L in LAYID.items():
        if not z.IsOnLayer(lid): continue
        fps = z.GetFilledPolysList(lid)
        for oi in range(fps.OutlineCount()):
            chain = fps.Outline(oi)
            pts = [(mm(chain.GetPoint(i).x), mm(chain.GetPoint(i).y)) for i in range(chain.PointCount())]
            if len(pts) >= 3:
                (own if net == NET else obs)[L].append(Polygon(pts))
for arg in sys.argv[3:]:
    x, y = (float(v) for v in arg.split(','))
    disc = Point(x, y).buffer(0.30, resolution=24)
    print(f"--- via candidate ({x},{y}) net {NET}")
    for L in ('F', 'I1', 'I2', 'B'):
        d_obs = min((disc.distance(g) for g in obs[L]), default=9.9)
        d_own = min((disc.distance(g) for g in own[L]), default=9.9)
        print(f"   {L}: clearance to other-net = {d_obs:.3f}   distance to own-net = {d_own:.3f}")
    dd = min((math.hypot(x - vx, y - vy) - 0.15 - vr for vx, vy, vr in vias_other), default=9.9)
    print(f"   drill-edge to nearest other via drill: {dd:.3f}")
