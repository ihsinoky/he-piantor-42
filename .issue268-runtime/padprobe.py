import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
for fp in b.GetFootprints():
    if fp.GetReference() == 'J_WING':
        print('fp layer:', fp.GetLayerName(), 'flipped:', fp.IsFlipped(), 'rot:', fp.GetOrientationDegrees())
        for pad in fp.Pads():
            ls = pad.GetLayerSet()
            print(' pad', pad.GetNumber(), 'GetLayer:', pad.GetLayer(), p.GetStandardLayerName(pad.GetLayer()) if hasattr(p,'GetStandardLayerName') else '', 'layerset F:', ls.Contains(p.F_Cu), 'B:', ls.Contains(p.B_Cu), 'size:', pad.GetSize().x/1e6, pad.GetSize().y/1e6, 'rot:', pad.GetOrientationDegrees())
        break
