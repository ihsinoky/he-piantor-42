import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for n2, s2 in all_obs('B'):
    x0, y0, x1, y1 = s2.bounds
    if x1 >= 71.3 and x0 <= 75.5 and y1 >= 112.5 and y0 <= 126.2:
        print('B', n2, tuple(round(v, 2) for v in s2.bounds))
