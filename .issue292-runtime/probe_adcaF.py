import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for n2, s2 in all_obs('F'):
    if n2 != 'ADC_A': continue
    x0, y0, x1, y1 = s2.bounds
    if x1 >= 70.0 and x0 <= 73.0 and y1 >= 118.5 and y0 <= 121.5:
        print('F ADC_A', tuple(round(v, 3) for v in s2.bounds))
