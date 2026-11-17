import pcbnew as p
from pathlib import Path
from collections import Counter
MM = 1e6
Q263 = Path("/home/hatch/workspace/projects/he-piantor-wingnotch/hardware/kicad/qualification/issue-263-implementation")
b = p.LoadBoard(str(Q263 / "wing-rev5-17mm-left/main.kicad_pcb"))
c = Counter()
arc = None
for d in b.GetDrawings():
    if d.GetLayer() != p.Edge_Cuts:
        continue
    c[str(d.GetShape())] += 1
    if str(d.GetShape()) in ("2", "ARC") and arc is None:
        arc = d
print("shape census:", dict(c))
if arc is not None:
    print("arc start", arc.GetStart().x / MM, arc.GetStart().y / MM)
    print("arc end", arc.GetEnd().x / MM, arc.GetEnd().y / MM)
    for m in ("GetArcMid", "GetCenter", "GetArcStart", "GetArcEnd", "GetRadius"):
        print(m, hasattr(arc, m))
    try:
        print("arc mid", arc.GetArcMid().x / MM, arc.GetArcMid().y / MM)
    except Exception as e:
        print("GetArcMid failed:", e)
    try:
        print("center", arc.GetCenter().x / MM, arc.GetCenter().y / MM)
    except Exception as e:
        print("GetCenter failed:", e)
