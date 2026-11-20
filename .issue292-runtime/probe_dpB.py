import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for L in ('B', 'F', 'I2'):
    for n2, s2 in all_obs(L):
        if n2 != 'USB_DP': continue
        x0, y0, x1, y1 = s2.bounds
        if x1 >= 71.8 and x0 <= 73.2 and y1 >= 123.5 and y0 <= 126.2:
            print(L, n2, tuple(round(v, 3) for v in s2.bounds))
