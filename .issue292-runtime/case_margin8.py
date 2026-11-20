import json, pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
from shapely.ops import nearest_points
def outline_pts(path):
    b = p.LoadBoard(path)
    po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
    ch = po.Outline(0)
    return [(ch.CPoint(j).x / 1e6, ch.CPoint(j).y / 1e6) for j in range(ch.PointCount())], b
wpts, wb = outline_pts('hardware/kicad/qualification/issue-270-wing-rev6/wing-rev6-17mm-left/main.kicad_pcb')
jw = [f for f in wb.GetFootprints() if f.GetReference() == 'J_WING'][0].GetPosition()
jw = (jw.x / 1e6, jw.y / 1e6)
print('J_WING at', jw)
wing = Polygon(wpts)
wing = shp_translate(wing, xoff=-jw[0], yoff=-jw[1])
wing = shp_rotate(wing, 30.5, origin=(0, 0))
wing = shp_translate(wing, xoff=-27.0, yoff=-37.5)
mpts, _ = outline_pts('hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb')
main = shp_translate(Polygon(mpts), xoff=-100.0, yoff=-70.0)
print('VALIDATION seam:', round(main.distance(wing), 4), 'overlap:', round(main.intersection(wing).area, 5))
A = (-32.949, 45.438); B = (-28.936, 52.387); C = (-35.893, 64.436)
for name, seg in (('A-B', LineString([A, B])), ('B-C', LineString([B, C]))):
    p1, p2 = nearest_points(seg, wing)
    print(f'{name} -> wing min {round(seg.distance(wing),3)} at ({round(p1.x,2)},{round(p1.y,2)}) -> ({round(p2.x,2)},{round(p2.y,2)})')
    print('   profile:', [round(seg.interpolate(f, normalized=True).distance(wing), 3) for f in (0, .2, .4, .6, .8, 1)])
# closest wing boundary points to the dent
nb = [(round(x,2), round(y,2)) for x, y in wing.exterior.coords if -45 <= x <= -15 and 35 <= y <= 75]
print('wing boundary near dent (case frame):', nb)
json.dump({'wing275_case': list(wing.exterior.coords)}, open('.issue292-runtime/wing275-case.json', 'w'))
