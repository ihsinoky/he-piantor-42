import json, pcbnew as p
from shapely.geometry import Polygon, LineString
from shapely.ops import nearest_points
def board_outline_pts(path):
    b = p.LoadBoard(path)
    po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
    ch = po.Outline(0); ps = p.SHAPE_POLY_SET(); ch.TransformToPolygon(ps, 100, False)
    c2 = ps.Outline(0)
    return [(c2.CPoint(i).x / 1e6, c2.CPoint(i).y / 1e6) for i in range(c2.PointCount())]
d = json.load(open('hardware/case/issue-198-final/17mm/dimensions.json'))
t = d['wing_transforms']['left']; M = t['matrix']; T = t['translation']
wpts = board_outline_pts('hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb')
loc = [(x - 100, -y + 100) for x, y in wpts]
wing6 = Polygon([(M[0][0]*x + M[0][1]*y + T[0], M[1][0]*x + M[1][1]*y + T[1]) for x, y in loc])
r10 = json.load(open('/home/hatch/workspace/projects/he-piantor-southnotch/.issue-case-runtime/rev10-assembly.json'))
main = Polygon(r10['rev10_assembly'])
print('wing6 bounds:', [round(v, 2) for v in wing6.bounds])
print('overlap main/wing6:', round(main.intersection(wing6).area, 4))
print('distance main/wing6:', round(main.distance(wing6), 4))
A = (-32.949, 45.438); B = (-28.936, 52.387); C = (-35.893, 64.436)
for name, seg in (('A-B', LineString([A, B])), ('B-C', LineString([B, C]))):
    p1, p2 = nearest_points(seg, wing6)
    print(f'{name} -> wing6 min {round(seg.distance(wing6),3)} at ({round(p1.x,2)},{round(p1.y,2)}) -> ({round(p2.x,2)},{round(p2.y,2)})')
    print('   profile:', [round(seg.interpolate(f, normalized=True).distance(wing6), 3) for f in (0, .25, .5, .75, 1)])
# wing6 east boundary points in dent band
pts = [(round(x,2), round(y,2)) for x, y in wing6.exterior.coords if -45 <= x <= -20 and 40 <= y <= 70]
print('wing6 boundary in band:', pts)
json.dump({'wing6_assembly': list(wing6.exterior.coords)}, open('.issue292-runtime/wing6-assembly.json', 'w'))
