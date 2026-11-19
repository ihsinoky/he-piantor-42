import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for net, lst in PAD_INDEX.items():
    for lay, ref in lst:
        if ref in ('J2.6', 'J2.5', 'J2.7', 'J2.4'):
            for L, sh in lay.items():
                print(ref, net, L, ' '.join(f'{v:.3f}' for v in sh.bounds))
