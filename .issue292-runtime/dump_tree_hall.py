import pcbnew as p
tb = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm(v): return v / 1e6
LAY = {0: 'F', 2: 'I2', 31: 'B'}
for t in tb.GetTracks():
    if t.GetNetname() != 'HALL_3V3': continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition(); x, y = mm(v.x), mm(v.y)
        if 126.5 < x < 130.5 and 125.5 < y < 131.5: print('tree VIA', f'{x:.2f},{y:.2f}')
    else:
        s, e = t.GetStart(), t.GetEnd()
        bx = (min(mm(s.x), mm(e.x)), min(mm(s.y), mm(e.y)), max(mm(s.x), mm(e.x)), max(mm(s.y), mm(e.y)))
        if bx[2] < 126.5 or bx[0] > 130.5 or bx[3] < 125.5 or bx[1] > 131.5: continue
        print('tree TRK', LAY.get(t.GetLayer(), t.GetLayer()), f"({mm(s.x):.2f},{mm(s.y):.2f})-({mm(e.x):.2f},{mm(e.y):.2f})")
for fp in tb.GetFootprints():
    if fp.GetReference() in ('CHOUT', 'TP3'):
        for pad in fp.Pads():
            pos = pad.GetPosition()
            print('tree PAD', fp.GetReference(), pad.GetNumber(), f"{mm(pos.x):.2f},{mm(pos.y):.2f}", 'size', f"{mm(pad.GetSize().x):.2f}x{mm(pad.GetSize().y):.2f}")
