src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track = g['astar'], g['add_track']

def leg(net, layer, start, goal, w, seed_r=0.35):
    gs = Point(*goal).buffer(0.3) if isinstance(goal, tuple) else goal
    path = astar(net, layer, Point(*start).buffer(seed_r), gs, w)
    print(net, layer, '->', goal if isinstance(goal, tuple) else 'shape', 'OK' if path else None)
    if not path: return None
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
    return path[-1]

cur = (77.0, 118.2)
for wp in [(82.0, 121.0), (81.0, 125.0)]:
    end = leg('SYS_3V3', 'B', cur, wp, 0.3, seed_r=0.15)
    if not end: break
    cur = end
else:
    leg('SYS_3V3', 'B', cur, (79.4, 124.2), 0.3, seed_r=0.1)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
