import csv, pcbnew as p
from shapely.geometry import Polygon
def board_outline_pts(path):
    b = p.LoadBoard(path)
    po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
    ch = po.Outline(0); ps = p.SHAPE_POLY_SET(); ch.TransformToPolygon(ps, 100, False)
    c2 = ps.Outline(0)
    return [(c2.CPoint(i).x / 1e6, c2.CPoint(i).y / 1e6) for i in range(c2.PointCount())]
rows = list(csv.DictReader(open('hardware/case/issue-228-final/inputs/rev3-final/outline-17mm-left.csv')))
ref = Polygon([(float(r['x_mm']), float(r['y_mm'])) for r in rows])
pts = board_outline_pts('hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb')
import itertools
def bbox(P):
    xs = [q[0] for q in P]; ys = [q[1] for q in P]
    return min(xs), min(ys), max(xs), max(ys)
rb = bbox(ref.exterior.coords)
for sx, sy in itertools.product((1,-1),(1,-1)):
    tp = [(sx*x, sy*y) for x, y in pts]
    tb = bbox(tp)
    dx, dy = rb[0]-tb[0], rb[1]-tb[1]
    cand = Polygon([(x+dx, y+dy) for x, y in tp])
    if not cand.is_valid: cand = cand.buffer(0)
    print(f'sx={sx} sy={sy}: hausdorff={cand.hausdorff_distance(ref):.3f} symdiff={cand.symmetric_difference(ref).area:.1f}')
