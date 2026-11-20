import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import box as sbox
r = sbox(80.0, 117.5, 100.0, 120.5)
for net, sh in all_obs('I2'):
    if sh.intersects(r):
        print(net, tuple(round(v, 2) for v in sh.bounds), 'area', round(sh.area, 2))
