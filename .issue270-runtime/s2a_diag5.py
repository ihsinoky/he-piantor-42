"""Print vertices of each removed part (17mm-left) and check
main_new vs w_old overlap directly."""
import json
from pathlib import Path
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
exec(open(HERE / 's2a_design.py').read().split('results = {}')[0])

mp, run = make_main(16.689)
w_old = Polygon(w2a['17mm-left']['outline'])
print('main_new vs w_old overlap area:', round(mp.intersection(w_old).area, 4))
print('main_new vs w_old distance:', round(mp.distance(w_old), 4))
buf = mp.buffer(GAP, resolution=64)
w_new = w_old.difference(buf)
removed = w_old.difference(w_new)
parts = list(removed.geoms) if removed.geom_type == 'MultiPolygon' else [removed]
for i, pt in enumerate(sorted(parts, key=lambda q: -q.area)):
    print(f'part{i} area {pt.area:.3f} vertices:')
    for c in pt.exterior.coords:
        print(f'    ({c[0]:.2f},{c[1]:.2f})')
