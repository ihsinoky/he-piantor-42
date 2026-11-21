import sys, json
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr/lib/python3/dist-packages")
import pcbnew, numpy as np

B = "/home/hatch/workspace/projects/he-piantor-wwing-review/hardware/kicad/qualification/issue-299-wwing/17R/wwing-17r.kicad_pcb"
b = pcbnew.LoadBoard(B)
# board outline points
pts = []
for d in b.GetDrawings():
    if d.GetLayer() == pcbnew.Edge_Cuts:
        s = d.GetShape() if hasattr(d, "GetShape") else None
        pts.append((d.GetStart().x/1e6, d.GetStart().y/1e6))
        pts.append((d.GetEnd().x/1e6, d.GetEnd().y/1e6))
bp = np.array(sorted(set(pts)))
asm = json.load(open("/home/hatch/workspace/projects/he-piantor-case296b/.issue296-runtime/wing17r-outline-asm.json"))
print("asm json type:", type(asm), list(asm.keys())[:5] if isinstance(asm, dict) else len(asm))
