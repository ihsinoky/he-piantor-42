import pcbnew as p
SRC = '/home/hatch/workspace/projects/he-piantor-matrix4/hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
b = p.LoadBoard(SRC)
def mm(v): return v/1e6
jw = next(fp for fp in b.GetFootprints() if fp.GetReference() == 'J_WING')
netcode = b.GetNetInfo().GetNetItem('GND')
n = 0
for pad in jw.Pads():
    if pad.GetNetname() != 'GND': continue
    q = pad.GetPosition(); x, y = mm(q.x), mm(q.y)
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(p.FromMM(x), p.FromMM(y)))
    t.SetEnd(p.VECTOR2I(p.FromMM(x), p.FromMM(131.0)))
    t.SetWidth(p.FromMM(0.3)); t.SetLayer(p.B_Cu); t.SetNet(netcode)
    b.Add(t); n += 1
    print('stub at x', x)
b.Save(SRC)
print('added', n, 'GND pad stubs')
