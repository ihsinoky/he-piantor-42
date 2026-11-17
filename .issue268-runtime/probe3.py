import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
print('== VIAS x 94..108, y 127..134')
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA): continue
    s = t.GetStart(); x, y = mm(s.x), mm(s.y)
    if 94 <= x <= 108 and 127 <= y <= 134:
        print(' VIA %s (%.2f,%.2f)' % (t.GetNetname(), x, y))
print('== F.Cu TRK x 94..108, y 128..134')
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA) or t.GetLayerName() != 'F.Cu': continue
    s, e = t.GetStart(), t.GetEnd()
    pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
    if all(94 <= x <= 108 and 128 <= y <= 134 for x, y in pts):
        print(' TRK %s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f' % (t.GetNetname(), pts[0][0], pts[0][1], pts[1][0], pts[1][1], mm(t.GetWidth())))
