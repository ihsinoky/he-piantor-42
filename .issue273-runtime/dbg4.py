import json, math, sys
from pathlib import Path
import numpy as np
import pcbnew as p
from shapely.geometry import LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
SRT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
sys.path.insert(0, str(SRT))
from notchain import wing_xf_factory
Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
ND = json.loads((SRT / "notch2d.json").read_text())
variant = "17mm-left"; side = "left"
b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
fwd, inv, jw = wing_xf_factory(b5, side)
def pt_case(pt):
    q = shp_translate(Point(pt), xoff=-jw[0], yoff=-jw[1])
    q = shp_rotate(q, 30.5, origin=(0, 0))
    q = shp_translate(q, xoff=-27.0, yoff=-37.5)
    return (q.x, q.y)
els_nd = ND[variant]["elements_case"]
chain_union = unary_union([LineString([els_nd[0][1], els_nd[0][2]]),
                           LineString([els_nd[2][1], els_nd[2][2]]),
                           LineString([els_nd[4][1], els_nd[4][2]])])
for d in b5.GetDrawings():
    if d.GetLayer() != p.Edge_Cuts:
        continue
    s = pt_case((d.GetStart().x / MM, d.GetStart().y / MM))
    e = pt_case((d.GetEnd().x / MM, d.GetEnd().y / MM))
    L = math.dist(s, e)
    if L >= 10.0:
        print(f"shape {d.GetShape()} len {L:.2f} {tuple(round(v,2) for v in s)} -> {tuple(round(v,2) for v in e)} dist2chain {LineString([s,e]).distance(chain_union):.3f}")
