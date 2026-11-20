import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read()
src = src.split("if __name__ == '__main__':")[0] if "__main__" in src else src
src = src.split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.strtree import STRtree
from shapely.geometry import Point
from collections import deque
NET, REF = 'MUX_A0', 'U1.5'
OUTLINE_ER05 = OUTLINE.buffer(-0.575)
# all-layer union obstacles (pads all layers + tracks all layers), 0.05 clr, own net free
obs = []
for n2, s2 in all_obs('F') + all_obs('I2') + all_obs('B'):
    if n2 != NET: obs.append(s2.buffer(0.05))
tree_u = STRtree(obs)
start = None
for lay, r in PAD_INDEX[NET]:
    if r == REF: start = list(lay.values())[0].centroid
STEP = 0.05
seen = {(round(start.x / STEP), round(start.y / STEP))}
dq = deque(seen)
while dq:
    i, j = dq.popleft()
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ni, nj = i + di, j + dj
        if (ni, nj) in seen: continue
        cx, cy = ni * STEP, nj * STEP
        pt = Point(cx, cy)
        if not OUTLINE_ER05.contains(pt): continue
        hit = False
        for k in tree_u.query(pt.buffer(0.001)):
            hit = True; break
        if hit: continue
        seen.add((ni, nj)); dq.append((ni, nj))
xs = [i * STEP for i, j in seen]; ys = [j * STEP for i, j in seen]
print(f'{REF} union-reach cells: {len(seen)} bbox x {min(xs):.1f}..{max(xs):.1f} y {min(ys):.1f}..{max(ys):.1f}')
# which seen cells are adjacent to J2.12 pad?
for lay, r in PAD_INDEX[NET]:
    if r == 'J2.12':
        sh = list(lay.values())[0]
        print('J2.12 pad bounds', tuple(round(v, 2) for v in sh.bounds))
