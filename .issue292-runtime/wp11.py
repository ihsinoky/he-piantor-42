src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track = g['astar'], g['add_track']
its = g['items']['RESET_N']
tgt = [it for it in its if it['kind'] == 'via' and abs(it['pts'][0][0] - 91.0) < 0.2][0]
for L in ('I2', 'B', 'F'):
    cur = Point(112.9, 131.3).buffer(0.35)
    ok = True
    for wp in [(112.9, 104.0)]:
        path = astar('RESET_N', L, cur, Point(*wp).buffer(0.3), 0.1)
        print(L, '->', wp, 'OK' if path else None)
        if not path: ok = False; break
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('RESET_N', *path[i], *path[i+1], 0.1, L)
        cur = Point(*path[-1]).buffer(0.05)
    if ok:
        path = astar('RESET_N', L, cur, tgt['shape'].buffer(0.05), 0.1)
        print(L, '-> target via:', 'OK' if path else None)
        if path:
            path = g['extend'](g['simplify'](path))
            for i in range(len(path) - 1): add_track('RESET_N', *path[i], *path[i+1], 0.1, L)
            b.Save(str(g['BPATH']))
            print('RESET_N comps:', len(g['components']('RESET_N')))
            break
