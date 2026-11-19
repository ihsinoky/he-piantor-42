import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for m in MODEL:
    if not m['alive']: continue
    sh = m['shapes'].get('F')
    if sh is None: continue
    x0, y0, x1, y1 = sh.bounds
    if x1 >= 71.0 and x0 <= 72.3 and y1 >= 116.5 and y0 <= 119.0:
        print(m['net'], 'via' if m['via'] else 'trk', tuple(round(v, 2) for v in sh.bounds))
for n2, s2 in all_obs('F'):
    x0, y0, x1, y1 = s2.bounds
    if x1 >= 71.0 and x0 <= 72.3 and y1 >= 116.5 and y0 <= 119.0:
        print('OBS', n2, tuple(round(v, 2) for v in s2.bounds))
