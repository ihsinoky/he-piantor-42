src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track = g['astar'], g['add_track']
its = g['items']['SYS_3V3']
stub = [it for it in its if it['kind'] == 'trk' and 'F' in it['layers'] and abs(it['pts'][0][0] - 79.0) < 0.3 and it['pts'][0][1] > 123][0]
cvcc1 = [it for it in its if it['kind'] == 'pad' and abs(it['pts'][0][0] - 75.675) < 0.1][0]
for w in (0.1, 0.05):
    path = astar('SYS_3V3', 'F', stub['shape'].buffer(0.02), cvcc1['shape'].buffer(0.02), w)
    print('SYS F direct w', w, ':', 'OK' if path else None)
    if path:
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('SYS_3V3', *path[i], *path[i+1], w, 'F')
        b.Save(str(g['BPATH']))
        print('SYS comps:', len(g['components']('SYS_3V3')))
        break
