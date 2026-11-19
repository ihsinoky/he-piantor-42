import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for net, lst in PAD_INDEX.items():
    for lay, ref in lst:
        if ref in ('U1.7', 'U1.5'):
            print(ref, net, [round(v, 3) for v in lay['F'].bounds])
