"""Notch-zone Edge.Cuts item counts, same rule for the Stage 2b
(exact-offset) and Stage 2d (simplified) Wing Rev.6 boards: items
whose midpoint (segments: mean of ends; arcs: GetMidPoint) in case
frame lies within that board's own removed region (vs Rev.5)
buffered by 1.0 mm."""
import json, subprocess
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
import sys
sys.path.insert(0, ".issue270-runtime")
from notchain import wing_xf_factory

MM = 1e6
WT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline")
RT = WT / ".issue270-runtime"
Q263 = WT / "hardware/kicad/qualification/issue-263-implementation"
Q270W = WT / "hardware/kicad/qualification/issue-270-wing-rev6"

def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])

def load_git(rev, rel, tag):
    dst = RT / f"seg-{tag}.kicad_pcb"
    dst.write_bytes(subprocess.run(["git", "-C", str(WT), "show", f"{rev}:{rel}"],
                                   capture_output=True, check=True).stdout)
    return p.LoadBoard(str(dst))

out = {}
for variant in ("17mm-left", "17mm-right", "16mm-left", "16mm-right"):
    pitch, side = variant.split("-")
    deg = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    def to_case(pb):
        q = shp_translate(pb, xoff=-jw[0], yoff=-jw[1]); q = shp_rotate(q, deg, origin=(0, 0))
        return shp_translate(q, xoff=env[0], yoff=env[1])
    old_case = to_case(outline_kicad(b5))
    res = {}
    for tag, board in (("2b", load_git("c59b295fc", f"hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-{variant}/main.kicad_pcb", variant + "2b")),
                       ("2d", p.LoadBoard(str(Q270W / f"wing-rev6-{variant}/main.kicad_pcb")))):
        new_case = to_case(outline_kicad(board))
        zone = old_case.difference(new_case).buffer(1.0)
        n = 0; kinds = {}
        for d in board.GetDrawings():
            if d.GetLayer() != p.Edge_Cuts:
                continue
            try:
                mid = d.GetMidPoint()
                mp = (mid.x / MM, mid.y / MM)
            except Exception:
                s, e = d.GetStart(), d.GetEnd()
                mp = ((s.x + e.x) / 2 / MM, (s.y + e.y) / 2 / MM)
            if zone.contains(Point(fwd(mp))):
                n += 1
                kinds[str(d.GetShape())] = kinds.get(str(d.GetShape()), 0) + 1
        res[tag] = {"count": n, "kinds": kinds, "removed_mm2": round(old_case.difference(new_case).area, 3)}
    out[variant] = res
    print(variant, res)
(RT / "segments-2d.json").write_text(json.dumps(out, indent=1))
