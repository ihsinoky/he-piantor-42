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
b5 = p.LoadBoard(str(Q263 / "wing-rev5-17mm-left/main.kicad_pcb"))
fwd, inv, jw = wing_xf_factory(b5, "left")
q = shp_translate(outline_kicad(b5), xoff=-jw[0], yoff=-jw[1])
q = shp_rotate(q, 30.5, origin=(0, 0))
q = shp_translate(q, xoff=-27.0, yoff=-37.5)
dumped = Polygon(json.loads(Path(".issue273-runtime/rev5-outlines.json").read_text())["17mm-left"])
nd = json.loads(Path(".issue273-runtime/notch2e.json").read_text())
new = Polygon(nd["17mm-left"]["wing_new_case"])
print("fresh old area", q.area, "dumped old area", dumped.area, "symdiff", q.symmetric_difference(dumped).area)
print("removed fresh", q.difference(new).area, "added fresh", new.difference(q).area)
print("jw", jw)
