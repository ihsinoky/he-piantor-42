src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track, add_via = g['astar'], g['add_track'], g['add_via']

def legs(net, layer, start, wps, w, final_shape=None, seed_r=0.35):
    cur = Point(*start).buffer(seed_r)
    for wp in wps:
        path = astar(net, layer, cur, Point(*wp).buffer(0.3), w)
        print(net, layer, '->', wp, 'OK' if path else None)
        if not path: return False
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
        cur = Point(*path[-1]).buffer(0.05)
    if final_shape is not None:
        path = astar(net, layer, cur, final_shape, w)
        print(net, layer, '-> final', 'OK' if path else None)
        if not path: return False
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, layer)
    return True

# VBUS: escape via (80.6,125.9) on B -> target B track near (86.25,111.5)
its = g['items']['VBUS']
tgt = [it for it in its if it['kind'] == 'trk' and 'B' in it['layers']][0]
ok = legs('VBUS', 'B', (80.6, 125.9), [(85.0, 134.0), (86.5, 120.0)], 0.3, tgt['shape'].buffer(0.05))
print('VBUS done:', ok, 'comps:', len(g['components']('VBUS')))
b.Save(str(g['BPATH']))
