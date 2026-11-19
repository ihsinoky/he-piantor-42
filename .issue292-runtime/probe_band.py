import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
from collections import Counter
for name, (bx0, bx1, by0, by1) in [('circle band x79-88 y106-126', (79, 88, 106, 126)),
                                   ('north band x79-88 y96-108', (79, 88, 96, 108))]:
    c = Counter()
    for m in MODEL:
        if not m['alive']: continue
        sh = m['shapes'].get('I2')
        if sh is None: continue
        x0, y0, x1, y1 = sh.bounds
        if x1 >= bx0 and x0 <= bx1 and y1 >= by0 and y0 <= by1: c[m['net']] += 1
    print(name, '->', dict(c.most_common(12)))
