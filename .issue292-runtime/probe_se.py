import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for L in ('F', 'I2', 'B'):
    for n2, s2 in all_obs(L):
        x0, y0, x1, y1 = s2.bounds
        if x1 >= 73.3 and x0 <= 74.4 and y1 >= 123.9 and y0 <= 126.7:
            print(L, n2, tuple(round(v, 2) for v in s2.bounds))
