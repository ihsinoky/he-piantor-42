import pcbnew
b = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-wmatrix/hardware/kicad/qualification/issue-288-wmatrix/wmatrix.kicad_pcb')
for t in b.GetTracks():
    if isinstance(t, pcbnew.PCB_VIA): continue
    a, e = t.GetStart(), t.GetEnd()
    ax, ay, bx, by = a.x/1e6, a.y/1e6, e.x/1e6, e.y/1e6
    if 131 < ax < 135.5 and 99 < ay < 110 or 131 < bx < 135.5 and 99 < by < 110:
        print(t.GetNetname(), 'F' if t.GetLayer() == pcbnew.F_Cu else 'B', f'({ax:.2f},{ay:.2f})->({bx:.2f},{by:.2f}) w={t.GetWidth()/1e6}')
