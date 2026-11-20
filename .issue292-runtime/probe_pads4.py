import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for net, lst in PAD_INDEX.items():
    for lay, ref in lst:
        if ref in ('J2.6', 'J2.5'):
            sh = lay['F']
            print(ref, net, [(round(x, 3), round(y, 3)) for x, y in sh.exterior.coords])
