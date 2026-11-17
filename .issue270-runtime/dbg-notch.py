import json, sys
import numpy as np
from shapely.geometry import Point
sys.path.insert(0, ".issue270-runtime")
d = json.load(open(".issue270-runtime/notch2d.json"))["17mm-left"]
els = d["elements_case"]
print("delta", d["delta"], "seam", d["seam_poly_dist"], "at", d["seam_min_at_case"])
for i, e in enumerate(els):
    print(i, e[0], [tuple(round(v,3) for v in p) if isinstance(p, list) else p for p in e[1:]])
pt = Point(d["seam_min_at_case"])
for i, e in enumerate(els):
    if e[0] == "line":
        from shapely.geometry import LineString
        print("dist to el", i, round(LineString([e[1], e[2]]).distance(pt), 4))
