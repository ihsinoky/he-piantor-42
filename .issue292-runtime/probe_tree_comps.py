import sys
sys.argv = ['tree_router.py']
src = open('.issue292-runtime/tree_router.py').read().split('ok = True')[0]
exec(compile(src, 'tree_router.py', 'exec'))
comps = net_components('ADC_B')
print('ADC_B tree comps:', len(comps))
for ci, comp in enumerate(comps):
    xs, ys = [], []
    for lay, ref in comp:
        sh = list(lay.values())[0]
        xs += [sh.bounds[0], sh.bounds[2]]; ys += [sh.bounds[1], sh.bounds[3]]
    print(' comp', ci, 'pads', [r for l, r in comp if r not in ('trk', 'via')], 'bbox', (round(min(xs), 1), round(min(ys), 1), round(max(xs), 1), round(max(ys), 1)))
