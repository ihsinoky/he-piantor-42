import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
import gndcheck as gc
from shapely.ops import unary_union

def fills(path):
    b = pcbnew.LoadBoard(path)
    out = {}
    for z in b.Zones():
        for layer in (pcbnew.F_Cu, pcbnew.B_Cu):
            if not z.IsOnLayer(layer):
                continue
            ps = gc.polys_from_set(z.GetFilledPolysList(layer))
            if ps:
                out[(z.GetNetname(), layer)] = unary_union(ps)
    return out

fa = fills(sys.argv[1])
fb = fills(sys.argv[2])
for k in sorted(set(fa) | set(fb)):
    a, b = fa.get(k), fb.get(k)
    if a is None or b is None:
        print(k, "present in one file only")
        continue
    sd = a.symmetric_difference(b)
    if sd.area < 1e-9:
        print(k, "identical", round(a.area, 3))
    else:
        parts = list(sd.geoms) if hasattr(sd, "geoms") else [sd]
        print(k, f"area {a.area:.3f} -> {b.area:.3f}; symdiff {sd.area:.3f} in {len(parts)} parts:")
        for p in parts:
            bb = p.bounds
            print(f"    part area {p.area:.3f} bbox ({bb[0]:.2f},{bb[1]:.2f})-({bb[2]:.2f},{bb[3]:.2f})")
