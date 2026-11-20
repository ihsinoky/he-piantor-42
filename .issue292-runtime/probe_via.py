import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import Point
for pt in [(70.7, 125.5), (70.7, 126.5), (70.6, 127.5), (70.9, 128.3)]:
    P = Point(*pt)
    print('site', pt, 'outline dist', round(OUTLINE.exterior.distance(P), 3) if not OUTLINE.contains(P) else 'inside ' + str(round(-OUTLINE.exterior.distance(P), 3)))
    for L in LAYERS:
        ds = sorted((round(P.distance(sh) - 0.3, 3), net) for net, sh in all_obs(L) if net != 'MUX_A1' and P.distance(sh) < 1.0)
        print('  ', L, ds[:4])
