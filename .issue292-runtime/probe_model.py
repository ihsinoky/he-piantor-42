import sys
sys.argv = ['tree_router.py']
src = open('.issue292-runtime/tree_router.py').read().split('ok = True')[0]
exec(compile(src, 'tree_router.py', 'exec'))
ms = [m for m in MODEL if m['net'] == 'ADC_B']
print('MODEL ADC_B entries:', len(ms))
tb = 0
for t in b.GetTracks():
    if t.GetNetname() == 'ADC_B': tb += 1
print('board ADC_B tracks+vias:', tb)
for m in ms[:5]:
    print(' via' if m['via'] else ' trk', {L: tuple(round(v, 1) for v in sh.bounds) for L, sh in m['shapes'].items()})
