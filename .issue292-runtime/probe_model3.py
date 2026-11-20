import sys
sys.argv = ['tree_router.py']
src = open('.issue292-runtime/tree_router.py').read().split('ok = True')[0]
exec(compile(src, 'tree_router.py', 'exec'))
pad = None
for lay, ref in PAD_INDEX.get('ADC_B', []):
    if ref == 'U1.46': pad = list(lay.values())[0]
print('pad shape bounds', tuple(round(v, 3) for v in pad.bounds), 'area', round(pad.area, 4))
for m in MODEL:
    if m['net'] != 'ADC_B': continue
    for L, sh in m['shapes'].items():
        if sh.intersects(pad):
            print('INTERSECTS pad:', 'via' if m['via'] else 'trk', L, tuple(round(v, 3) for v in sh.bounds))
