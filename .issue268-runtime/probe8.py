import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
print('== all nets F.Cu near GND gap (83..88, 125.5..129)')
for t in b.GetTracks():
    if t.GetLayerName() != 'F.Cu' or t.GetNetname() == 'GND': continue
    bb = t.GetBoundingBox()
    if mm(bb.GetRight()) < 83 or mm(bb.GetLeft()) > 88 or mm(bb.GetBottom()) < 125.5 or mm(bb.GetTop()) > 129: continue
    s, e = t.GetStart(), t.GetEnd()
    print(' %s (%.2f,%.2f)-(%.2f,%.2f)' % (t.GetNetname(), mm(s.x), mm(s.y), mm(e.x), mm(e.y)))
for fp in b.GetFootprints():
    for pad in fp.Pads():
        pos = pad.GetPosition(); x, y = mm(pos.x), mm(pos.y)
        if 83 <= x <= 88 and 125.5 <= y <= 129 and pad.GetNetname() != 'GND':
            print(' PAD %s.%s %s (%.2f,%.2f) F:%s' % (fp.GetReference(), pad.GetNumber(), pad.GetNetname(), x, y, pad.IsOnLayer(p.F_Cu)))
print('== all nets B.Cu near A2 gap (110..112.5, 124.5..126.5)')
for t in b.GetTracks():
    if t.GetLayerName() != 'B.Cu' or t.GetNetname() == 'MUX_A2': continue
    bb = t.GetBoundingBox()
    if mm(bb.GetRight()) < 110 or mm(bb.GetLeft()) > 112.5 or mm(bb.GetBottom()) < 124.5 or mm(bb.GetTop()) > 126.5: continue
    s, e = t.GetStart(), t.GetEnd()
    print(' %s (%.2f,%.2f)-(%.2f,%.2f)' % (t.GetNetname(), mm(s.x), mm(s.y), mm(e.x), mm(e.y)))
