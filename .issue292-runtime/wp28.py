src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point, LineString
b = g['b']; astar, add_track = g['astar'], g['add_track']

def leg(net, layer, start, goal, w, seed_r=0.35):
    gs = Point(*goal).buffer(0.3) if isinstance(goal, tuple) else goal
    path = astar(net, layer, Point(*start).buffer(seed_r), gs, w)
    print(net, layer, 'w', w, '->', goal if isinstance(goal, tuple) else 'shape', 'OK' if path else None)
    if not path: return None
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
    return path[-1]

tgt_top = LineString([(79.6, 119.6), (79.7, 119.3)]).buffer(0.12)
end = leg('SYS_3V3', 'B', (77.0, 118.2), tgt_top, 0.15, seed_r=0.15)
if not end:
    tgt_run = LineString([(79.3, 120.0), (79.3, 122.7)]).buffer(0.15)
    leg('SYS_3V3', 'B', (70.4, 120.9), tgt_run, 0.15, seed_r=0.15)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
