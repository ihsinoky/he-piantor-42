src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track = g['astar'], g['add_track']
its = g['items']['SYS_3V3']
tgt = [it for it in its if it['kind'] == 'via' and abs(it['pts'][0][0] - 79.4) < 0.2][0]
for w in (0.3, 0.2):
    path = astar('SYS_3V3', 'I2', Point(74.0, 116.75).buffer(0.35), tgt['shape'].buffer(0.05), w)
    print('SYS I2 leg w', w, ':', 'OK' if path else None)
    if path:
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('SYS_3V3', *path[i], *path[i+1], w, 'I2')
        b.Save(str(g['BPATH']))
        print('SYS comps:', len(g['components']('SYS_3V3')))
        break
