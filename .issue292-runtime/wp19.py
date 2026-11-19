src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track = g['astar'], g['add_track']
its = g['items']['SYS_3V3']
tgt = [it for it in its if it['kind'] == 'trk' and 'B' in it['layers']][0]
# current position: end of the B west leg drawn in wp18 (70.5,121)
path = astar('SYS_3V3', 'B', Point(70.5, 121.0).buffer(0.15), tgt['shape'].buffer(0.05), 0.3)
print('SYS B east along y121:', 'OK' if path else None)
if path:
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track('SYS_3V3', *path[i], *path[i+1], 0.3, 'B')
    b.Save(str(g['BPATH']))
    print('SYS comps:', len(g['components']('SYS_3V3')))
