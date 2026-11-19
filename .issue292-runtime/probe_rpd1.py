import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for lay, ref in [(l, r) for net in ('HALL_PWR_EN', 'HALL_3V3') for l, r in PAD_INDEX.get(net, [])]:
    if ref.startswith(('RPD1', 'CHOUT')):
        sh = list(lay.values())[0]
        print(ref, tuple(round(v, 2) for v in sh.bounds), 'outline dist', round(OUTLINE.distance(sh), 3))
print('outline vertices near:', [(round(x, 2), round(y, 2)) for x, y in OUTLINE.exterior.coords if x > 125 and y > 120])
