"""Local geometry around a pour gap: foreign tracks/pads on the layer + fragment boundaries."""
import sys
import pcbnew as p
from shapely.geometry import LineString, Point
from verify import xy, polys, padgeom

E = '/home/hatch/workspace/projects/he-piantor-boards/hardware/kicad/qualification/issue-263-implementation'
name, net, layer, cx, cy, R = sys.argv[1], sys.argv[2], p.B_Cu if sys.argv[3] == 'B' else p.F_Cu, float(sys.argv[4]), float(sys.argv[5]), float(sys.argv[6])
b = p.LoadBoard(f'{E}/{name}/main.kicad_pcb')
b.BuildConnectivity(); p.ZONE_FILLER(b).Fill(b.Zones()); b.BuildConnectivity()
C = Point(cx, cy)
print(f'--- foreign tracks on layer (within {R}mm of {cx},{cy})')
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        if C.distance(Point(xy(t.GetPosition()))) < R:
            print(f'  VIA {t.GetNetname()} at {xy(t.GetPosition())}')
    elif t.GetLayer() == layer and t.GetNetname() != net:
        g = LineString([xy(t.GetStart()), xy(t.GetEnd())])
        if C.distance(g) < R:
            print(f'  TRK {t.GetNetname()} w={p.ToMM(t.GetWidth()):.2f} {xy(t.GetStart())} -> {xy(t.GetEnd())} dist={C.distance(g):.3f}')
print('--- foreign pads on layer')
for f in b.GetFootprints():
    for a in f.Pads():
        if a.GetNetname() != net and a.IsOnLayer(layer):
            g = padgeom(a, layer)
            if C.distance(g) < R:
                print(f'  PAD {f.GetReference()}.{a.GetNumber()} {a.GetNetname()} centre {xy(a.GetPosition())} dist={C.distance(g):.3f}')
print('--- same-net fragments: boundary vertices near centre')
for z in b.Zones():
    if z.GetIsRuleArea() or z.GetNetname() != net or not z.IsOnLayer(layer):
        continue
    g = polys(z.GetFilledPolysList(layer))
    for part in (g.geoms if hasattr(g, 'geoms') else [g]):
        if part.is_empty or C.distance(part) > R:
            continue
        verts = [(round(x, 3), round(y, 3)) for x, y in part.exterior.coords if abs(x - cx) < R and abs(y - cy) < R]
        print(f'  frag area={part.area:.3f} near-verts={verts}')
print('--- same-net tracks on layer near centre')
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA) or t.GetLayer() != layer or t.GetNetname() != net:
        continue
    g = LineString([xy(t.GetStart()), xy(t.GetEnd())])
    if C.distance(g) < R:
        print(f'  TRK w={p.ToMM(t.GetWidth()):.2f} {xy(t.GetStart())} -> {xy(t.GetEnd())}')
