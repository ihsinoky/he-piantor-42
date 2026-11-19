import sys, os
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.strtree import STRtree
from shapely.geometry import Point
from collections import deque
NET = os.environ.get('P_NET', 'PAD_SCL'); LAY = os.environ.get('P_LAY', 'I2')
SX, SY = [float(v) for v in os.environ.get('P_START', '73.05,126.25').split(',')]
obs = [s2.buffer(0.075) for n2, s2 in all_obs(LAY) if n2 != NET]
tree_u = STRtree(obs)
OUTL_E = OUTLINE.buffer(-0.575)
STEP = 0.05
start = (round(SX / STEP), round(SY / STEP))
seen = {start}; dq = deque([start])
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
print(f'{NET} {LAY}-reach from ({SX},{SY}): {len(seen)} cells bbox x {min(xs):.2f}..{max(xs):.2f} y {min(ys):.2f}..{max(ys):.2f}')
# does reach come within 0.3 of the vertical (72.05, 114.75-117.0) or chain (74.55,109.6)?
def near(x, y): return any(abs(i * STEP - x) < 0.35 and abs(j * STEP - y) < 0.35 for i, j in seen)
print('near vertical south end (72.05,117.0):', near(72.05, 117.0), '| near chain west (74.55,109.6):', near(74.55, 109.6))
