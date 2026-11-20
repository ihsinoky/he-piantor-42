import pcbnew as p
b = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
def mm(v): return v / 1e6
for fp in b.GetFootprints():
    if fp.GetReference() in ('Q1', 'JPAD'):
        for pad in fp.Pads():
            pos = pad.GetPosition()
            print(fp.GetReference(), pad.GetNumber(), pad.GetNetname(), f"{mm(pos.x):.2f},{mm(pos.y):.2f}")
# zone fill probe on In1 (layer id?) around JPAD.6 via + Q1
from shapely.geometry import Point
for z in b.Zones():
    if z.GetNetname() != 'GND': continue
    print('zone layer', z.GetLayer(), 'filled?', z.GetIsFilled())
    fp_ = z.GetFilledPolysList(z.GetLayer())
    for i in range(fp_.OutlineCount()):
        from shapely.geometry import Polygon
        pts = [(mm(fp_.Vertex(i, j).x), mm(fp_.Vertex(i, j).y)) for j in range(fp_.VertexCount(i))]
        poly = Polygon(pts)
        for q in [(112.6, 98.3), (110.6, 96.8)]:
            if poly.contains(Point(q)): print('  contains', q, 'area', round(poly.area, 1))
