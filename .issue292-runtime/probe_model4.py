import sys
sys.argv = ['tree_router.py']
src = open('.issue292-runtime/tree_router.py').read().split('ok = True')[0]
exec(compile(src, 'tree_router.py', 'exec'))
for m in MODEL:
    if m['net'] != 'ADC_B' or m['via']: continue
    o = m['obj']
    s, e = o.GetStart(), o.GetEnd()
    x0, y0 = s.x/1e6, s.y/1e6
    if abs(x0 - 73.15) < 0.01 and abs(y0 - 121.15) < 0.01:
        print('track', o.GetLayerName(), (x0, y0), (e.x/1e6, e.y/1e6))
        for L, sh in m['shapes'].items():
            print('  shape', L, tuple(round(v, 3) for v in sh.bounds), 'area', round(sh.area, 4), 'type', sh.geom_type)
