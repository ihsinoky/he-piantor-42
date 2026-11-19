src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point, LineString
b = g['b']; astar, add_track = g['astar'], g['add_track']

def leg(net, layer, start, goal, w, seed_r=0.35):
    gs = Point(*goal).buffer(0.3) if isinstance(goal, tuple) else goal
    path = astar(net, layer, Point(*start).buffer(seed_r), gs, w)
    print(net, layer, '->', goal if isinstance(goal, tuple) else 'shape', 'OK' if path else None)
    if not path: return None
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
    return path[-1]

tgt = LineString([(79.6, 119.6), (79.7, 119.3)]).buffer(0.12)
end = leg('SYS_3V3', 'B', (72.5, 118.6), (77.0, 118.2), 0.3, seed_r=0.15)
if end:
    leg('SYS_3V3', 'B', end, tgt, 0.3, seed_r=0.1)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
