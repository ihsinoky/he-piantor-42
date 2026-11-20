import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import Point
pad = None
for lay, ref in PAD_INDEX['MUX_A1']:
    if ref == 'U1.6': pad = lay['F']
print('U1.6 pad bounds:', tuple(round(v, 3) for v in pad.bounds))
near = []
for net, sh in all_obs('F'):
    if net == 'MUX_A1': continue
    d = pad.distance(sh)
    if d < 1.2: near.append((round(d, 3), net, tuple(round(v, 2) for v in sh.bounds)))
for row in sorted(near)[:16]: print(row)
print('--- no-net zones on F near field:')
for L in ('F',):
    for net, sh in OBS_STATIC[L]:
        if net == '' and sh.bounds[0] < 85 and sh.bounds[2] > 65 and sh.bounds[1] < 135 and sh.bounds[3] > 115:
            print(' zone fill bounds:', tuple(round(v, 2) for v in sh.bounds), 'area', round(sh.area, 1))
