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

its = g['items']['VBUS']
tgt_via = [it for it in its if it['kind'] == 'via' and abs(it['pts'][0][0] - 87.9) < 0.2][0]
end = leg('VBUS', 'B', (84.0, 131.0), (88.0, 119.5), 0.3)
print('via_legal (88,119.5):', g['via_legal']('VBUS', 88.0, 119.5))
if end and g['via_legal']('VBUS', 88.0, 119.5):
    add_via('VBUS', 88.0, 119.5)
    path = astar('VBUS', 'I2', Point(88.0, 119.5).buffer(0.35), tgt_via['shape'].buffer(0.05), 0.3)
    print('VBUS I2 north:', 'OK' if path else None)
    if path:
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('VBUS', *path[i], *path[i+1], 0.3, 'I2')
print('VBUS comps:', len(g['components']('VBUS')))
b.Save(str(g['BPATH']))
