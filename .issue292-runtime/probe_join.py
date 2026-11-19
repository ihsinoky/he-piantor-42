import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
region = (72.0, 104.0, 108.0, 130.0)
grids, via_ok, (x0, y0, nx, ny) = rasterize('VBAT_SENSE', 0.1, region, via_field05=True)
fmask = np.zeros((ny, nx), dtype=bool)
for (fx0, fy0, fx1, fy1) in [FIELD] + FANOUT:
    fi0 = max(0, int((fx0-x0)/STEP)); fi1 = min(nx-1, int((fx1-x0)/STEP))
    fj0 = max(0, int((fy0-y0)/STEP)); fj1 = min(ny-1, int((fy1-y0)/STEP))
    fmask[fj0:fj1+1, fi0:fi1+1] = True
blockedI2 = np.where(fmask, grids['I2']['c05'] | ~grids['I2']['ok'], grids['I2']['c10'] | ~grids['I2']['ok'])
print('I2 map (v=via_ok&free, .=free, #=blocked), cols x=72+k*0.6, rows y=104+r*0.65')
for r in range(40):
    y = 104.0 + r*0.65; j0 = int((y-y0)/STEP); row = ''
    for k in range(60):
        x = 72.0 + k*0.6; i0 = int((x-x0)/STEP)
        blk = blockedI2[j0:j0+13, i0:i0+12]
        via = via_ok[j0:j0+13, i0:i0+12]
        if blk.all(): row += '#'
        elif via.any() and not blk.all(): row += 'v'
        else: row += '.'
    print(f'{y:6.2f} {row}')
