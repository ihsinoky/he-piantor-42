import json
from shapely.geometry import Polygon, LineString
from shapely.ops import nearest_points
m = json.load(open('/home/hatch/workspace/projects/he-piantor-southnotch/.issue-case-runtime/measured.json'))
wing = Polygon(m['wing_left'])
A = (-32.949, 45.438); B = (-28.936, 52.387); C = (-35.893, 64.436)
dent = LineString([A, B, C])
print('wing bounds:', [round(v, 2) for v in wing.bounds])
print('min distance dent->wing_left:', round(dent.distance(wing), 3))
for Y in (46, 50, 52.387, 56, 60, 64):
    inter = LineString([(-200, Y), (0, Y)]).intersection(wing)
    xe = None if inter.is_empty else inter.bounds[2]
    xd = A[0] + (Y-A[1])/(B[1]-A[1])*(B[0]-A[0]) if Y <= 52.387 else B[0] + (Y-B[1])/(C[1]-B[1])*(C[0]-B[0])
    print(f"Y={Y}: wing east X={None if xe is None else round(xe,3)} dent X={round(xd,3)} gap={None if xe is None else round(xd-xe,3)}")
p1, p2 = nearest_points(dent, wing)
print('nearest dent->wing:', (round(p1.x,3), round(p1.y,3)), '->', (round(p2.x,3), round(p2.y,3)))
