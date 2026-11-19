import pcbnew as p
tb = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm2(v): return v / 1e6
for t in tb.GetTracks():
    if t.GetNetname() != 'GND': continue
    if isinstance(t, p.PCB_VIA):
        v = t.GetPosition(); x, y = mm2(v.x), mm2(v.y)
        if 72.5 < x < 75.0 and 116.5 < y < 119.0: print('tree GND VIA', f'{x:.2f},{y:.2f}')
    else:
        s, e = t.GetStart(), t.GetEnd()
        bx = (min(mm2(s.x), mm2(e.x)), min(mm2(s.y), mm2(e.y)), max(mm2(s.x), mm2(e.x)), max(mm2(s.y), mm2(e.y)))
        if bx[2] < 72.5 or bx[0] > 75.0 or bx[3] < 116.5 or bx[1] > 119.0: continue
        print('tree GND TRK', f"({mm2(s.x):.2f},{mm2(s.y):.2f})-({mm2(e.x):.2f},{mm2(e.y):.2f})", 'L', t.GetLayer())
