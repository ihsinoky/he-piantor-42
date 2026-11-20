import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
region = (69.8, 119.5, 73.2, 125.8)
grids, via_ok, (x0, y0, nx, ny) = rasterize('MUX_A1', 0.05, region, via_field05=True)
fmask = np.zeros((ny, nx), dtype=bool)
for (rx0, ry0, rx1, ry1) in [FIELD] + FANOUT:
    fi0, fi1 = int((rx0-x0)/STEP), int((rx1-x0)/STEP)
    fj0, fj1 = int((ry0-y0)/STEP), int((ry1-y0)/STEP)
    fmask[fj0:fj1+1, fi0:fi1+1] = True
blocked = np.where(fmask, grids['F']['c05'] | ~grids['F']['ok'], grids['F']['c10'] | ~grids['F']['ok'])
# ASCII: x 69.5..74.5 step 0.1 (2 cells), y 120..128 step 0.2 (4 cells): cell shown blocked if ANY subcell blocked
print('   ' + ''.join(str(int((69.5 + k*0.1) % 10)) for k in range(50)))
for r in range(32):
    y = 119.5 + r * 0.2
    j0 = int((y - y0) / STEP)
    row = ''
    for k in range(50):
        x = 69.5 + k * 0.1
        i0 = int((x - x0) / STEP)
        blk = blocked[j0:j0+4, i0:i0+2].any()
        via = via_ok[j0:j0+4, i0:i0+2].any()
        row += ('#' if blk else ('v' if via else '.'))
    print(f'{y:5.1f} {row}')
