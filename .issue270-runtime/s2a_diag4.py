"""Pin down removed part 2: centroid, distance to main_new, nearest
points; also bounds of rev7/rev8/main_new for reference."""
import json
from pathlib import Path
from shapely.geometry import Polygon
from shapely.ops import nearest_points

HERE = Path(__file__).resolve().parent
exec(open(HERE / 's2a_design.py').read().split('results = {}')[0])

mp, run = make_main(16.689)
print('rev7 bounds', [round(v, 1) for v in rev7.bounds])
print('rev8 bounds', [round(v, 1) for v in rev8.bounds])
print('main_new bounds', [round(v, 1) for v in mp.bounds])
buf = mp.buffer(GAP, resolution=64)
w_old = Polygon(w2a['17mm-left']['outline'])
w_new = w_old.difference(buf)
removed = w_old.difference(w_new)
parts = list(removed.geoms) if removed.geom_type == 'MultiPolygon' else [removed]
for i, pt in enumerate(sorted(parts, key=lambda q: -q.area)):
    c = pt.centroid
    a, b = nearest_points(pt, mp)
    print(f'part{i} area {pt.area:.3f} centroid ({c.x:.1f},{c.y:.1f}) '
          f'dist_to_main {mp.distance(pt):.3f} nearest ({a.x:.1f},{a.y:.1f})->({b.x:.1f},{b.y:.1f}) '
          f'vertices {len(list(pt.exterior.coords))}')
