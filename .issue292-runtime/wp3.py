src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track, add_via = g['astar'], g['add_track'], g['add_via']

def leg(net, layer, start, goal, w, seed_r=0.35, goal_r=0.3):
    gs = Point(*goal).buffer(goal_r) if isinstance(goal, tuple) else goal
    path = astar(net, layer, Point(*start).buffer(seed_r), gs, w)
    print(net, layer, '->', goal if isinstance(goal, tuple) else 'shape', 'OK' if path else None)
    if not path: return None
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
    return path[-1]

# VBUS: F east, via at (84,131), B north to target
its = g['items']['VBUS']
tgt = [it for it in its if it['kind'] == 'trk' and 'B' in it['layers']][0]
end = leg('VBUS', 'F', (78.6, 125.9), (84.0, 131.0), 0.3, seed_r=0.2)
print('via_legal (84,131):', g['via_legal']('VBUS', 84.0, 131.0))
if end and g['via_legal']('VBUS', 84.0, 131.0):
    add_via('VBUS', 84.0, 131.0)
    leg('VBUS', 'B', (84.0, 131.0), None, 0.3) if False else None
    path = astar('VBUS', 'B', Point(84.0, 131.0).buffer(0.35), tgt['shape'].buffer(0.05), 0.3)
    print('VBUS B north:', 'OK' if path else None)
    if path:
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('VBUS', *path[i], *path[i+1], 0.3, 'B')
print('VBUS comps:', len(g['components']('VBUS')))
b.Save(str(g['BPATH']))

# PAD_EN: F route south-east to far F track (89.1,132.6)
its = g['items']['PAD_EN']
tgt = [it for it in its if it['kind'] == 'trk' and it['shape'].length > 20][0]
cur = leg('PAD_EN', 'F', (77.38, 121.8), (84.0, 127.0), 0.1, seed_r=0.2)
if cur:
    path = astar('PAD_EN', 'F', Point(*cur).buffer(0.05), tgt['shape'].buffer(0.05), 0.1)
    print('PAD_EN F final:', 'OK' if path else None)
    if path:
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('PAD_EN', *path[i], *path[i+1], 0.1, 'F')
print('PAD_EN comps:', len(g['components']('PAD_EN')))
b.Save(str(g['BPATH']))
