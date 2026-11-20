import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for m in MODEL:
    if not m['alive']: continue
    for L in ('F', 'I2', 'B'):
        sh = m['shapes'].get(L)
        if sh is None: continue
        x0, y0, x1, y1 = sh.bounds
        if x1 >= 70.3 and x0 <= 71.25 and y1 >= 118.8 and y0 <= 123.4:
            print(L, m['net'], 'via' if m['via'] else 'trk', tuple(round(v, 2) for v in sh.bounds))
for n2, s2 in all_obs('F'):
    x0, y0, x1, y1 = s2.bounds
    if x1 >= 70.3 and x0 <= 71.25 and y1 >= 118.8 and y0 <= 123.4:
        print('PAD/OBS F', n2, tuple(round(v, 2) for v in s2.bounds))
