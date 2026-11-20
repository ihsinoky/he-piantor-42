import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for m in MODEL:
    if not m['alive']: continue
    sh = m['shapes'].get('I2')
    if sh is None: continue
    x0, y0, x1, y1 = sh.bounds
    if x1 >= 69.8 and x0 <= 72.2 and y1 >= 116.8 and y0 <= 120.2:
        print(m['net'], 'via' if m['via'] else 'trk', tuple(round(v, 2) for v in sh.bounds))
