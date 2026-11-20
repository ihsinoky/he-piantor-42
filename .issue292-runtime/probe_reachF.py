import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.strtree import STRtree
from shapely.geometry import Point
from collections import deque
NET, REF, LAY = sys.argv[1] if len(sys.argv) > 1 else 'MUX_A0', 'U1.5', 'F'
import os
NET = os.environ.get('P_NET', 'MUX_A0'); REF = os.environ.get('P_REF', 'U1.5'); LAY = os.environ.get('P_LAY', 'F')
obs = []
for n2, s2 in all_obs(LAY):
    if n2 != NET: obs.append(s2.buffer(0.075))
tree_u = STRtree(obs)
start = None
for lay, r in PAD_INDEX[NET]:
    if r == REF: start = list(lay.values())[0].centroid
OUTL_E = OUTLINE.buffer(-0.575)
STEP = 0.05
seen = {(round(start.x / STEP), round(start.y / STEP))}
dq = deque(seen)
while dq:
    i, j = dq.popleft()
    for di, dj in ((1, 0), (-1, 0), (0, 1), (0, -1)):
        ni, nj = i + di, j + dj
        if (ni, nj) in seen: continue
        pt = Point(ni * STEP, nj * STEP)
        if not OUTL_E.contains(pt): continue
        if len(tree_u.query(pt)) > 0: continue
        seen.add((ni, nj)); dq.append((ni, nj))
xs = [i * STEP for i, j in seen]; ys = [j * STEP for i, j in seen]
print(f'{REF} {LAY}-reach cells: {len(seen)} bbox x {min(xs):.2f}..{max(xs):.2f} y {min(ys):.2f}..{max(ys):.2f}')
