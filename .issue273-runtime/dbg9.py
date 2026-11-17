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
nd = json.loads(Path(".issue273-runtime/notch2e.json").read_text())
res = {}
for variant, side in (("17mm-left", "left"), ("17mm-right", "right")):
    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    ang = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    q = shp_translate(outline_kicad(b5), xoff=-jw[0], yoff=-jw[1])
    q = shp_rotate(q, ang, origin=(0, 0))
    q = shp_translate(q, xoff=env[0], yoff=env[1])
    new = Polygon(nd[variant]["wing_new_case"])
    def parts(poly):
        found = []
        def walk(g):
            if g.geom_type == "Polygon":
                if g.area > 1e-4:
                    found.append(g)
            elif hasattr(g, "geoms"):
                for s in g.geoms:
                    walk(s)
        walk(poly)
        return [{"area": g.area, "bounds": list(g.bounds),
                 "xy": [list(c) for c in g.exterior.coords]} for g in found]
    res[variant] = {"removed": parts(q.difference(new)), "added": parts(new.difference(q))}
    for kind in ("removed", "added"):
        for g in res[variant][kind]:
            print(variant, kind, round(g["area"], 2), tuple(round(b, 1) for b in g["bounds"]))
Path(".issue273-runtime/delta-parts.json").write_text(json.dumps(res))
