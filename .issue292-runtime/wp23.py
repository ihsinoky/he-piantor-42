src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point, LineString
b = g['b']; astar, add_track = g['astar'], g['add_track']
tgt2 = LineString([(79.3, 120.0), (79.3, 122.7)]).buffer(0.15)
path = astar('SYS_3V3', 'B', Point(70.4, 120.9).buffer(0.15), tgt2, 0.2)
print('SYS B leg w0.2:', 'OK' if path else None)
if path:
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track('SYS_3V3', *path[i], *path[i+1], 0.2, 'B')
    b.Save(str(g['BPATH']))
    print('SYS comps:', len(g['components']('SYS_3V3')))
