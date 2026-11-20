import sys, os
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.strtree import STRtree
from shapely.geometry import Point
NET = os.environ.get('P_NET', 'MUX_A0')
X0, X1, Y0, Y1 = [float(v) for v in os.environ.get('P_BOX', '71.0,74.0,120.8,125.4').split(',')]
trees = {}
for L in ('F', 'I2', 'B'):
    trees[L] = STRtree([s2.buffer(float(os.environ.get('P_BUF', '0.05'))) for n2, s2 in all_obs(L) if n2 != NET])
sites = []
j = Y0
while j <= Y1:
    i = X0
    while i <= X1:
        pt = Point(i, j)
        if OUTLINE.exterior.distance(pt) >= 0.85:
            disc = pt.buffer(0.30)
            if all(len(trees[L].query(disc)) == 0 for L in ('F', 'I2', 'B')):
                sites.append((round(i, 2), round(j, 2)))
        i += 0.05
    j += 0.05
print(f'{NET}: {len(sites)} legal via sites in box')
# cluster print: every site, grouped by rows
rows = {}
for x, y in sites: rows.setdefault(y, []).append(x)
for y in sorted(rows): print('  y=%.2f x:' % y, ' '.join('%.2f' % x for x in rows[y]))
