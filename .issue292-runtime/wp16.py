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

# scan via near CVCC1
via_pt = None
for vx in [74.0 + 0.25 * i for i in range(17)]:
    for vy in [116.5 + 0.25 * j for j in range(7)]:
        if g['via_legal']('SYS_3V3', vx, vy):
            via_pt = (vx, vy); break
    if via_pt: break
print('SYS via candidate:', via_pt)
if via_pt:
    end = leg('SYS_3V3', 'F', (75.675, 118.3), via_pt, 0.3, seed_r=0.25)
    if end:
        add_via('SYS_3V3', *via_pt)
        leg('SYS_3V3', 'B', via_pt, (79.65, 119.35), 0.3)
        print('SYS comps:', len(g['components']('SYS_3V3')))
        b.Save(str(g['BPATH']))
