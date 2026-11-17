import pcbnew as p
from shapely.geometry import Polygon
MM = 1e6
b = p.LoadBoard("hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
ps = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(ps)
print("outlines:", ps.OutlineCount())
ch = ps.Outline(0)
pts = [(ch.CPoint(j).x / MM - 100.0, ch.CPoint(j).y / MM - 70.0) for j in range(ch.PointCount())]
poly = Polygon(pts)
print("case-frame area:", round(poly.area, 3), "(design 2637.71)")
