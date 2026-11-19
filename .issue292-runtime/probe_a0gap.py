import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for L in ('F', 'I2', 'B'):
    for n2, s2 in all_obs(L):
        if n2 not in ('SYS_3V3', 'USB_DM', 'MUX_A0'): continue
        x0, y0, x1, y1 = s2.bounds
        if x1 >= 70.8 and x0 <= 72.6 and y1 >= 118.3 and y0 <= 120.2:
            print(L, n2, tuple(round(v, 2) for v in s2.bounds))
