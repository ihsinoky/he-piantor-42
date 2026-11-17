import sys
import pcbnew as p
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
X0, X1, Y0, Y1 = float(sys.argv[1]), float(sys.argv[2]), float(sys.argv[3]), float(sys.argv[4])
layer = sys.argv[5] if len(sys.argv) > 5 else 'B.Cu'
for t in b.GetTracks():
    if t.GetLayerName() != layer: continue
    s, e = t.GetStart(), t.GetEnd()
    pts = [(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]
    if all(X0 <= x <= X1 and Y0 <= y <= Y1 for x, y in pts):
        kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK'
        print('%s %s (%.2f,%.2f)-(%.2f,%.2f) w=%.2f' % (kind, t.GetNetname(), pts[0][0], pts[0][1], pts[1][0], pts[1][1], mm(t.GetWidth()) if kind == 'TRK' else 0.6))
