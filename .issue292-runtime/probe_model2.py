import sys
sys.argv = ['tree_router.py']
src = open('.issue292-runtime/tree_router.py').read().split('ok = True')[0]
exec(compile(src, 'tree_router.py', 'exec'))
comps = net_components('ADC_B')
print('comps:', [(len(c), [r for l, r in c if r not in ('trk', 'via')]) for c in comps])
for m in MODEL:
    if m['net'] != 'ADC_B' or m['via']: continue
    for L, sh in m['shapes'].items():
        x0, y0, x1, y1 = sh.bounds
        if x0 < 80 and L == 'F':
            print('F item bounds', tuple(round(v, 2) for v in sh.bounds))
