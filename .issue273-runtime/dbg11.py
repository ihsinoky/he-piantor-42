import pcbnew as p
from pathlib import Path
from shapely.geometry import Polygon
MM = 1e6
Q = Path("/home/hatch/workspace/projects/he-piantor-wingnotch/hardware/kicad/qualification/issue-270-wing-rev6")
def outline(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])
for side in ("left", "right"):
    a = outline(p.LoadBoard(str(Q / f"wing-rev6-17mm-{side}/main.kicad_pcb")))
    b = outline(p.LoadBoard(str(Q / f"wing-rev6-16mm-{side}/main.kicad_pcb")))
    print(side, "17-vs-16 board-frame outline symdiff:", round(a.symmetric_difference(b).area, 6))
