import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
def mm(v): return v/1e6
for t in b.GetTracks():
    if t.GetNetname() in ('MUX_A2', 'MUX_A1'):
        s, e = t.GetStart(), t.GetEnd()
        pts = [(round(mm(s.x),2), round(mm(s.y),2)), (round(mm(e.x),2), round(mm(e.y),2))]
        if any(70 < x < 80 and 105 < y < 118 for x, y in pts) or any(118 < x < 130 and 105 < y < 118 for x, y in pts):
            print(t.GetNetname(), 'VIA' if isinstance(t, p.PCB_VIA) else t.GetLayer(), pts)
