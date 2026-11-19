"""Extract a BFS path (0.025 grid, all layers, via hops) from a stranded pad
to the south band (y >= 125.0, x <= 79.0, cell free or via_ok), emit it as
copper on the work board, and report the path's exact min clearances.
Usage: kpy.sh extract_path.py NET PADREF
"""
import sys
ARGS = sys.argv[1:]
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
from collections import deque

NET, PADREF = ARGS[0], ARGS[1]
STEP = 0.025
comps = net_components(NET)
si = [i for i, c in enumerate(comps) if any(r == PADREF for _, r in c)][0]
sb = [s.bounds for lay, _ in comps[si] for s in lay.values()]
region = (max(60.0, min(x[0] for x in sb) - 3), max(70.0, min(x[1] for x in sb) - 6),
          min(100.0, max(x[2] for x in sb) + 10), min(140.0, max(x[3] for x in sb) + 6))
grids, via_ok, (x0, y0, nx, ny) = rasterize(NET, 0.05, region, via_field05=True)
globals()['X0G'], globals()['Y0G'] = x0, y0
fmask = np.zeros((ny, nx), dtype=bool)
for (fx0, fy0, fx1, fy1) in [FIELD] + FANOUT:
    fi0 = max(0, int((fx0 - x0) / STEP)); fi1 = min(nx - 1, int((fx1 - x0) / STEP))
    fj0 = max(0, int((fy0 - y0) / STEP)); fj1 = min(ny - 1, int((fy1 - y0) / STEP))
    fmask[fj0:fj1 + 1, fi0:fi1 + 1] = True
blocked = {L: np.where(fmask, grids[L]['c05'] | ~grids[L]['ok'],
                       grids[L]['c10'] | ~grids[L]['ok']) for L in LAYERS}
parent = {}
dq = deque()
for lay, _ in comps[si]:
    for L, sh in lay.items():
        a, bq, c, d = sh.bounds
        for j in range(max(0, int((bq - y0) / STEP) - 1), min(ny - 1, int((d - y0) / STEP) + 1) + 1):
            for i in range(max(0, int((a - x0) / STEP) - 1), min(nx - 1, int((c - x0) / STEP) + 1) + 1):
                if sh.contains(Point(x0 + i * STEP, y0 + j * STEP)) and (L, j, i) not in parent:
                    parent[(L, j, i)] = None; dq.append((L, j, i))
target = None
while dq:
    L, j, i = dq.popleft()
    x, y = x0 + i * STEP, y0 + j * STEP
    if y >= 125.0 and x <= 79.0 and (via_ok[j, i] or not blocked[L][j, i]):
        target = (L, j, i); break
    if via_ok[j, i]:
        for L2 in LAYERS:
            if L2 != L and (L2, j, i) not in parent:
                parent[(L2, j, i)] = (L, j, i); dq.append((L2, j, i))
    for dj, di in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
        nj, ni = j + dj, i + di
        if 0 <= nj < ny and 0 <= ni < nx and (L, nj, ni) not in parent and not blocked[L][nj, ni]:
            if di and dj and (blocked[L][j, ni] or blocked[L][nj, i]): continue
            parent[(L, nj, ni)] = (L, j, i); dq.append((L, nj, ni))
if target is None:
    print('EXTRACT: no path to south band'); sys.exit(1)
path = []
k = target
while k is not None:
    path.append(k); k = parent[k]
path = path[::-1]
print(f'EXTRACT: path {len(path)} cells, end at ({x0 + target[2] * STEP:.2f},{y0 + target[1] * STEP:.2f}) on {target[0]}')
# emit
run = [path[0]]; nadd = 0
for st in path[1:]:
    if st[0] != run[-1][0]:
        nadd += emit_run(NET, 0.05, run)
        add_via(NET, x0 + run[-1][2] * STEP, y0 + run[-1][1] * STEP); nadd += 1
        run = [st]
    else:
        run.append(st)
nadd += emit_run(NET, 0.05, run)
print('EXTRACT: added', nadd, 'items')
# exact min clearance of the new copper vs other nets (per layer) + edge
new_shapes = []
for m in MODEL:
    if m['alive'] and m['net'] == NET:
        for L, sh in m['shapes'].items(): new_shapes.append((L, sh))
worst = 9.9
for L, sh in new_shapes:
    for net2, osh in all_obs(L):
        if net2 == NET: continue
        d = sh.distance(osh)
        if d < worst: worst = d
print('EXTRACT: worst exact clearance of ALL', NET, 'copper vs other nets:', round(worst, 4))
p.SaveBoard(DST, b)
print('saved')
