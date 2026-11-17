"""Probe copper near the FH12 (x 88..118, y 122..134) for given nets."""
import sys
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
mm = lambda v: v/1e6
nets = sys.argv[1:] or ['GND']
b = p.LoadBoard(SRC)
X0, X1, Y0, Y1 = 88, 118, 122, 134
for net in nets:
    print('==', net)
    for t in b.GetTracks():
        if t.GetNetname() != net: continue
        s, e = t.GetStart(), t.GetEnd()
        pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
        if all(X0 <= x <= X1 and Y0 <= y <= Y1 for x, y in pts):
            kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK'
            print(' %s %s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f' % (kind, t.GetLayerName(), pts[0][0], pts[0][1], pts[1][0], pts[1][1], mm(t.GetWidth())))
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != net: continue
            pos = pad.GetPosition()
            x, y = mm(pos.x), mm(pos.y)
            if X0 <= x <= X1 and Y0 <= y <= Y1:
                print(' PAD %s.%s (%.2f,%.2f) %s' % (fp.GetReference(), pad.GetNumber(), x, y, pad.GetLayerName()))
    for z in b.Zones():
        if z.GetNetname() != net: continue
        bb = z.GetBoundingBox()
        print(' ZONE %s bbox (%.1f,%.1f)-(%.1f,%.1f)' % (z.GetLayerName(), mm(bb.GetLeft()), mm(bb.GetTop()), mm(bb.GetRight()), mm(bb.GetBottom())))
