import pcbnew as p
SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
mm = lambda v: v/1e6
b = p.LoadBoard(SRC)
for t in list(b.GetTracks()):
    if isinstance(t, p.PCB_VIA) and t.GetNetname() == 'MUX_A2':
        s = t.GetStart()
        if abs(mm(s.x) - 103.60) < 0.01 and abs(mm(s.y) - 128.40) < 0.01:
            b.RemoveNative(t); print('deleted A2 via only (B.Cu joint remains)')
b.Save(SRC); print('saved')
