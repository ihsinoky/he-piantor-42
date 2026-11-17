"""Stage 2a diagnostics: where is the Wing removed region, where is
the Rev.8-minus-new sliver, and how much of the new notch floor sits
at exactly the 0.55 offset (uniform run) vs blend zones."""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, Point
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
exec(open(HERE / 's2a_design.py').read().split('results = {}')[0])

mp, run = make_main(16.689)
buf = mp.buffer(GAP, resolution=64)
sliver = rev8.difference(mp)
print('rev8-new sliver area', round(sliver.area, 4), 'bbox', [round(v, 2) for v in sliver.bounds])

for variant in ('17mm-left', '17mm-right'):
    w_old = Polygon(w2a[variant]['outline'])
    w_new = w_old.difference(buf)
    if w_new.geom_type == 'MultiPolygon':
        w_new = max(w_new.geoms, key=lambda q: q.area)
    removed = w_old.difference(w_new)
    parts = list(removed.geoms) if removed.geom_type == 'MultiPolygon' else [removed]
    print(f'--- {variant}: removed parts {len(parts)}')
    for pt in sorted(parts, key=lambda q: -q.area):
        print(f'   area {pt.area:8.3f}  bbox {[round(v, 1) for v in pt.bounds]}')
    # floor analysis: new boundary inside the 1.2 band, split by distance
    floor = w_new.exterior.intersection(mp.buffer(1.2, resolution=64))
    tot, uni = 0.0, 0.0
    geoms = [floor] if floor.geom_type == 'LineString' else list(getattr(floor, 'geoms', []))
    for ln in geoms:
        if ln.geom_type not in ('LineString', 'LinearRing'):
            continue
        tot += ln.length
        n = max(2, int(ln.length / 0.1))
        prev = None
        for i in range(n + 1):
            p = ln.interpolate(i / n, normalized=True)
            d = mp.distance(p)
            if prev is not None and abs(d - GAP) <= 0.01:
                uni += ln.length / n
            prev = d
    print(f'   floor-in-band length {tot:.2f}mm, at 0.55+-0.01: {uni:.2f}mm')
    # distance from new main tab front/walls: check mouth blend extents
    print(f'   seam {mp.distance(w_new):.4f}')
