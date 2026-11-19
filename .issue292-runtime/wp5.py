src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track = g['astar'], g['add_track']
its = g['items']['VBUS']
diag = [it for it in its if it['kind'] == 'trk' and 'F' in it['layers'] and it['shape'].length > 12][0]
path = astar('VBUS', 'F', Point(88.0, 119.5).buffer(0.35), diag['shape'].buffer(0.05), 0.3)
print('VBUS F to diagonal:', 'OK' if path else None)
if path:
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track('VBUS', *path[i], *path[i+1], 0.3, 'F')
    b.Save(str(g['BPATH']))
    print('VBUS comps:', len(g['components']('VBUS')))
