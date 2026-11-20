import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
from collections import deque
STEP = 0.025
comps = net_components('PAD_SCL')
si = [i for i, c in enumerate(comps) if any(r == 'U1.3' for _, r in c)][0]
region = (69.8, 116.4, 98.2, 127.8)
grids, via_ok, (x0, y0, nx, ny) = rasterize('PAD_SCL', 0.05, region, via_field05=True)
fmask = np.zeros((ny, nx), dtype=bool)
for (fx0, fy0, fx1, fy1) in [FIELD] + FANOUT:
    fi0 = max(0, int((fx0-x0)/STEP)); fi1 = min(nx-1, int((fx1-x0)/STEP))
    fj0 = max(0, int((fy0-y0)/STEP)); fj1 = min(ny-1, int((fy1-y0)/STEP))
    fmask[fj0:fj1+1, fi0:fi1+1] = True
blocked = {L: np.where(fmask, grids[L]['c05'] | ~grids[L]['ok'], grids[L]['c10'] | ~grids[L]['ok']) for L in LAYERS}
reach = {L: np.zeros((ny, nx), dtype=bool) for L in LAYERS}
dq = deque()
for lay, _ in comps[si]:
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
for L in LAYERS:
    ys, xs = np.nonzero(reach[L])
    print(L, 'cells', len(xs), 'x', (x0+xs.min()*STEP).round(2), (x0+xs.max()*STEP).round(2), 'y', (y0+ys.min()*STEP).round(2), (y0+ys.max()*STEP).round(2))
# ASCII of F reachability x 69.5..73.5 (0.1 cols), y 122..129 (0.2 rows)
print('F reach map (R=reachable, .=free, #=blocked):')
for r in range(35):
    y = 122.0 + r*0.2; j0 = int((y-y0)/STEP); row = ''
    for k in range(40):
        x = 69.5 + k*0.1; i0 = int((x-x0)/STEP)
        if reach['F'][j0:j0+8, i0:i0+4].any(): row += 'R'
        elif blocked['F'][j0:j0+8, i0:i0+4].all(): row += '#'
        else: row += '.'
    print(f'{y:5.1f} {row}')
