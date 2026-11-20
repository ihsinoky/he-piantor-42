import build123d as bd, json
import numpy as np
from shapely.geometry import Polygon, Point
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
def load(i): return bd.import_brep(f"{G17}/{i}.brep")
def vol(s):
    if s is None: return 0.0
    try: return s.volume
    except AttributeError: return sum(x.volume for x in s.solids())
# N-TAB solid: board X112..124, Y74..88 -> g17 X12..24, Y4..18, Z raw 7.35..8.55
ntab = bd.Solid.make_box(12, 14, 1.2).moved(bd.Location((12, 4, 7.35)))
for i in (4, 3, 221, 131):
    print(f"N-TAB x {idx[i]['name']}: {vol(ntab.intersect(load(i))):.2f} mm3")
# real placed Wing outline (shapely) - free-space profile north of Main tab:
w = json.load(open("/home/hatch/workspace/projects/he-piantor-wmain2/.issue292-runtime/wing17R.json"))
ch = max(w["chains"], key=len)
f = np.load("/home/hatch/workspace/projects/he-piantor-wmain2/.issue292-runtime/wing-fit.npz")
W = (f["R"] @ np.array(ch).T).T + f["t"] + np.array([100.0, 70.0])
wing = Polygon(W)
print("dist from tab-edge midpoints/corners to WingR:")
for name, p in [("tab centre (100,75.73)", (100,75.73)), ("tab NE corner (102,75.73)", (102,75.73)),
                ("tab NW corner (98,75.73)", (98,75.73)), ("north of tab (100,71)", (100,71)),
                ("north of tab (100,70)", (100,70)), ("NE diag mid (110,88)", (110,88))]:
    print(f"  {name}: {Point(p).distance(wing):.2f}")
