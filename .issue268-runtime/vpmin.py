import pcbnew as p, math
mm = lambda v: v/1e6
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
vias = []
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        s = t.GetStart(); vias.append((mm(s.x), mm(s.y), mm(t.GetWidth())/2, t.GetNetname()))
pads = []
for fp in b.GetFootprints():
    for pad in fp.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        pads.append((mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y), pad.GetOrientation().AsDegrees(), pad.GetNetname(), fp.GetReference()+'.'+pad.GetNumber()))
best_diff, best_same = (9e9, None), (9e9, None)
for vx, vy, vr, vn in vias:
    for px, py, sx, sy, rot, pn, ref in pads:
        dx0, dy0 = vx-px, vy-py
        if abs(dx0) > 3 or abs(dy0) > 3: continue
        a = math.radians(-rot)
        lx, ly = dx0*math.cos(a)-dy0*math.sin(a), dx0*math.sin(a)+dy0*math.cos(a)
        gap = math.hypot(max(abs(lx)-sx/2, 0.0), max(abs(ly)-sy/2, 0.0)) - vr
        rec = (round(gap, 4), vn, ref, pn, round(vx, 2), round(vy, 2))
        if vn != pn and gap < best_diff[0]: best_diff = rec
        if vn == pn and gap < best_same[0]: best_same = rec
print('min different-net:', best_diff)
print('min same-net:', best_same)
