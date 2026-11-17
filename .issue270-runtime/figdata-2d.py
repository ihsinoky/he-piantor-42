import json, subprocess
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
import sys
sys.path.insert(0, ".issue270-runtime")
from notchain import wing_xf_factory
MM = 1e6
WT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline")
RT = WT / ".issue270-runtime"
def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return [(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())]
main_b = outline_kicad(p.LoadBoard(str(WT / "hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")))
data = {"main": [[x - 100.0, y - 70.0] for x, y in main_b]}
for variant in ("17mm-left", "17mm-right"):
    pitch, side = variant.split("-")
    deg = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    b5 = p.LoadBoard(str(WT / f"hardware/kicad/qualification/issue-263-implementation/wing-rev5-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    def to_case(pts):
        poly = shp_translate(Polygon(pts), xoff=-jw[0], yoff=-jw[1])
        poly = shp_rotate(poly, deg, origin=(0, 0))
        poly = shp_translate(poly, xoff=env[0], yoff=env[1])
        return [list(c) for c in poly.exterior.coords]
    data[variant + "-2d"] = to_case(outline_kicad(p.LoadBoard(str(WT / f"hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-{variant}/main.kicad_pcb"))))
    dst = RT / f"fig-{variant}-2b.kicad_pcb"
    dst.write_bytes(subprocess.run(["git", "-C", str(WT), "show", f"c59b295fc:hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-{variant}/main.kicad_pcb"], capture_output=True, check=True).stdout)
    data[variant + "-2b"] = to_case(outline_kicad(p.LoadBoard(str(dst))))
    data[variant + "-rev5"] = to_case(outline_kicad(b5))
(RT / "figdata-2d.json").write_text(json.dumps(data))
print("ok", {k: len(v) for k, v in data.items()})
