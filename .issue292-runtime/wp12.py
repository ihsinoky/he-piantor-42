src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track, add_via = g['astar'], g['add_track'], g['add_via']
its = g['items']['RESET_N']
cands = []
for it in its:
    if it['kind'] == 'via' and it['pts'][0][0] > 90: cands.append(('via', it))
    if it['kind'] == 'trk' and 'I2' in it['layers'] and it['pts'][0][0] > 85: cands.append(('trk', it))
start = Point(112.9, 104.0).buffer(0.2)
for kind, it in cands:
    path = astar('RESET_N', 'I2', start, it['shape'].buffer(0.05), 0.1)
    print('I2 ->', kind, [(round(x, 1), round(y, 1)) for x, y in it['pts']][:2], 'OK' if path else None)
    if path:
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('RESET_N', *path[i], *path[i+1], 0.1, 'I2')
        b.Save(str(g['BPATH']))
        print('RESET_N comps:', len(g['components']('RESET_N')))
        break
