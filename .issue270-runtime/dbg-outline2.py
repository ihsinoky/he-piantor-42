import sys, math, collections
sys.path.insert(0, ".issue270-runtime")
import pcbnew as p
from geom2b import xy
MM = 1e6
b = p.LoadBoard("hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
ends = collections.Counter()
nseg = narc = 0
for d in b.GetDrawings():
    if d.GetLayer() != p.Edge_Cuts: continue
    if d.GetShape() == p.SHAPE_T_ARC:
        narc += 1
        ends[(round(d.GetStart().x/MM,3), round(d.GetStart().y/MM,3))] += 1
        ends[(round(d.GetEnd().x/MM,3), round(d.GetEnd().y/MM,3))] += 1
    else:
        nseg += 1
        ends[(round(d.GetStart().x/MM,3), round(d.GetStart().y/MM,3))] += 1
        ends[(round(d.GetEnd().x/MM,3), round(d.GetEnd().y/MM,3))] += 1
print("segments", nseg, "arcs", narc)
odd = {k: v for k, v in ends.items() if v != 2}
print("endpoints with count != 2:", odd)
