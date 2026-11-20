src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track, add_via = g['astar'], g['add_track'], g['add_via']
its = g['items']['RESET_N']
tgt = [it for it in its if it['kind'] == 'trk' and 'I2' in it['layers']][0]
print('via_legal (77.5,113.0):', g['via_legal']('RESET_N', 77.5, 113.0))
path = astar('RESET_N', 'F', Point(73.55, 119.35).buffer(0.3), Point(77.5, 113.0).buffer(0.3), 0.1)
print('F leg:', 'OK' if path else None)
if path:
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track('RESET_N', *path[i], *path[i+1], 0.1, 'F')
    if g['via_legal']('RESET_N', 77.5, 113.0):
        add_via('RESET_N', 77.5, 113.0)
        path = astar('RESET_N', 'I2', Point(77.5, 113.0).buffer(0.35), tgt['shape'].buffer(0.05), 0.1)
        print('I2 leg:', 'OK' if path else None)
        if path:
            path = g['extend'](g['simplify'](path))
            for i in range(len(path) - 1): add_track('RESET_N', *path[i], *path[i+1], 0.1, 'I2')
    b.Save(str(g['BPATH']))
    print('RESET_N comps:', len(g['components']('RESET_N')))
