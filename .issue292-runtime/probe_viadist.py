import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import Point
disc = Point(79.4, 124.2).buffer(0.30)
for L in ('F', 'I2', 'B'):
    near = sorted((round(disc.distance(s2), 3), n2) for n2, s2 in all_obs(L) if n2 != 'SYS_3V3')[:4]
    print(L, near)
