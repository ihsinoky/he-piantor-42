import json, pcbnew as p
from shapely.geometry import Polygon, LineString
from shapely.ops import nearest_points

def board_outline_pts(path):
    b = p.LoadBoard(path)
    po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
    ch = po.Outline(0)
    ps = p.SHAPE_POLY_SET(); ch.TransformToPolygon(ps, 100, False)
    c2 = ps.Outline(0)
    return [(c2.CPoint(i).x / 1e6, c2.CPoint(i).y / 1e6) for i in range(c2.PointCount())]

# Wing Rev.6 17L outline -> assembly frame via #198 transform
d = json.load(open('hardware/case/issue-198-final/17mm/dimensions.json'))
t = d['wing_transforms']['left']; M = t['matrix']; T = t['translation']
wpts = board_outline_pts('hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb')
wing6 = Polygon([(M[0][0]*(x-100) + M[0][1]*(y-54) + T[0], M[1][0]*(x-100) + M[1][1]*(y-54) + T[1]) for x, y in wpts])
wing3 = Polygon(d['boards']['wing_left'])
print('wing6 valid:', wing6.is_valid, 'bounds:', [round(v,2) for v in wing6.bounds])
print('wing3 bounds:', [round(v,2) for v in wing3.bounds])

r10 = json.load(open('/home/hatch/workspace/projects/he-piantor-southnotch/.issue-case-runtime/rev10-assembly.json'))
main = Polygon(r10['rev10_assembly'])
print('main(rev10) bounds:', [round(v,2) for v in main.bounds])
print('main vs wing6 distance:', round(main.distance(wing6), 4))
print('main vs wing3 distance:', round(main.distance(wing3), 4))
# dent segments in assembly coords
A = (-32.949, 45.438); B = (-28.936, 52.387); C = (-35.893, 64.436)
for name, seg in (('A-B', LineString([A, B])), ('B-C', LineString([B, C]))):
    for wn, w in (('wing6', wing6), ('wing3', wing3)):
        p1, p2 = nearest_points(seg, w)
        print(f'{name} -> {wn}: min {round(seg.distance(w),3)} at ({round(p1.x,2)},{round(p1.y,2)}) -> ({round(p2.x,2)},{round(p2.y,2)})')
# gap profile along B-C and A-B: sample points, distance to wing6
for name, seg in (('A-B', LineString([A, B])), ('B-C', LineString([B, C]))):
    ds = [round(seg.interpolate(f, normalized=True).distance(wing6), 3) for f in (0, .25, .5, .75, 1)]
    print(name, 'dist profile to wing6:', ds)
# does wing6 overlap main?
print('overlap area main/wing6:', round(main.intersection(wing6).area, 4))
