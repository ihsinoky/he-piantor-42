src = open('s3b_merge9.py').read().split('total_added = 0')[0]
g = {}
exec(src, g)
from shapely.geometry import Point, LineString
b = g['b']; astar, add_track = g['astar'], g['add_track']

# GND: pad16 -> south loop -> pad18 chain track (76.2,125.0)-(76.5,125.0)
chain = LineString([(76.2, 125.0), (76.5, 125.0)]).buffer(0.1)
cur = Point(75.1, 124.65).buffer(0.15)
ok = True
for wp in [(74.95, 125.7), (76.2, 125.7)]:
    path = astar('GND', 'F', cur, Point(*wp).buffer(0.25), 0.2)
    print('GND F ->', wp, 'OK' if path else None)
    if not path: ok = False; break
    path = g['extend'](g['simplify'](path))
    for i in range(len(path) - 1): add_track('GND', *path[i], *path[i+1], 0.2, 'F')
    cur = Point(*path[-1]).buffer(0.05)
if ok:
    path = astar('GND', 'F', cur, chain, 0.2)
    print('GND F -> chain:', 'OK' if path else None)
    if path:
        path = g['extend'](g['simplify'](path))
        for i in range(len(path) - 1): add_track('GND', *path[i], *path[i+1], 0.2, 'F')
b.Save(str(g['BPATH']))

# RESET_N: flood I2 from drop via
from collections import deque
def flood(net, L, seed_pt, box, step=0.25, infl=0.15):
    x0, x1, y0, y1 = box
    nx, ny = int((x1-x0)/step), int((y1-y0)/step)
    tree, shapes, nets = g['IDX'][(L, infl)]
    def blocked(gx, gy):
        pt = Point(x0 + gx*step, y0 + gy*step)
        return any(nets[i] != net and shapes[i].intersects(pt) for i in tree.query(pt))
    seed = Point(*seed_pt).buffer(0.3)
    seen = set(); dq = deque()
    for gy in range(ny):
        for gx in range(nx):
            if seed.intersects(Point(x0+gx*step, y0+gy*step)):
                seen.add((gx, gy)); dq.append((gx, gy))
    while dq:
        cx, cy = dq.popleft()
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                nk = (cx+dx, cy+dy)
                if nk in seen or not (0 <= nk[0] < nx and 0 <= nk[1] < ny): continue
                if blocked(*nk): continue
                seen.add(nk); dq.append(nk)
    xs = [x0+gx*step for gx, gy in seen]; ys = [y0+gy*step for gx, gy in seen]
    return len(seen), (min(xs), max(xs), min(ys), max(ys))
print('RESET_N I2 flood from drop via:', flood('RESET_N', 'I2', (73.55, 119.35), (68, 95, 100, 128)))
print('RESET_N F flood from stub:', flood('RESET_N', 'F', (73.55, 119.35), (68, 95, 100, 128)))
