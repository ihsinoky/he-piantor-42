import json, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
from notchain import wing_xf_factory
Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])
res = {}
for variant, side in (("17mm-left", "left"), ("17mm-right", "right")):
    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    ang = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    q = shp_translate(outline_kicad(b5), xoff=-jw[0], yoff=-jw[1])
    q = shp_rotate(q, ang, origin=(0, 0))
    q = shp_translate(q, xoff=env[0], yoff=env[1])
    res[variant] = [list(c) for c in q.exterior.coords]
Path(".issue273-runtime/rev5-outlines.json").write_text(json.dumps(res))
print("dumped")
