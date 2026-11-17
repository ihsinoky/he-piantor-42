"""Direct overlap check: new Main vs CURRENT Wing outlines (all
variants), Rev.8 as control. If the trapezoid overlapped the Wing,
the buffer cut would silently absorb it - must be ruled out."""
import json
from pathlib import Path
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
exec(open(HERE / 's2a_design.py').read().split('results = {}')[0])

mp, run = make_main(16.689)
for v in ('17mm-left', '17mm-right', '16mm-left', '16mm-right'):
    w = Polygon(w2a[v]['outline'])
    print(v, 'overlap main_new vs wing_old:', round(mp.intersection(w).area, 4),
          ' dist:', round(mp.distance(w), 4))
wl = Polygon(w2a['17mm-left']['outline'])
print('rev8 control: overlap', round(rev8.intersection(wl).area, 4),
      ' dist', round(rev8.distance(wl), 4))
# where is the closest approach of main_new to wing_old (17L)?
from shapely.ops import nearest_points
a, b = nearest_points(mp, wl)
print('nearest pair 17L:', [round(v, 2) for v in (a.x, a.y)], '->', [round(v, 2) for v in (b.x, b.y)])
