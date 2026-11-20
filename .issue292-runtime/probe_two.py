import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for net, ref in [('LED_DRV', 'U1.56'), ('ADC_B', 'U1.46')]:
    for lay, r in PAD_INDEX.get(net, []):
        if r == ref:
            sh = list(lay.values())[0]
            print(ref, net, 'pad bounds', tuple(round(v, 2) for v in sh.bounds))
            near = sorted((round(sh.distance(s2), 3), n2, tuple(round(v, 2) for v in s2.bounds))
                          for n2, s2 in all_obs('F') if n2 != net and sh.distance(s2) < 0.8)
            for row in near[:8]: print('   ', row)
