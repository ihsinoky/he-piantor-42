import sys, json
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/python3/dist-packages")
import pcbnew
b = pcbnew.LoadBoard("hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb")
segs = []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        s = d.GetStart(); e = d.GetEnd()
        segs.append([[s.x/1e6-100, s.y/1e6-70.0], [e.x/1e6-100, e.y/1e6-70.0]])
json.dump(segs, open(".issue296-runtime/main-outline-asm.json", "w"))
xs = [p[0] for s in segs for p in s]; ys = [p[1] for s in segs for p in s]
print("segments", len(segs), "bbox X", round(min(xs),2), round(max(xs),2), "Y", round(min(ys),2), round(max(ys),2))
# Y span at X=0: collect segment crossings
span = []
for (x1,y1),(x2,y2) in segs:
    if (x1 <= 0 <= x2) or (x2 <= 0 <= x1):
        if x2 != x1:
            t = (0-x1)/(x2-x1); span.append(round(y1 + t*(y2-y1), 2))
print("Y crossings at X=0:", sorted(span))
