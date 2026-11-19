import pcbnew as p
from shapely.geometry import Polygon
def polys(sh):
    ps = p.SHAPE_POLY_SET(); sh.TransformToPolygon(ps, 100, False)
    c = ps.Outline(0)
    return Polygon([(c.CPoint(j).x / 1e6, c.CPoint(j).y / 1e6) for j in range(c.PointCount())])
for tag, path in [('TREE', 'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'),
                  ('WORK', '.issue292-runtime/wmain-work.kicad_pcb')]:
    b = p.LoadBoard(path)
    padpoly = None
    for f in b.GetFootprints():
        if f.GetReference() == 'J2':
            for pad in f.Pads():
                if pad.GetNumber() == '12':
                    padpoly = polys(pad.GetEffectiveShape(p.F_Cu))
                    print(tag, 'J2.12 net', pad.GetNetname())
    for t in b.GetTracks():
        if isinstance(t, p.PCB_VIA):
            q = t.GetPosition()
            if abs(q.x / 1e6 - 76.29) < 0.3 and abs(q.y / 1e6 - 109.14) < 0.3:
                vp = polys(t.GetEffectiveShape(p.F_Cu))
                print(tag, 'via', t.GetNetname(), (round(q.x/1e6, 2), round(q.y/1e6, 2)), 'overlap with J2.12:', round(vp.intersection(padpoly).area, 4))
