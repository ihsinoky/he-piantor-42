import json, pcbnew as p
from shapely.geometry import Polygon
from shapely.ops import nearest_points
def board_outline_pts(path):
    b = p.LoadBoard(path)
    po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
    ch = po.Outline(0); ps = p.SHAPE_POLY_SET(); ch.TransformToPolygon(ps, 100, False)
    c2 = ps.Outline(0)
    return [(c2.CPoint(i).x / 1e6, c2.CPoint(i).y / 1e6) for i in range(c2.PointCount())]
d = json.load(open('hardware/case/issue-198-final/17mm/dimensions.json'))
t = d['wing_transforms']['left']; M = t['matrix']; T = t['translation']
r10 = json.load(open('/home/hatch/workspace/projects/he-piantor-southnotch/.issue-case-runtime/rev10-assembly.json'))
main = Polygon(r10['rev10_assembly'])
for name in ('main.kicad_pcb', 'routed.kicad_pcb', 'input.kicad_pcb', 'respin-in.kicad_pcb'):
    wpts = board_outline_pts(f'hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/{name}')
    loc = [(x - 100, -y + 100) for x, y in wpts]
    w = Polygon([(M[0][0]*x + M[0][1]*y + T[0], M[1][0]*x + M[1][1]*y + T[1]) for x, y in loc])
    print(f'{name}: overlap={round(main.intersection(w).area,3)} distance={round(main.distance(w),4)}')
