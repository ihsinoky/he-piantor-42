import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for m in MODEL:
    if not m['alive'] or m['net'] != 'LED_DRV': continue
    sh = m['shapes'].get('B')
    if sh is None: continue
    print('B', 'via' if m['via'] else 'trk', tuple(round(v, 2) for v in sh.bounds))
