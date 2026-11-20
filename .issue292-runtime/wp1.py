src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track, add_via = g['astar'], g['add_track'], g['add_via']

def legs(net, layer, start, wps, w, final_shape=None):
    cur = Point(*start).buffer(0.35)
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

# ADC_C via B south lane
its = g['items']['ADC_C']
far_via = [it for it in its if it['kind'] == 'via' and abs(it['pts'][0][0] - 92.4) < 0.2][0]
ok = legs('ADC_C', 'B', (74.45, 119.35), [(74.45, 126.5), (92.4, 126.5)], 0.1, far_via['shape'].buffer(0.05))
print('ADC_C done:', ok, 'comps:', len(g['components']('ADC_C')))
b.Save(str(g['BPATH']))
