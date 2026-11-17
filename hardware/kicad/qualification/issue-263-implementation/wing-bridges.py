"""F1 pour bridges: join pinched zone fragments with a 0.30 mm track on the
pour layer (D-021 power width). Local copper repair only: no placement moves,
no rule relaxation. Each candidate is validated against foreign copper on its
layer at the 0.10 mm yardstick clearance before it is applied."""
import json, math, sys
import pcbnew as p
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from verify import xy, polys, padgeom

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
V = lambda a: p.VECTOR2I(round(a[0] * 1e6), round(a[1] * 1e6))
W2 = 0.30

CASES = [
    # variant, net, layer, gap endpoints (from wing-analysis.json)
    ('wing-rev5-16mm-right', 'GND', p.B_Cu, (82.609, 28.293), (82.893, 28.009)),
    ('wing-rev5-17mm-right', 'GND', p.B_Cu, (81.400, 27.545), (81.800, 27.525)),
    ('wing-rev5-17mm-left', 'HALL_5V', p.F_Cu, None, None),  # point-touch: direction searched
]

def foreign_on_layer(b, net, layer):
    gs = []
    for f in b.GetFootprints():
        for a in f.Pads():
            if a.GetNetname() != net and a.IsOnLayer(layer):
                gs.append(padgeom(a, layer))
    for t in b.GetTracks():
        if t.GetNetname() == net:
            continue
        if isinstance(t, p.PCB_VIA):
            gs.append(Point(xy(t.GetPosition())).buffer(0.3))
        elif t.GetLayer() == layer:
            gs.append(LineString([xy(t.GetStart()), xy(t.GetEnd())]).buffer(p.ToMM(t.GetWidth()) / 2))
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() == net or not z.IsOnLayer(layer):
            continue
        g = polys(z.GetFilledPolysList(layer))
        if not g.is_empty:
            gs.append(g)
    return unary_union(gs) if gs else None

def fragments(b, net, layer):
    """Filled-zone fragments of net on layer, as separate polygons."""
    out = []
    for z in b.Zones():
        if z.GetIsRuleArea() or z.GetNetname() != net or not z.IsOnLayer(layer):
            continue
        g = polys(z.GetFilledPolysList(layer))
        for part in (g.geoms if hasattr(g, 'geoms') else [g]):
            if not part.is_empty:
                out.append(part)
    return out

for name, net, layer, ga, gb in CASES:
    w = f'{E}/{name}'
    b = p.LoadBoard(f'{w}/main.kicad_pcb')
    mgr = p.GetSettingsManager(); mgr.LoadProject(f'{w}/input.kicad_pro'); b.SetProject(mgr.Prj())
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()
    frags = fragments(b, net, layer)
    foreign = foreign_on_layer(b, net, layer)
    if ga is not None:
        d = (gb[0] - ga[0], gb[1] - ga[1]); L = math.hypot(*d); d = (d[0] / L, d[1] / L)
        c = ((ga[0] + gb[0]) / 2, (ga[1] + gb[1]) / 2)
        a2 = (c[0] - d[0] * (L / 2 + 0.5), c[1] - d[1] * (L / 2 + 0.5))
        b2 = (c[0] + d[0] * (L / 2 + 0.5), c[1] + d[1] * (L / 2 + 0.5))
        candidates = [(a2, b2)]
    else:
        # point-touch: find the touching pair + point, search orientation
        touch = None
        for i, f1 in enumerate(frags):
            for f2 in frags[i + 1:]:
                if f1.distance(f2) < 0.01:
                    inter = f1.intersection(f2)
                    pt = inter if inter.geom_type == 'Point' else inter.representative_point()
                    touch = (f1, f2, (pt.x, pt.y))
        assert touch, f'{name}: no touching fragment pair found'
        f1, f2, c = touch
        candidates = []
        for deg in range(0, 180, 5):
            th = math.radians(deg); d = (math.cos(th), math.sin(th))
            a2 = (c[0] - d[0] * 0.6, c[1] - d[1] * 0.6); b2 = (c[0] + d[0] * 0.6, c[1] + d[1] * 0.6)
            g = LineString([a2, b2]).buffer(W2 / 2)
            score = min(g.intersection(f1).area, g.intersection(f2).area)
            candidates.append((score, a2, b2))
        candidates.sort(reverse=True)
        candidates = [(a2, b2) for _, a2, b2 in candidates[:6]]
    applied = None
    for a2, b2 in candidates:
        g = LineString([a2, b2]).buffer(W2 / 2)
        clr = g.distance(foreign) if foreign is not None else 9
        if clr < 0.0999:
            print(f'{name}: candidate {a2}->{b2} rejected, foreign clearance {clr:.3f}', flush=True)
            continue
        t = p.PCB_TRACK(b); t.SetStart(V(a2)); t.SetEnd(V(b2)); t.SetWidth(p.FromMM(W2))
        t.SetLayer(layer); t.SetNetCode(b.FindNet(net).GetNetCode()); b.Add(t)
        applied = (a2, b2, clr)
        break
    assert applied, f'{name}: no valid bridge candidate'
    b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()
    p.SaveBoard(f'{w}/main.kicad_pcb', b)
    print(f'{name}: bridge {net} {applied[0]}->{applied[1]} foreign_clearance {applied[2]:.3f} APPLIED', flush=True)
print('done')
