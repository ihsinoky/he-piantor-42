import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
for t in b.GetTracks():
    if not isinstance(t, p.PCB_VIA): continue
    s = t.GetStart(); x, y = mm(s.x), mm(s.y)
    if 96 <= x <= 104 and 129 <= y <= 132:
        print('VIA %s (%.2f,%.2f)' % (t.GetNetname(), x, y))
