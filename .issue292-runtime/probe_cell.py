import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from shapely.geometry import Point
pad = None
for lay, ref in PAD_INDEX['PAD_SCL']:
    if ref == 'U1.3': pad = lay['F']
print('U1.3 pad:', tuple(round(v, 3) for v in pad.bounds))
w = 0.05
for dx, dy in [(0.05, 0), (-0.05, 0), (0, 0.05), (0, -0.05), (0.05, 0.05), (-0.05, -0.05)]:
    cx, cy = pad.centroid.x + dx + (0.225 if dx > 0 else -0.225 if dx < 0 else 0), pad.centroid.y + dy + (0.225 if dy > 0 else -0.225 if dy < 0 else 0)
    # cell just outside the pad edge in direction (dx,dy): place at pad edge + 0.025
    ex = pad.bounds[2] + 0.025 if dx > 0 else pad.bounds[0] - 0.025 if dx < 0 else pad.centroid.x
    ey = pad.bounds[3] + 0.025 if dy > 0 else pad.bounds[1] - 0.025 if dy < 0 else pad.centroid.y
    P = Point(ex, ey)
    cover = [(net, tuple(round(v, 2) for v in sh.bounds), round(P.distance(sh), 3))
             for net, sh in all_obs('F') if net != 'PAD_SCL' and P.distance(sh) < 0.075 + w/2]
    print(f'cell ({ex:.3f},{ey:.3f}):', cover)
