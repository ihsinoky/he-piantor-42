import math, sys
import pcbnew as p
MM = 1e6
b = p.LoadBoard("hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb")
P0 = (159.808, 104.396)
for d in b.GetDrawings():
    if d.GetLayer() != p.Edge_Cuts:
        continue
    s = (d.GetStart().x / MM, d.GetStart().y / MM); e = (d.GetEnd().x / MM, d.GetEnd().y / MM)
    if min(math.dist(P0, s), math.dist(P0, e)) < 7.0:
        kind = {0: "SEG", 2: "ARC"}.get(d.GetShape(), str(d.GetShape()))
        print(f"{kind} ({s[0]:.4f},{s[1]:.4f}) -> ({e[0]:.4f},{e[1]:.4f}) len={math.dist(s,e):.4f}")
