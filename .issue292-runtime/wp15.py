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

# SYS_3V3 (a) CVCC2 -> CVCC1
leg('SYS_3V3', 'F', (71.8, 119.425), (75.675, 118.3), 0.3, seed_r=0.25)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
# SYS_3V3 (b) CVCC1 -> F track (80.4,107.3)
its = g['items']['SYS_3V3']
tgt = [it for it in its if it['kind'] == 'trk' and 'F' in it['layers'] and it['pts'][0][1] < 110][0]
leg('SYS_3V3', 'F', (75.675, 118.3), tgt['shape'].buffer(0.05), 0.3, seed_r=0.25)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
# SYS_3V3 (c) CVCC1 -> escape via (79.65,119.35)
leg('SYS_3V3', 'F', (75.675, 118.3), (79.65, 119.35), 0.3, seed_r=0.25)
print('SYS comps:', len(g['components']('SYS_3V3')))
b.Save(str(g['BPATH']))
# PAD_EN F south corridor
its = g['items']['PAD_EN']
tgt = [it for it in its if it['kind'] == 'trk' and it['shape'].length > 20][0]
end = leg('PAD_EN', 'F', (77.38, 121.8), (83.0, 125.5), 0.1, seed_r=0.2)
if end:
    leg('PAD_EN', 'F', end, tgt['shape'].buffer(0.05), 0.1, seed_r=0.1)
print('PAD_EN comps:', len(g['components']('PAD_EN')))
b.Save(str(g['BPATH']))
