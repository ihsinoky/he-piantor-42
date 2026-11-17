import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
for t in b.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
    if t.GetLayerName() != 'B.Cu': continue
    if all(94 <= x <= 106 and 128.5 <= y <= 132.2 for x, y in pts):
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK'
        print('%s %s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f' % (kind, t.GetNetname(), pts[0][0], pts[0][1], pts[1][0], pts[1][1], mm(t.GetWidth()) if kind=='TRK' else 0.6))
