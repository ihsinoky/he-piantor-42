import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
from collections import deque
region = (69.5, 117.5, 84.5, 130.5)
grids, via_ok, (x0, y0, nx, ny) = rasterize('PAD_SCL', 0.05, region, via_field05=True)
fmask = np.zeros((ny, nx), dtype=bool)
for (fx0, fy0, fx1, fy1) in [FIELD] + FANOUT:
    fi0 = max(0, int((fx0-x0)/STEP)); fi1 = min(nx-1, int((fx1-x0)/STEP))
    fj0 = max(0, int((fy0-y0)/STEP)); fj1 = min(ny-1, int((fy1-y0)/STEP))
    fmask[fj0:fj1+1, fi0:fi1+1] = True
blocked = np.where(fmask, grids['F']['c05'] | ~grids['F']['ok'], grids['F']['c10'] | ~grids['F']['ok'])
comps = net_components('PAD_SCL')
si = [i for i, c in enumerate(comps) if any(r == 'U1.3' for _, r in c)][0]
reach = np.zeros((ny, nx), dtype=bool); dq = deque()
for lay, _ in comps[si]:
    if 'F' not in lay: continue
    sh = lay['F']; a, bq, c, d = sh.bounds
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
print('via_ok cells inside F reach:', int((via_ok & reach).sum()))
# ASCII: cols x 69.5..84.5 step 0.25, rows y 117.5..130.5 step 0.25; R=reach, v=via_ok free, .=free, #=blocked
for r in range(52):
    y = 117.5 + r*0.25; j0 = int((y-y0)/STEP); row = ''
    for k in range(60):
        x = 69.5 + k*0.25; i0 = int((x-x0)/STEP)
        sub_r = reach[j0:j0+5, i0:i0+5]; sub_b = blocked[j0:j0+5, i0:i0+5]; sub_v = via_ok[j0:j0+5, i0:i0+5]
        if sub_r.any(): row += 'R'
        elif sub_b.all(): row += '#'
        elif sub_v.any() and not sub_b.all(): row += 'v'
        else: row += '.'
    print(f'{y:6.2f} {row}')
