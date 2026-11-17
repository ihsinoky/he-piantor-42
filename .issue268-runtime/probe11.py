import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
for fp in b.GetFootprints():
    if fp.GetReference() != 'U_MUX_C': continue
    pos = fp.GetPosition()
    print('U_MUX_C at (%.2f,%.2f) layer %s rot %.0f' % (mm(pos.x), mm(pos.y), fp.GetLayerName(), fp.GetOrientationDegrees()))
    for pad in fp.Pads():
        q = pad.GetPosition()
        print('  pad %s %s (%.2f,%.2f) F:%s B:%s' % (pad.GetNumber(), pad.GetNetname(), mm(q.x), mm(q.y), pad.IsOnLayer(p.F_Cu), pad.IsOnLayer(p.B_Cu)))
