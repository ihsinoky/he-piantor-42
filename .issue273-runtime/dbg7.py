import json
from pathlib import Path
from shapely.geometry import Polygon
RT = Path(".issue273-runtime")
old = {k: Polygon(v) for k, v in json.loads((RT / "rev5-outlines.json").read_text()).items()}
nd = json.loads((RT / "notch2e.json").read_text())
res = {}
for v in ("17mm-left", "17mm-right"):
    o = old[v]; n = Polygon(nd[v]["wing_new_case"])
    def parts(poly):
        gs = list(poly.geoms) if poly.geom_type == "MultiPolygon" else [poly]
        return [{"area": g.area, "bounds": list(g.bounds),
                 "xy": [list(c) for c in g.exterior.coords]} for g in gs if not g.is_empty]
    res[v] = {"removed": parts(o.difference(n)), "added": parts(n.difference(o))}
(RT / "delta-parts.json").write_text(json.dumps(res))
for v, d in res.items():
    for kind in ("removed", "added"):
        for g in d[kind]:
            print(v, kind, round(g["area"], 2), tuple(round(b, 1) for b in g["bounds"]))
