import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
from collections import deque
comps = net_components('VBAT_SENSE')
region = (71.0, 78.0, 109.0, 129.0)
grids, via_ok, (x0, y0, nx, ny) = rasterize('VBAT_SENSE', 0.1, region, via_field05=True)
fmask = np.zeros((ny, nx), dtype=bool)
for (fx0, fy0, fx1, fy1) in [FIELD] + FANOUT:
    fi0 = max(0, int((fx0-x0)/STEP)); fi1 = min(nx-1, int((fx1-x0)/STEP))
    fj0 = max(0, int((fy0-y0)/STEP)); fj1 = min(ny-1, int((fy1-y0)/STEP))
    fmask[fj0:fj1+1, fi0:fi1+1] = True
blocked = {L: np.where(fmask, grids[L]['c05'] | ~grids[L]['ok'], grids[L]['c10'] | ~grids[L]['ok']) for L in LAYERS}
def seeds(ci):
    cells = set()
    for lay, _ in comps[ci]:
        for L, sh in lay.items():
            a, bq, c, d = sh.bounds
            for j in range(max(0, int((bq-y0)/STEP)-1), min(ny-1, int((d-y0)/STEP)+1)+1):
                for i in range(max(0, int((a-x0)/STEP)-1), min(nx-1, int((c-x0)/STEP)+1)+1):
                    if sh.contains(Point(x0+i*STEP, y0+j*STEP)): cells.add((L, j, i))
    return cells
target = seeds(1) | seeds(2)
reach = set(seeds(0)); dq = deque(reach)
hit = None
while dq:
    L, j, i = dq.popleft()
    if (L, j, i) in target: hit = (L, j, i); break
    if via_ok[j, i]:
        for L2 in LAYERS:
            if L2 != L and (L2, j, i) not in reach:
                reach.add((L2, j, i)); dq.append((L2, j, i))
    for dj, di in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        nj, ni = j+dj, i+di
        if 0 <= nj < ny and 0 <= ni < nx and (L, nj, ni) not in reach and not blocked[L][nj, ni]:
            if di and dj and (blocked[L][j, ni] or blocked[L][nj, i]): continue
            reach.add((L, nj, ni)); dq.append((L, nj, ni))
print('BFS hit target:', hit, 'at', (round(x0+hit[2]*STEP, 2), round(y0+hit[1]*STEP, 2)) if hit else None)
from collections import Counter
print('reach cells per layer:', Counter(L for L, _, _ in reach))
