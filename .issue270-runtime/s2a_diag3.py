"""Inspect the anomalous removed strip: components before/after the
buffer difference, and the strip's own vertices."""
import json
from pathlib import Path
from shapely.geometry import Polygon

HERE = Path(__file__).resolve().parent
exec(open(HERE / 's2a_design.py').read().split('results = {}')[0])

mp, run = make_main(16.689)
buf = mp.buffer(GAP, resolution=64)
w_old = Polygon(w2a['17mm-left']['outline'])
print('w_old type', w_old.geom_type, 'area', round(w_old.area, 2), 'valid', w_old.is_valid)
d = w_old.difference(buf)
print('diff type', d.geom_type)
parts = list(d.geoms) if d.geom_type == 'MultiPolygon' else [d]
for i, pt in enumerate(sorted(parts, key=lambda q: -q.area)):
    print(f'  part{i} area {pt.area:.3f} bbox {[round(v,1) for v in pt.bounds]}')
# the strip: part of w_old NOT in the largest diff component
big = max(parts, key=lambda q: q.area)
strip = w_old.difference(big).difference(buf)
print('strip (in w_old, not in big, not in buffer):', strip.geom_type,
      round(strip.area, 4) if not strip.is_empty else 0)
if not strip.is_empty:
    sp = list(strip.geoms) if strip.geom_type == 'MultiPolygon' else [strip]
    for s in sp:
        print('   strip part area', round(s.area, 4), 'bbox', [round(v, 2) for v in s.bounds],
              'dist to main_new', round(mp.distance(s), 3))
# Is the strip inside the buffer after all? (i.e. dropped for another reason)
strip2 = w_old.difference(big)
print('w_old minus big, total:', strip2.geom_type, round(strip2.area, 4))
