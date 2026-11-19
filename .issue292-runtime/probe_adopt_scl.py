import pcbnew as p
def mm(v): return v / 1e6
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
LN = {0: 'F', 1: 'I1', 2: 'I2', 31: 'B'}
for t in b.GetTracks():
    if t.GetNetname() != 'PAD_SCL': continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition()
        print('via', (round(mm(v.x), 2), round(mm(v.y), 2)))
    else:
        s, e = t.GetStart(), t.GetEnd()
        cx, cy = (mm(s.x) + mm(e.x)) / 2, (mm(s.y) + mm(e.y)) / 2
        if 68 <= cx <= 78 and 112 <= cy <= 128:
            print('trk', LN.get(t.GetLayer(), t.GetLayer()), (round(mm(s.x), 2), round(mm(s.y), 2)), '->', (round(mm(e.x), 2), round(mm(e.y), 2)), 'w', round(mm(t.GetWidth()), 2))
