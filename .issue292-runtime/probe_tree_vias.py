import pcbnew as p
tb = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm2(v): return v / 1e6
for t in tb.GetTracks():
    if t.GetNetname() != 'GND' or not isinstance(t, p.PCB_VIA): continue
    v = t.GetPosition(); x, y = mm2(v.x), mm2(v.y)
    if 70 < x < 82 and 107 < y < 116: print('tree GND via', f'{x:.2f},{y:.2f}')
wk = p.LoadBoard('.issue292-runtime/wmain-work.kicad_pcb')
for t in wk.GetTracks():
    if t.GetNetname() != 'GND' or not isinstance(t, p.PCB_VIA): continue
    v = t.GetPosition(); x, y = mm2(v.x), mm2(v.y)
    if 70 < x < 82 and 107 < y < 116: print('work GND via', f'{x:.2f},{y:.2f}')
