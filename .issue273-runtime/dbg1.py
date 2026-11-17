import sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
from notchain import wing_xf_factory
Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
Q270W = W / "hardware/kicad/qualification/issue-270-wing-rev6"

def outline(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM)
                    for j in range(ch.PointCount())])

for variant in ("17mm-right", "17mm-left"):
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
    o5, o6 = to_case(outline(b5)), to_case(outline(b6))
    rem = o5.difference(o6)
    print(variant, "jw", [round(v, 3) for v in jw])
    print("  o5 bounds", [round(v, 1) for v in o5.bounds], "area", round(o5.area, 1))
    print("  o6 bounds", [round(v, 1) for v in o6.bounds], "area", round(o6.area, 1))
    print("  removed bounds", [round(v, 1) for v in rem.bounds], "area", round(rem.area, 3))
