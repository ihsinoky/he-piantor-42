import pcbnew
B = pcbnew.LoadBoard('/home/hatch/workspace/projects/he-piantor-matrix4/hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
def mm(v): return v/1e6
print('--- B.Cu tracks intersecting x 94..99.5, y 123..133.5 (non-GND) ---')
for t in B.GetTracks():
    if not isinstance(t, pcbnew.PCB_TRACK) or isinstance(t, pcbnew.PCB_VIA): continue
    if t.GetLayer() != pcbnew.B_Cu: continue
    s, e = t.GetStart(), t.GetEnd()
    x0, x1 = sorted([mm(s.x), mm(e.x)]); y0, y1 = sorted([mm(s.y), mm(e.y)])
    if x1 < 94 or x0 > 99.5 or y1 < 123 or y0 > 133.5: continue
    if t.GetNetname() == 'GND': continue
    print(f"{t.GetNetname():12s} ({x0:.2f},{y0:.2f})-({x1:.2f},{y1:.2f}) w={mm(t.GetWidth()):.2f}")
print('--- B.Cu pads in same box ---')
for fp in B.GetFootprints():
    for pad in fp.Pads():
        if pad.GetLayerSet().Contains(pcbnew.B_Cu) is False: continue
        q = pad.GetPosition(); x, y = mm(q.x), mm(q.y)
        if 94 <= x <= 99.5 and 123 <= y <= 133.5 and pad.GetNetname() != 'GND':
            print(f"{fp.GetReference():8s} pad {pad.GetNumber():>3s} net={pad.GetNetname():12s} ({x:.2f},{y:.2f})")
