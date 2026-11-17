import pcbnew as p
from collections import Counter
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
mm = lambda v: v/1e6
LINK = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
c = Counter()
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA) or t.GetNetname() not in LINK: continue
    s, e = t.GetStart(), t.GetEnd()
    key = (t.GetNetname(), t.GetLayerName(), round(mm(s.x), 2), round(mm(s.y), 2), round(mm(e.x), 2), round(mm(e.y), 2))
    c[key] += 1
for k, v in c.items():
    if v > 1: print('x%d' % v, k)
print('--- lane 98.75 B.Cu GND wide:')
for t in b.GetTracks():
    if t.GetNetname() != 'GND' or t.GetLayerName() != 'B.Cu': continue
    bb = t.GetBoundingBox()
    if mm(bb.GetRight()) < 98.0 or mm(bb.GetLeft()) > 99.6 or mm(bb.GetBottom()) < 129.2 or mm(bb.GetTop()) > 131.2: continue
    s, e = t.GetStart(), t.GetEnd()
    kind = 'VIA' if isinstance(t, p.PCB_VIA) else 'TRK'
    print(' %s (%.2f,%.2f)-(%.2f,%.2f)' % (kind, mm(s.x), mm(s.y), mm(e.x), mm(e.y)))
