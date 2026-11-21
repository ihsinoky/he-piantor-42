import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
import gndcheck as gc
from shapely.ops import unary_union
path, netname = sys.argv[1], sys.argv[2]
layer = pcbnew.B_Cu if netname == "GND" else pcbnew.F_Cu
def area(b):
    for z in b.Zones():
        if z.GetNetname() == netname:
            ps = gc.polys_from_set(z.GetFilledPolysList(layer))
            return round(unary_union(ps).area, 4) if ps else 0.0
b = pcbnew.LoadBoard(path)
print("before:", area(b))
zs = [z for z in b.Zones() if z.GetNetname() == netname]
f = pcbnew.ZONE_FILLER(b)
f.Fill(zs)
print("after:", area(b))
pcbnew.SaveBoard(path, b)
b2 = pcbnew.LoadBoard(path)
print("reloaded:", area(b2))
