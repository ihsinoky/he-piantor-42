import json, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
sys.path.insert(0, ".issue270-runtime")
from notchain import wing_xf_factory
MM = 1e6
WT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline")
ND = json.loads((WT / ".issue270-runtime/notch2d.json").read_text())["17mm-left"]
def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])
b = p.LoadBoard(str(WT / "hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb"))
b5 = p.LoadBoard(str(WT / "hardware/kicad/qualification/issue-263-implementation/wing-rev5-17mm-left/main.kicad_pcb"))
fwd, inv, jw = wing_xf_factory(b5, "left")
def to_case(pb):
    q = shp_translate(pb, xoff=-jw[0], yoff=-jw[1]); q = shp_rotate(q, 30.5, origin=(0, 0))
    return shp_translate(q, xoff=-27.0, yoff=-37.5)
new_case = to_case(outline_kicad(b))
design = Polygon(ND["wing_new_case"])
sd = new_case.symmetric_difference(design)
parts = list(sd.geoms) if sd.geom_type == "MultiPolygon" else [sd]
for q in parts:
    print("comp area %.5f centroid %s bounds %s" % (q.area, tuple(round(v,2) for v in q.centroid.coords[0]), tuple(round(v,2) for v in q.bounds)))
