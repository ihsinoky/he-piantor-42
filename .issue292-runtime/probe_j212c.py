import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def pts_of(sh):
    ps = p.SHAPE_POLY_SET(); sh.TransformToPolygon(ps, 100, False)
    out = []
    for i in range(ps.OutlineCount()):
        c = ps.Outline(i)
        out.append([(round(c.CPoint(j).x / 1e6, 3), round(c.CPoint(j).y / 1e6, 3)) for j in range(c.PointCount())])
    return out
for f in b.GetFootprints():
    if f.GetReference() == 'J2':
        for pad in f.Pads():
            if pad.GetNumber() == '12':
                print('J2.12 poly:', pts_of(pad.GetEffectiveShape(p.F_Cu)))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        if abs(q.x / 1e6 - 76.29) < 0.3 and abs(q.y / 1e6 - 109.14) < 0.3:
            print('via poly:', pts_of(t.GetEffectiveShape(p.F_Cu)))
