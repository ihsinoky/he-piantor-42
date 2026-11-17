"""Distance profile: Wing 17L boundary points vs Main Rev.8 outline,
to find every span where the fitted gap is < 1.0mm (not just notch)."""
import json
from pathlib import Path
from shapely.geometry import Polygon, Point

HERE = Path(__file__).resolve().parent
g = json.loads((HERE / 'geometry.json').read_text())
w2a = json.loads((HERE / 'wing2a.json').read_text())
main = Polygon(g['main_rev8_outline'])

for variant in ('17mm-left', '17mm-right'):
    w = Polygon(w2a[variant]['outline'])
    ext = w.exterior
    n = int(ext.length / 0.25)
    runs = []
    cur = None
    for i in range(n + 1):
        p = ext.interpolate(i / n, normalized=True)
        d = main.distance(p)
        if d < 1.0:
            if cur is None:
                cur = [p.x, p.y, p.x, p.y, d, 0.0]
            cur[2], cur[3] = p.x, p.y
            cur[4] = min(cur[4], d)
            cur[5] += ext.length / n
        else:
            if cur:
                runs.append(cur)
            cur = None
    if cur:
        runs.append(cur)
    print(variant, 'boundary spans with gap<1.0mm:')
    for r in runs:
        print(f'   from ({r[0]:.1f},{r[1]:.1f}) to ({r[2]:.1f},{r[3]:.1f}) len {r[5]:.1f}mm min {r[4]:.4f}')
