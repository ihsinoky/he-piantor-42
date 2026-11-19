import sys
ARGS = sys.argv[1:]
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
NET = ARGS[0]
for m in MODEL:
    if not m['alive'] or m['net'] != NET: continue
    for L, sh in m['shapes'].items():
        for net2, osh in all_obs(L):
            if net2 == NET: continue
            d = sh.distance(osh)
            if d < 0.04:
                print(f'{L} d={d:.3f} vs {net2} at {tuple(round(v,2) for v in sh.bounds)} vs {tuple(round(v,2) for v in osh.bounds)}')
