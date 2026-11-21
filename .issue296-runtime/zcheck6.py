import sys, json
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/python3/dist-packages")
import pcbnew, numpy as np
T = json.load(open("/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime/zcheck_transform.json"))
R = np.array(T["R"]); t = np.array(T["t"])
def to_asm(p): return R @ np.array(p) + t
quad = [(78.01,20.58),(81.26,22.46),(63.11,53.90),(59.87,52.02)]
def pip(pt, poly):
    x, y = pt; inside = False; n = len(poly)
    for i in range(n):
        x1,y1 = poly[i]; x2,y2 = poly[(i+1)%n]
        if (y1>y)!=(y2>y):
            if x < (x2-x1)*(y-y1)/(y2-y1)+x1: inside = not inside
    return inside
B = "/home/hatch/workspace/projects/he-piantor-wwing-review/hardware/kicad/qualification/issue-299-wwing/17R/wwing-17r.kicad_pcb"
b = pcbnew.LoadBoard(B)
print("== footprints with >=1 pad inside overlap quad (board coords) ==")
for fp in b.GetFootprints():
    hits = 0
    for p in fp.Pads():
        pos = p.GetPosition()
        if pip((pos.x/1e6, pos.y/1e6), quad): hits += 1
    if hits:
        c = fp.GetPosition()
        print("%-8s %-28s layer %s pads-in %d/%d centre-board (%.2f,%.2f) centre-asm (%.2f,%.2f)" % (
            fp.GetReference(), fp.GetValue(), "B" if fp.GetLayer()==pcbnew.B_Cu else "F",
            hits, len(fp.Pads()), c.x/1e6, c.y/1e6, *to_asm((c.x/1e6, c.y/1e6))))
print("== track segments intersecting quad, by net ==")
from collections import Counter
cnt = Counter(); tot = Counter()
def seg_int_quad(a, bq):
    # sample: endpoints in, or segment crosses quad edges (approx via dense sampling)
    for s in np.linspace(0,1,25):
        if pip(tuple(a+(bq-a)*s), quad): return True
    return False
for tr in b.GetTracks():
    if tr.Type() == pcbnew.PCB_TRACE_T:
        a = np.array((tr.GetStart().x/1e6, tr.GetStart().y/1e6)); e = np.array((tr.GetEnd().x/1e6, tr.GetEnd().y/1e6))
        tot[tr.GetNetname()] += 1
        if seg_int_quad(a, e): cnt[tr.GetNetname()] += 1
print("intersecting:", dict(cnt))
print("== vias inside quad ==")
nv = 0
for tr in b.GetTracks():
    if tr.Type() == pcbnew.PCB_VIA_T:
        pos = tr.GetPosition()
        if pip((pos.x/1e6, pos.y/1e6), quad): nv += 1
print("vias in quad:", nv)
