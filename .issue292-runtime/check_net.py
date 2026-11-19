import sys
ARGS = sys.argv[1:]
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for net in ARGS:
    comps = net_components(net)
    print(net, 'components:', len(comps), [[r for _, r in c if r not in ('trk', 'via')] for c in comps])
