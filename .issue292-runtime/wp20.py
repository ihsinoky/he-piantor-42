src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point, LineString
b = g['b']; astar, add_track = g['astar'], g['add_track']

def leg(net, layer, start, goal_shape, w, seed_r=0.35):
    path = astar(net, layer, Point(*start).buffer(seed_r), goal_shape, w)
    print(net, layer, 'leg:', 'OK' if path else None)
    if not path: return None
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
    return path[-1]

# comp1 -> comp2 on B: target = comp2 B run (79.3,120.0)-(79.3,122.7)
tgt2 = LineString([(79.3, 120.0), (79.3, 122.7)]).buffer(0.15)
leg('SYS_3V3', 'B', (70.4, 120.9), tgt2, 0.3, seed_r=0.15)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
# comp1 -> comp0 on I2: target = comp0 I2 track (85.0,104.3)-(85.8,103.5)
tgt0 = LineString([(85.0, 104.3), (85.8, 103.5)]).buffer(0.15)
leg('SYS_3V3', 'I2', (74.0, 116.75), tgt0, 0.3)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
