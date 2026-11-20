src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track = g['astar'], g['add_track']
its = g['items']['RESET_N']
comps = g['components']('RESET_N')
small = min(comps, key=len)
start = Point(112.9, 104.0).buffer(0.2)
for i in small:
    it = its[i]
    if it['kind'] == 'pad': continue
    for L in sorted(it['layers'] & {'F', 'I2', 'B'}):
        path = astar('RESET_N', L, start, it['shape'].buffer(0.05), 0.1)
        print(L, '->', it['kind'], [(round(x, 1), round(y, 1)) for x, y in it['pts']][:2], 'OK' if path else None)
        if path:
            path = g['extend'](g['simplify'](path))
            for j in range(len(path) - 1): add_track('RESET_N', *path[j], *path[j+1], 0.1, L)
            b.Save(str(g['BPATH']))
            print('RESET_N comps:', len(g['components']('RESET_N')))
            raise SystemExit
print('no leg worked')
