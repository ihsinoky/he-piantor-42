import sys
ARGS = sys.argv[1:]
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
net = ARGS[0]
comps = net_components(net)
for ci, comp in enumerate(comps):
    print(f'--- comp {ci}')
    for lay, ref in comp:
        if ref in ('trk', 'via'):
            for L, sh in lay.items():
                print('   ', ref, L, tuple(round(v, 2) for v in sh.bounds))
        else:
            print('   pad', ref, tuple(round(v, 2) for v in list(lay.values())[0].bounds))
