import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
region = (71.0, 78.0, 109.0, 129.0)
grids, via_ok, (x0, y0, nx, ny) = rasterize('VBAT_SENSE', 0.05, region, via_field05=True)
for x in (75.0, 85.0, 90.0, 100.0):
    i = int(round((x - x0) / STEP))
    col = []
    for y in [116.0, 117.0, 118.0, 118.5, 119.0, 119.5, 120.0, 121.0]:
        j = int(round((y - y0) / STEP))
        col.append((y, bool(grids['I2']['c10'][j, i]), bool(grids['I2']['c05'][j, i]), bool(grids['I2']['ok'][j, i])))
    print('x=', x, '(y, c10, c05, ok):', col)
