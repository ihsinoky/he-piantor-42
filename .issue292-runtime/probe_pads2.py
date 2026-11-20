import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for (net, ref, sh) in [(n, r, s) for (n, r, s) in PAD_INDEX] if False else []:
    pass
for entry in PAD_INDEX:
    net, ref = entry[0], entry[1]
    if ref in ('J2.6', 'J2.5', 'J2.7', 'J2.4'):
        sh = entry[2]
        print(ref, net, ' '.join(f'{v:.3f}' for v in sh.bounds))
