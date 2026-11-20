import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb')
for f in b.GetFootprints():
    if f.GetReference() == 'J2':
        for pad in f.Pads():
            if pad.GetNumber() == '12':
                q = pad.GetPosition()
                print('J2.12 centre', q.x / 1e6, q.y / 1e6, 'layers F?', pad.IsOnLayer(p.F_Cu))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        if abs(q.x / 1e6 - 76.29) < 0.3 and abs(q.y / 1e6 - 109.14) < 0.3:
            print('via type', t.GetViaType(), 'top', t.TopLayer(), 'bottom', t.BottomLayer(), 'net', t.GetNetname())
