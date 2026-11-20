import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
items = []
for m in MODEL:
    if not m['alive'] or m['net'] != 'LED_DRV': continue
    sh = m['shapes'].get('F')
    if sh is None: continue
    x0, y0, x1, y1 = sh.bounds
    items.append(((x0 + x1) / 2, tuple(round(v, 2) for v in sh.bounds), 'via' if m['via'] else 'trk'))
for cx, b, k in sorted(items)[:10]: print(k, b)
