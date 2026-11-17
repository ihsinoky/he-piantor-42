import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
for lay in ('F.Cu', 'B.Cu'):
    print('== GND', lay)
    for t in b.GetTracks():
        if t.GetNetname() != 'GND' or t.GetLayerName() != lay: continue
        bb = t.GetBoundingBox()
        if mm(bb.GetRight()) < 82 or mm(bb.GetLeft()) > 90 or mm(bb.GetBottom()) < 124 or mm(bb.GetTop()) > 130: continue
        s, e = t.GetStart(), t.GetEnd()
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK'
        print(' %s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f' % (kind, mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()) if kind == 'TRK' else 0.6))
