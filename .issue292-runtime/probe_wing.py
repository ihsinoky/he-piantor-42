import pcbnew as p
for name in ('main.kicad_pcb', 'routed.kicad_pcb', 'input.kicad_pcb'):
    path = f'hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/{name}'
    b = p.LoadBoard(path)
    if b is None: print(name, 'LOAD FAIL'); continue
    po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
    ch = po.Outline(0); ps = p.SHAPE_POLY_SET(); ch.TransformToPolygon(ps, 100, False)
    c2 = ps.Outline(0)
    pts = [(c2.CPoint(i).x/1e6, c2.CPoint(i).y/1e6) for i in range(c2.PointCount())]
    xs = [q[0] for q in pts]; ys = [q[1] for q in pts]
    print(name, 'verts', len(pts), 'X', round(min(xs),2), round(max(xs),2), 'Y', round(min(ys),2), round(max(ys),2))
