import pcbnew as p
def mm(v): return v / 1e6
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
n = 0
for t in b.GetTracks():
    if t.GetNetname() != 'PAD_SCL': continue
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        if mm(q.y) > 128.9: print('SCL via south', mm(q.x), mm(q.y)); n += 1
    else:
        s, e = t.GetStart(), t.GetEnd()
        if max(mm(s.y), mm(e.y)) > 128.95: print('SCL trk south L', t.GetLayer(), (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))); n += 1
print('SCL items south of 128.9:', n)
