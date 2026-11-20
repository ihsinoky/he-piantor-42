import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def polys(sh):
    ps = p.SHAPE_POLY_SET(); sh.TransformToPolygon(ps, 100, False)
    out = []
    for i in range(ps.OutlineCount()):
        c = ps.Outline(i)
        out.append([(c.CPoint(j).x / 1e6, c.CPoint(j).y / 1e6) for j in range(c.PointCount())])
    return out
from shapely.geometry import Polygon
padpoly = None
for f in b.GetFootprints():
    if f.GetReference() == 'JPAD':
        for pad in f.Pads():
            if pad.GetNumber() == '5':
                print('JPAD.5 shape type:', pad.GetShape(), 'size', pad.GetSize().x / 1e6, pad.GetSize().y / 1e6, 'rot', pad.GetOrientationDegrees())
                padpoly = Polygon(polys(pad.GetEffectiveShape(p.F_Cu))[0])
for t in b.GetTracks():
    if t.GetNetname() == 'PAD_SCL' and not isinstance(t, p.PCB_VIA):
        s, e = t.GetStart(), t.GetEnd()
        if abs(s.x / 1e6 - 112.2) < 0.01:
            tp = Polygon(polys(t.GetEffectiveShape(p.F_Cu))[0])
            print('track-pad intersection area:', round(tp.intersection(padpoly).area, 4))
