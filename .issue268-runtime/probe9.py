import sys
import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
net, cx, cy, r, lay = sys.argv[1], float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4]), sys.argv[5]
for t in b.GetTracks():
    if t.GetNetname() != net: continue
    if lay != 'ALL' and t.GetLayerName() != lay: continue
    bb = t.GetBoundingBox()
    if mm(bb.GetRight()) < cx-r or mm(bb.GetLeft()) > cx+r or mm(bb.GetBottom()) < cy-r or mm(bb.GetTop()) > cy+r: continue
    s, e = t.GetStart(), t.GetEnd()
    kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK'
    print(' %s %s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f' % (kind, t.GetLayerName(), mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()) if kind == 'TRK' else 0.6))
for fp in b.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() != net: continue
        pos = pad.GetPosition(); x, y = mm(pos.x), mm(pos.y)
        if abs(x-cx) <= r and abs(y-cy) <= r:
            print(' PAD %s.%s (%.2f,%.2f) F:%s B:%s' % (fp.GetReference(), pad.GetNumber(), x, y, pad.IsOnLayer(p.F_Cu), pad.IsOnLayer(p.B_Cu)))
