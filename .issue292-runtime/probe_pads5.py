import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for net, lst in PAD_INDEX.items():
    for lay, ref in lst:
        if not ref.startswith('U1.'): continue
        sh = lay['F']
        cx = (sh.bounds[0] + sh.bounds[2]) / 2; cy = (sh.bounds[1] + sh.bounds[3]) / 2
        if 74.2 < cx < 76.0 and 124.3 < cy < 125.0:
            print(ref, net, f'{cx:.2f},{cy:.2f}')
