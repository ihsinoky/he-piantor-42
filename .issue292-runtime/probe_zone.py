import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for m in MODEL:
    if not m['alive'] or m['net'] not in ('PAD_SCL', 'MUX_A0'): continue
    for L, sh in m['shapes'].items():
        x0, y0, x1, y1 = sh.bounds
        if x1 >= 70 and x0 <= 78 and y1 >= 112 and y0 <= 120:
            print(m['net'], L, 'via' if m['via'] else 'trk', tuple(round(v, 2) for v in sh.bounds))
