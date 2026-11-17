import pcbnew
B = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-matrix4/hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
def mm(v): return v/1e6
for t in B.GetTracks():
    s, e = t.GetStart(), t.GetEnd()
    x0, x1 = sorted([mm(s.x), mm(e.x)]); y0, y1 = sorted([mm(s.y), mm(e.y)])
    if x1 < 97.2 or x0 > 99.4 or y1 < 128.8 or y0 > 131.3: continue
    kind = 'VIA' if isinstance(t, pcbnew.PCB_VIA) else 'seg'
    print(f"{t.GetNetname():12s} {kind} {'F' if t.GetLayer()==0 else 'B'} ({x0:.2f},{y0:.2f})-({x1:.2f},{y1:.2f}) w={mm(t.GetWidth()):.2f}")
for fp in B.GetFootprints():
    for pad in fp.Pads():
        q = pad.GetPosition(); x, y = mm(q.x), mm(q.y)
        if 97.2 <= x <= 99.4 and 128.8 <= y <= 131.3:
            ls = pad.GetLayerSet()
            lay = 'F' if ls.Contains(pcbnew.F_Cu) else ('B' if ls.Contains(pcbnew.B_Cu) else '?')
            print(f"PAD {fp.GetReference():8s} {pad.GetNumber():>3s} net={pad.GetNetname():12s} {lay} ({x:.2f},{y:.2f})")
