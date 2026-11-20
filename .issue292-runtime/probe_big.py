import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for L in ('I2', 'B', 'F'):
    obs = sorted(all_obs(L), key=lambda t: -t[1].area)[:5]
    print(L, [(n, round(s.area, 1), tuple(round(v, 1) for v in s.bounds)) for n, s in obs])
