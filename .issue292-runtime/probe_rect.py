import sys
ARGS = sys.argv[1:]
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import box as sbox
import sys as s2
x0, y0, x1, y1 = [float(v) for v in ARGS[0:4]]
L = ARGS[4] if len(ARGS) > 4 else 'F'
r = sbox(x0, y0, x1, y1)
rows = []
for net, sh in all_obs(L):
    if sh.intersects(r):
        rows.append((round(sh.bounds[1], 2), round(sh.bounds[0], 2), net, tuple(round(v, 2) for v in sh.bounds)))
for row in sorted(rows): print(row[2], row[3])
