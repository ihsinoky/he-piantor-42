import pcbnew as p
mm = lambda v: v/1e6
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
nv = sum(1 for t in b.GetTracks() if isinstance(t, p.PCB_VIA))
print('via count rev4:', nv)
for fp in b.GetFootprints():
    if fp.GetReference() in ('C_MUX_C', 'TP_W_MUXA'):
        print(fp.GetReference(), 'at (%.2f,%.2f) rot %.0f' % (mm(fp.GetPosition().x), mm(fp.GetPosition().y), fp.GetOrientationDegrees()))
        for pad in fp.Pads():
            pos, sz = pad.GetPosition(), pad.GetSize()
            print('  pad %s %s centre (%.3f,%.3f) size %.3f x %.3f' % (pad.GetNumber(), pad.GetNetname(), mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y)))
