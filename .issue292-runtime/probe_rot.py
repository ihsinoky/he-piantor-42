import pcbnew as p, math
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm(v): return v/1e6
for f in b.GetFootprints():
    if f.GetReference() == 'J3':
        for pad in f.Pads():
            if pad.GetNumber() == '10':
                sh = pad.GetEffectiveShape(p.F_Cu)
                ps = p.SHAPE_POLY_SET(); sh.TransformToPolygon(ps, 100, False)
                c = ps.Outline(0)
                pts = [(round(c.CPoint(i).x/1e6, 3), round(c.CPoint(i).y/1e6, 3)) for i in range(c.PointCount())]
                print('KiCad effective shape points:', pts)
                q = pad.GetPosition(); cx, cy = mm(q.x), mm(q.y)
                th = math.radians(pad.GetOrientationDegrees()); co, si = math.cos(th), math.sin(th)
                w, h = 0.3, 1.3
                mine = [(round(cx + dx*co - dy*si, 3), round(cy + dx*si + dy*co, 3)) for dx, dy in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))]
                conj = [(round(cx + dx*co + dy*si, 3), round(cy - dx*si + dy*co, 3)) for dx, dy in ((-w/2,-h/2),(w/2,-h/2),(w/2,h/2),(-w/2,h/2))]
                print('mine (current):', mine)
                print('conjugate     :', conj)
