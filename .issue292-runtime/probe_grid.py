import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
import numpy as np
STEP = 0.025
region = (69.8, 116.4, 98.2, 127.8)
grids, via_ok, (x0, y0, nx, ny) = rasterize('PAD_SCL', 0.05, region, via_field05=True)
def cell(x, y):
    i, j = int(round((x - x0) / STEP)), int(round((y - y0) / STEP))
    return dict(c05=bool(grids['F']['c05'][j, i]), c10=bool(grids['F']['c10'][j, i]), ok=bool(grids['F']['ok'][j, i]))
for pt in [(72.275, 122.575), (71.825, 122.575), (72.05, 122.8), (72.05, 122.35), (72.05, 122.575)]:
    print(pt, cell(*pt))
