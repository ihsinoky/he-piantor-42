import json, math, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, LineString
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
SRT = "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime"
sys.path.insert(0, SRT)
from notchain import wing_xf_factory
Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
Q270W = W / "hardware/kicad/qualification/issue-270-wing-rev6"
Q270M = W / "hardware/kicad/qualification/issue-270-main-rev9/main-rev9"
ND = json.loads(Path(SRT, "notch2d.json").read_text())

def outline(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM)
                    for j in range(ch.PointCount())])

main_case = shp_translate(outline(p.LoadBoard(str(Q270M / "main.kicad_pcb"))),
                          xoff=-100.0, yoff=-70.0)

import json as _json
data = {"main": [list(c) for c in main_case.exterior.coords], "variants": {}}
for variant in ("17mm-left", "17mm-right"):
    pitch, side = variant.split("-")
    deg = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    b6 = p.LoadBoard(str(Q270W / f"wing-rev6-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    def to_case(poly):
        q = shp_translate(poly, xoff=-jw[0], yoff=-jw[1])
        q = shp_rotate(q, deg, origin=(0, 0))
        return shp_translate(q, xoff=env[0], yoff=env[1])
    data["variants"][variant] = {
        "rev5": [list(c) for c in to_case(outline(b5)).exterior.coords],
        "rev6": [list(c) for c in to_case(outline(b6)).exterior.coords],
        "chain": ND[variant]["elements_case"]}
_json.dump(data, open("/home/hatch/workspace/projects/he-piantor-wingnotch/.issue273-runtime/dbg2.json", "w"))
print("dumped")
