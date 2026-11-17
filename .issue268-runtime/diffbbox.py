import pcbnew as p
from collections import Counter, defaultdict
mm = lambda v: v/1e6
def copper(path):
    b = p.LoadBoard(path); c = Counter()
    for t in b.GetTracks():
        s, e = t.GetStart(), t.GetEnd()
        if isinstance(t, p.PCB_VIA): c[(t.GetNetname(), round(mm(s.x),2), round(mm(s.y),2), round(mm(s.x),2), round(mm(s.y),2))] += 1
        else: c[(t.GetNetname(), round(mm(s.x),2), round(mm(s.y),2), round(mm(e.x),2), round(mm(e.y),2))] += 1
    return c
c3 = copper('/home/hatch/workspace/projects/he-piantor-42/hardware/kicad/qualification/issue-182-matrix-rev3/board/m1-matrix18.kicad_pcb')
c4 = copper('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')
bb = defaultdict(lambda: [1e9,1e9,-1e9,-1e9])
for c, sgn in ((c4-c3, 0), (c3-c4, 0)):
    for (n, x1, y1, x2, y2), v in c.items():
        b = bb[n]
        b[0]=min(b[0],x1,x2); b[1]=min(b[1],y1,y2); b[2]=max(b[2],x1,x2); b[3]=max(b[3],y1,y2)
for n in sorted(bb):
    b = bb[n]; print('%s x %.2f..%.2f  y %.2f..%.2f' % (n, b[0], b[2], b[1], b[3]))
