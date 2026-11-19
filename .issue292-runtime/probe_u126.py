import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
from collections import deque
delete_west('SYS_3V3')
comps = net_components('SYS_3V3')
idx = [i for i, c in enumerate(comps) if any(r == 'U1.26' for _, r in c)][0]
print('U1.26 comp index:', idx, 'of', len(comps))
allsh = [s for comp in comps for lay, _ in comp for s in lay.values()]
region = (max(60.0, min(s.bounds[0] for s in allsh) - 3), max(70.0, min(s.bounds[1] for s in allsh) - 3),
          min(140.0, max(s.bounds[2] for s in allsh) + 3), min(140.0, max(s.bounds[3] for s in allsh) + 3))
grids, via_ok, (x0, y0, nx, ny) = rasterize('SYS_3V3', 0.05, region)
# via cell for (79.4,124.2)
vi, vj = int(round((79.4 - x0) / STEP)), int(round((124.2 - y0) / STEP))
print('via_ok at original via site:', via_ok[vj, vi])
print('via_ok density near field:', via_ok[int((119-y0)/STEP):int((129-y0)/STEP), int((70-x0)/STEP):int((81-x0)/STEP)].mean().round(3))
# BFS on F from island seeds at field clr
lab = np.full((ny, nx), -1, dtype=np.int32)
for lay, _ in comps[idx]:
    for L, sh in lay.items():
        a, bq, c, d = sh.bounds
        for j in range(max(0, int((bq-y0)/STEP)-1), min(ny-1, int((d-y0)/STEP)+1)+1):
            for i in range(max(0, int((a-x0)/STEP)-1), min(nx-1, int((c-x0)/STEP)+1)+1):
                if sh.contains(Point(x0 + i*STEP, y0 + j*STEP)): lab[j, i] = 0
fmask = np.zeros((ny, nx), dtype=bool)
fi0, fi1 = int((FIELD[0]-x0)/STEP), int((FIELD[2]-x0)/STEP)
fj0, fj1 = int((FIELD[1]-y0)/STEP), int((FIELD[3]-y0)/STEP)
fmask[fj0:fj1+1, fi0:fi1+1] = True
blockedF = np.where(fmask, grids['F']['c05'] | ~grids['F']['ok'], grids['F']['c10'] | ~grids['F']['ok'])
reach = np.zeros((ny, nx), dtype=bool)
dq = deque()
jj, ii = np.nonzero(lab >= 0)
for j, i in zip(jj.tolist(), ii.tolist()):
    if not reach[j, i]: reach[j, i] = True; dq.append((j, i))
while dq:
    j, i = dq.popleft()
    for dj, di in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
        nj, ni = j+dj, i+di
        if 0 <= nj < ny and 0 <= ni < nx and not reach[nj, ni] and not blockedF[nj, ni]:
            if di and dj and (blockedF[j, ni] or blockedF[nj, i]): continue
            reach[nj, ni] = True; dq.append((nj, ni))
ys, xs = np.nonzero(reach)
print('F reachable from U1.26: cells', len(xs), 'x range', (x0+xs.min()*STEP).round(2), (x0+xs.max()*STEP).round(2),
      'y range', (y0+ys.min()*STEP).round(2), (y0+ys.max()*STEP).round(2))
print('via cell reachable on F:', reach[vj, vi])
# how many via_ok cells are inside the F-reachable set (layer hop potential)
hop = int((via_ok & reach).sum())
print('via_ok cells reachable on F:', hop)
