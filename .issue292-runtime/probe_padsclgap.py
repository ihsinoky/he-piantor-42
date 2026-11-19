import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for m in MODEL:
    if not m['alive'] or m['net'] != 'PAD_SCL': continue
    for L, sh in m['shapes'].items():
        x0, y0, x1, y1 = sh.bounds
        cx = (x0 + x1) / 2
        if 74 <= cx <= 100:
            print(L, 'via' if m['via'] else 'trk', tuple(round(v, 2) for v in sh.bounds))
