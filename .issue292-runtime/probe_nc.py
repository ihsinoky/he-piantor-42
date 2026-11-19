import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for n2, s2 in all_obs('F'):
    x0, y0, x1, y1 = s2.bounds
    if x1 >= 70.9 and x0 <= 71.8 and y1 >= 121.3 and y0 <= 122.4:
        print(repr(n2), tuple(round(v, 2) for v in s2.bounds), 'area', round(s2.area, 3))
