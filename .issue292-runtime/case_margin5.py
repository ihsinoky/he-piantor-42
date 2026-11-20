import json, pcbnew as p
from shapely.geometry import Polygon
def board_outline_pts(path):
    b = p.LoadBoard(path)
    po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
    ch = po.Outline(0); ps = p.SHAPE_POLY_SET(); ch.TransformToPolygon(ps, 100, False)
    c2 = ps.Outline(0)
    return [(c2.CPoint(i).x / 1e6, c2.CPoint(i).y / 1e6) for i in range(c2.PointCount())]
d = json.load(open('hardware/case/issue-198-final/17mm/dimensions.json'))
t = d['wing_transforms']['left']; M = t['matrix']; T = t['translation']
wpts = board_outline_pts('hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb')
wing6 = Polygon([(M[0][0]*(x-100) + M[0][1]*(y-54) + T[0], M[1][0]*(x-100) + M[1][1]*(y-54) + T[1]) for x, y in wpts])
wing3 = Polygon(d['boards']['wing_left'])
print('hausdorff wing6<->wing3:', round(wing6.hausdorff_distance(wing3), 3))
print('symdiff area:', round(wing6.symmetric_difference(wing3).area, 2), 'wing6 area', round(wing6.area,1), 'wing3 area', round(wing3.area,1))
pts = [(round(x,2), round(y,2)) for x, y in wing6.exterior.coords if -45 <= x <= -15 and 35 <= y <= 75]
print('wing6 boundary near dent band:', pts)
pts3 = [(round(x,2), round(y,2)) for x, y in wing3.exterior.coords if -45 <= x <= -15 and 35 <= y <= 75]
print('wing3 boundary near dent band:', pts3)
