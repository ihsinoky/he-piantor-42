import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from collections import Counter
for L in ('F', 'I2', 'B'):
    c = Counter()
    for n2, s2 in all_obs(L):
        x0, y0, x1, y1 = s2.bounds
        if y0 <= 119.0 <= y1 and x1 >= 70 and x0 <= 80: c[n2] += 1
    print(L, 'items crossing y=119.0 in x70-80:', dict(c.most_common(10)))
