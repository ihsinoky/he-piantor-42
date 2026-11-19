import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for lay, r in PAD_INDEX.get('LED_DRV', []):
    print(r, {L: tuple(round(v, 2) for v in s.bounds) for L, s in lay.items()})
