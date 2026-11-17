import json, math, sys
from pathlib import Path
import pcbnew
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-wingnotch/.issue273-runtime")
import notchain

R = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
def densify(poly, step=0.05):
    pts = []
    for ring in [poly.exterior]:
        cs = list(ring.coords)
        for (x0, y0), (x1, y1) in zip(cs, cs[1:]):
            d = math.hypot(x1 - x0, y1 - y0)
            n = max(1, int(d / step))
            for i in range(n):
                pts.append([x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n])
    return pts


def outline(board):
    from shapely.geometry import Polygon
    ps = pcbnew.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / 1e6, ch.CPoint(j).y / 1e6)
                    for j in range(ch.PointCount())])

out = {}
main_b = pcbnew.LoadBoard(str(R / "hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb"))
from shapely.affinity import translate as _tr
mp = _tr(outline(main_b), xoff=-100, yoff=-70)
out["main"] = densify(mp)
for v in ("17mm-left", "17mm-right"):
    side = "left" if "left" in v else "right"
    from shapely.geometry import Polygon as _Poly
    def to_case(board):
        fwd, _, _ = notchain.wing_xf_factory(board, side)
        o = outline(board)
        return _Poly([fwd(pt) for pt in o.exterior.coords])
    b2d = pcbnew.LoadBoard(str(R / f".issue273-runtime/old2d/wing-rev6-{v}.kicad_pcb"))
    out[v + "-2d"] = densify(to_case(b2d))
    bn = pcbnew.LoadBoard(str(R / f"hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-{v}/main.kicad_pcb"))
    out[v + "-2e"] = densify(to_case(bn))
rev5 = json.loads((R / ".issue273-runtime/rev5-outlines.json").read_text())
for v in ("17mm-left", "17mm-right"):
    out[v + "-rev5"] = rev5[v]
(R / ".issue273-runtime/figdata-2e.json").write_text(json.dumps(out))
print("keys:", {k: len(v) for k, v in out.items()})
