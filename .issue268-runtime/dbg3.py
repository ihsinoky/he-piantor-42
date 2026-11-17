import pcbnew as p
mm = lambda v: v/1e6
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
for t in b.GetTracks():
    if t.GetNetname() != 'HALL_5V' or isinstance(t, p.PCB_VIA): continue
    s, e = t.GetStart(), t.GetEnd()
    x1, x2, y1, y2 = mm(s.x), mm(e.x), mm(s.y), mm(e.y)
    if (x1 - 96.9) * (x2 - 96.9) < 0 and 110 < min(y1, y2) and max(y1, y2) < 135:
        print('crossing:', t.GetLayerName(), (round(x1,2), round(y1,2)), (round(x2,2), round(y2,2)), 'w', mm(t.GetWidth()))
    if (x1 - 108.0) * (x2 - 108.0) < 0 and 110 < min(y1, y2) and max(y1, y2) < 135:
        print('crossing108:', t.GetLayerName(), (round(x1,2), round(y1,2)), (round(x2,2), round(y2,2)), 'w', mm(t.GetWidth()))
