import json, math, sys
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
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
fig, axes = plt.subplots(1, 2, figsize=(15, 7))
for ax, variant in zip(axes, ("17mm-left", "17mm-right")):
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
    for poly, style, lab in ((to_case(outline(b5)), "grey", "Rev.5"),
                             (to_case(outline(b6)), "b-", "Rev.6-2d")):
        xs, ys = poly.exterior.xy
        ax.plot(xs, ys, style, lw=1.0, label=lab)
    xs, ys = main_case.exterior.xy
    ax.plot(xs, ys, "k-", lw=1.2, label="Main Rev.9")
    for e in ND[variant]["elements_case"]:
        if e[0] == "line":
            ax.plot([e[1][0], e[2][0]], [e[1][1], e[2][1]], "r--", lw=1.0)
        else:
            _, O, r, a, bb, _m = e
            a0 = math.atan2(a[1] - O[1], a[0] - O[0]); a1 = math.atan2(bb[1] - O[1], bb[0] - O[0])
            while a1 - a0 > math.pi: a1 -= 2 * math.pi
            while a1 - a0 < -math.pi: a1 += 2 * math.pi
            th = [a0 + (a1 - a0) * i / 40 for i in range(41)]
            ax.plot([O[0] + r * math.cos(t) for t in th],
                    [O[1] + r * math.sin(t) for t in th], "r--", lw=1.0)
    ax.set_aspect("equal"); ax.grid(True, lw=0.3)
    ax.set_title(variant)
    if side == "left":
        ax.set_xlim(-45, -5); ax.set_ylim(25, 60)
    else:
        ax.set_xlim(5, 45); ax.set_ylim(25, 60)
    ax.legend(loc="best", fontsize=8)
fig.tight_layout()
fig.savefig(W / ".issue273-runtime/dbg-notch.png", dpi=110)
print("saved dbg-notch.png")
