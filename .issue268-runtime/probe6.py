import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
for lay in ('B.Cu', 'F.Cu'):
    print('==', lay)
    for t in b.GetTracks():
        if t.GetNetname() != 'MUX_A2' or t.GetLayerName() != lay: continue
        bb = t.GetBoundingBox()
        if mm(bb.GetRight()) < 107 or mm(bb.GetLeft()) > 121 or mm(bb.GetBottom()) < 121 or mm(bb.GetTop()) > 129: continue
        s, e = t.GetStart(), t.GetEnd()
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK'
        print(' %s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f' % (kind, mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()) if kind == 'TRK' else 0.6))
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != 'MUX_A2': continue
            pos = pad.GetPosition(); x, y = mm(pos.x), mm(pos.y)
            if 107 <= x <= 121 and 121 <= y <= 129:
                print(' PAD %s.%s (%.2f,%.2f) %s' % (fp.GetReference(), pad.GetNumber(), x, y, 'B' if pad.IsOnLayer(p.B_Cu) and not pad.IsOnLayer(p.F_Cu) else 'F'))
