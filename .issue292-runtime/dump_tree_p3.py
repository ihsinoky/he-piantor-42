import pcbnew as p
tb = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm(v): return v / 1e6
LAY = {0: 'F', 2: 'I2', 31: 'B'}
for t in tb.GetTracks():
    if t.GetNetname() != 'PAD_3V3': continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition(); x, y = mm(v.x), mm(v.y)
        if 106.5 < x < 110.5 and 89.5 < y < 95.0: print('tree VIA', f'{x:.2f},{y:.2f}')
    else:
        s, e = t.GetStart(), t.GetEnd()
        bx = (min(mm(s.x), mm(e.x)), min(mm(s.y), mm(e.y)), max(mm(s.x), mm(e.x)), max(mm(s.y), mm(e.y)))
        if bx[2] < 106.5 or bx[0] > 110.5 or bx[3] < 89.5 or bx[1] > 95.0: continue
        print('tree TRK', LAY.get(t.GetLayer(), t.GetLayer()), f"({mm(s.x):.2f},{mm(s.y):.2f})-({mm(e.x):.2f},{mm(e.y):.2f})")
