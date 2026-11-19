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

# GND pad 18: scan via candidates SE of pad 18
found = None
for vx in (77.5, 77.0, 78.0, 76.8, 78.5):
    for vy in (125.0, 125.5, 124.9, 125.9):
        if g['via_legal']('GND', vx, vy):
            found = (vx, vy); break
    if found: break
print('GND18 via candidate:', found)
if found:
    add_track('GND', 75.75, 124.65, *found, 0.2, 'F')
    add_via('GND', *found)
    b.Save(str(g['BPATH']))

# RESET_N: B leg then via + I2
its = g['items']['RESET_N']
tgt = [it for it in its if it['kind'] == 'trk' and 'I2' in it['layers']][0]
end = leg('RESET_N', 'B', (79.8, 119.05), (84.0, 112.0), 0.1, seed_r=0.2)
print('via_legal RESET (84,112):', g['via_legal']('RESET_N', 84.0, 112.0))
if end and g['via_legal']('RESET_N', 84.0, 112.0):
    add_via('RESET_N', 84.0, 112.0)
    leg('RESET_N', 'I2', (84.0, 112.0), tgt['shape'].buffer(0.05), 0.1)
print('RESET_N comps:', len(g['components']('RESET_N')))
b.Save(str(g['BPATH']))
