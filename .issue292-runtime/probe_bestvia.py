import sys, os
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.strtree import STRtree
from shapely.geometry import Point
NET = os.environ.get('P_NET', 'MUX_A0')
X0, X1, Y0, Y1 = [float(v) for v in os.environ.get('P_BOX', '71.0,77.0,120.8,128.0').split(',')]
trees = {L: STRtree([s2 for n2, s2 in all_obs(L) if n2 != NET]) for L in ('F', 'I2', 'B')}
shapes = {L: [s2 for n2, s2 in all_obs(L) if n2 != NET] for L in ('F', 'I2', 'B')}
res = []
j = Y0
while j <= Y1:
    i = X0
    while i <= X1:
        pt = Point(i, j)
        if OUTLINE.exterior.distance(pt) >= 0.80:
            worst = 9.9
            for L in ('F', 'I2', 'B'):
                idx = trees[L].query(pt.buffer(1.2))
                for k in idx:
                    d = pt.distance(shapes[L][k]) - 0.30
                    if d < worst: worst = d
            res.append((round(worst, 3), round(i, 2), round(j, 2)))
        i += 0.05
    j += 0.05
res.sort(reverse=True)
print('best via centres (clearance, x, y):', res[:8])
