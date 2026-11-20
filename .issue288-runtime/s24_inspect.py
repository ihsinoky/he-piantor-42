import pcbnew
b = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb')
for fp in b.GetFootprints():
    ref = fp.GetReference()
    if ref.startswith('TP') or ref == 'J_WING' or ref.startswith('U_MUX'):
        p = fp.GetPosition()
        nets = {pad.GetNumber(): pad.GetNetname() for pad in fp.Pads()}
        print(ref, f'({p.x/1e6:.2f},{p.y/1e6:.2f}) rot={fp.GetOrientationDegrees():.0f}', nets)
