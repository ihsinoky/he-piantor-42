src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point
b = g['b']; astar, add_track, add_via = g['astar'], g['add_track'], g['add_via']
its = g['items']['RESET_N']
tgt = [it for it in its if it['kind'] == 'trk' and 'I2' in it['layers']][0]
done = False
for vx in [75.5 + 0.25 * i for i in range(19)]:
    for vy in [111.0 + 0.25 * j for j in range(17)]:
        if not g['via_legal']('RESET_N', vx, vy): continue
        # F stub from the new F track end (77.5,113.0) to via point
        p1 = astar('RESET_N', 'F', Point(77.5, 113.0).buffer(0.1), Point(vx, vy).buffer(0.28), 0.1)
        if not p1: continue
        p2 = astar('RESET_N', 'I2', Point(vx, vy).buffer(0.35), tgt['shape'].buffer(0.05), 0.1)
        print('via', (vx, vy), 'F stub:', bool(p1), 'I2 leg:', bool(p2))
        if p2:
            p1 = g['extend'](g['simplify'](p1))
            for i in range(len(p1) - 1): add_track('RESET_N', *p1[i], *p1[i+1], 0.1, 'F')
            add_via('RESET_N', vx, vy)
            p2 = g['extend'](g['simplify'](p2))
            for i in range(len(p2) - 1): add_track('RESET_N', *p2[i], *p2[i+1], 0.1, 'I2')
            done = True
            break
    if done: break
print('RESET_N done:', done, 'comps:', len(g['components']('RESET_N')))
b.Save(str(g['BPATH']))
