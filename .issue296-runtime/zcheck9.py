import sys, json
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/python3/dist-packages")
import pcbnew, numpy as np
T = json.load(open("/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime/zcheck_transform.json"))
R = np.array(T["R"]); t = np.array(T["t"])
def to_board(p): return R.T @ (np.array(p) - t)
corners = [(14.0,-8.0),(24.0,-8.0),(24.0,-2.0),(14.0,-2.0)]
quad = [tuple(to_board(p)) for p in corners]
print("corner quad in board coords:", [(round(x,2), round(y,2)) for x, y in quad])
def pip(pt, poly):
    x, y = pt; inside = False; n = len(poly)
    for i in range(n):
        x1,y1 = poly[i]; x2,y2 = poly[(i+1)%n]
        if (y1>y)!=(y2>y):
            if x < (x2-x1)*(y-y1)/(y2-y1)+x1: inside = not inside
    return inside
B = "/home/hatch/workspace/projects/he-piantor-wwing-review/hardware/kicad/qualification/issue-299-wwing/17R/wwing-17r.kicad_pcb"
b = pcbnew.LoadBoard(B)
found = False
for fp in b.GetFootprints():
    hits = sum(1 for p in fp.Pads() if pip((p.GetPosition().x/1e6, p.GetPosition().y/1e6), quad))
    if hits:
        print("FP %-8s %s pads-in %d/%d" % (fp.GetReference(), fp.GetValue(), hits, len(fp.Pads()))); found = True
if not found: print("no footprint pads in corner quad")
from collections import Counter
cnt = Counter()
for tr in b.GetTracks():
    if tr.Type() == pcbnew.PCB_TRACE_T:
        a = (tr.GetStart().x/1e6, tr.GetStart().y/1e6); e = (tr.GetEnd().x/1e6, tr.GetEnd().y/1e6)
        for s in np.linspace(0,1,15):
            if pip((a[0]+(e[0]-a[0])*s, a[1]+(e[1]-a[1])*s), quad): cnt[tr.GetNetname()] += 1; break
print("tracks through corner quad:", dict(cnt))
