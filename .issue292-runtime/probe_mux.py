import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
from collections import deque
comps = net_components('MUX_A1')
print('comps:', [( [r for _, r in c if r not in ('trk','via')]) for c in comps])
allsh = [s for comp in comps for lay, _ in comp for s in lay.values()]
region = (max(60.0, min(s.bounds[0] for s in allsh) - 3), max(70.0, min(s.bounds[1] for s in allsh) - 3),
          min(140.0, max(s.bounds[2] for s in allsh) + 3), min(140.0, max(s.bounds[3] for s in allsh) + 3))
grids, via_ok, (x0, y0, nx, ny) = rasterize('MUX_A1', 0.05, region, via_field05=True)
fmask = np.zeros((ny, nx), dtype=bool)
for (rx0, ry0, rx1, ry1) in [FIELD] + FANOUT:
    fi0, fi1 = int((rx0-x0)/STEP), int((rx1-x0)/STEP)
    fj0, fj1 = int((ry0-y0)/STEP), int((ry1-y0)/STEP)
    fmask[fj0:fj1+1, fi0:fi1+1] = True
def bfs(L, comp_idx):
    blocked = np.where(fmask, grids[L]['c05'] | ~grids[L]['ok'], grids[L]['c10'] | ~grids[L]['ok'])
    reach = np.zeros((ny, nx), dtype=bool); dq = deque()
    for lay, _ in comps[comp_idx]:
        if L not in lay: continue
        sh = lay[L]
        a, bq, c, d = sh.bounds
        for j in range(max(0, int((bq-y0)/STEP)-1), min(ny-1, int((d-y0)/STEP)+1)+1):
            for i in range(max(0, int((a-x0)/STEP)-1), min(nx-1, int((c-x0)/STEP)+1)+1):
                if sh.contains(Point(x0+i*STEP, y0+j*STEP)) and not reach[j, i]:
                    reach[j, i] = True; dq.append((j, i))
    while dq:
        j, i = dq.popleft()
        for dj, di in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nj, ni = j+dj, i+di
            if 0 <= nj < ny and 0 <= ni < nx and not reach[nj, ni] and not blocked[nj, ni]:
                if di and dj and (blocked[j, ni] or blocked[nj, i]): continue
                reach[nj, ni] = True; dq.append((nj, ni))
    return reach
for ci in range(len(comps)):
    for L in LAYERS:
        r = bfs(L, ci)
        ys, xs = np.nonzero(r)
        if len(xs) == 0: print(f'comp{ci} {L}: no seeds'); continue
        print(f'comp{ci} {L}: cells {len(xs)} x {(x0+xs.min()*STEP).round(1)}..{(x0+xs.max()*STEP).round(1)} y {(y0+ys.min()*STEP).round(1)}..{(y0+ys.max()*STEP).round(1)} via_ok&reach {int((via_ok & r).sum())}')
