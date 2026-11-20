src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track, add_via = g['astar'], g['add_track'], g['add_via']

def leg(net, layer, start, goal, w, seed_r=0.35):
    gs = Point(*goal).buffer(0.3) if isinstance(goal, tuple) else goal
    path = astar(net, layer, Point(*start).buffer(seed_r), gs, w)
    print(net, layer, '->', goal if isinstance(goal, tuple) else 'shape', 'OK' if path else None)
    if not path: return None
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
    return path[-1]

# GND {14,16} -> pad 7 tap via (70.85,124.45) on F
leg('GND', 'F', (74.45, 124.65), (70.85, 124.45), 0.2, seed_r=0.15)
b.Save(str(g['BPATH']))

# VBAT_SENSE: B leg to (86.5,121), via, I2 to far track
its = g['items']['VBAT_SENSE']
tgt = [it for it in its if it['kind'] == 'trk' and 'I2' in it['layers']][0]
end = leg('VBAT_SENSE', 'B', (80.6, 125.45), (86.5, 121.0), 0.1, seed_r=0.2)
print('via_legal VBAT (86.5,121):', g['via_legal']('VBAT_SENSE', 86.5, 121.0))
if end and g['via_legal']('VBAT_SENSE', 86.5, 121.0):
    add_via('VBAT_SENSE', 86.5, 121.0)
    leg('VBAT_SENSE', 'I2', (86.5, 121.0), tgt['shape'].buffer(0.05), 0.1)
print('VBAT_SENSE comps:', len(g['components']('VBAT_SENSE')))
b.Save(str(g['BPATH']))
