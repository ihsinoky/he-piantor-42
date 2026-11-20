import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
from collections import deque
STEP = 0.025
comps = net_components('VBAT_SENSE')
region = (71.0, 78.0, 109.0, 129.0)
grids, via_ok, (x0, y0, nx, ny) = rasterize('VBAT_SENSE', 0.05, region, via_field05=True)
fmask = np.zeros((ny, nx), dtype=bool)
for (fx0, fy0, fx1, fy1) in [FIELD] + FANOUT:
    fi0 = max(0, int((fx0-x0)/STEP)); fi1 = min(nx-1, int((fx1-x0)/STEP))
    fj0 = max(0, int((fy0-y0)/STEP)); fj1 = min(ny-1, int((fy1-y0)/STEP))
    fmask[fj0:fj1+1, fi0:fi1+1] = True
blocked = {L: np.where(fmask, grids[L]['c05'] | ~grids[L]['ok'], grids[L]['c10'] | ~grids[L]['ok']) for L in LAYERS}
reach = {L: np.zeros((ny, nx), dtype=bool) for L in LAYERS}
dq = deque()
for lay, _ in comps[0]:
    for L, sh in lay.items():
        a, bq, c, d = sh.bounds
        for j in range(max(0, int((bq-y0)/STEP)-1), min(ny-1, int((d-y0)/STEP)+1)+1):
            for i in range(max(0, int((a-x0)/STEP)-1), min(nx-1, int((c-x0)/STEP)+1)+1):
                if sh.contains(Point(x0+i*STEP, y0+j*STEP)) and not reach[L][j, i]:
                    reach[L][j, i] = True; dq.append((L, j, i))
while dq:
    L, j, i = dq.popleft()
    if via_ok[j, i]:
        for L2 in LAYERS:
            if L2 != L and not reach[L2][j, i]:
                reach[L2][j, i] = True; dq.append((L2, j, i))
    for dj, di in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        nj, ni = j+dj, i+di
        if 0 <= nj < ny and 0 <= ni < nx and not reach[L][nj, ni] and not blocked[L][nj, ni]:
            if di and dj and (blocked[L][j, ni] or blocked[L][nj, i]): continue
            reach[L][nj, ni] = True; dq.append((L, nj, ni))
# closest approach: for each target shape, distance from reached cells (sampled via shape distance to reach mask points)
from shapely.geometry import MultiPoint
for ci in (1, 2):
    best = (9e9, None)
    for lay, _ in comps[ci]:
        for L, sh in lay.items():
            ys, xs = np.nonzero(reach[L])
            if len(xs) == 0: continue
            pts = MultiPoint([(x0 + i * STEP, y0 + j * STEP) for j, i in zip(ys[::7], xs[::7])])
            d = sh.distance(pts)
            if d < best[0]: best = (d, (L, tuple(round(v, 1) for v in sh.bounds)))
    print(f'target comp {ci}: closest reached-cell distance {best[0]:.3f} via {best[1]}')
for L in LAYERS:
    ys, xs = np.nonzero(reach[L])
    print(L, 'reach x', round(x0 + xs.min() * STEP, 1), round(x0 + xs.max() * STEP, 1), 'y', round(y0 + ys.min() * STEP, 1), round(y0 + ys.max() * STEP, 1), 'cells', len(xs))
