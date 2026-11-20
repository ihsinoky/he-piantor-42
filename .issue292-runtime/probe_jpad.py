import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm2(v): return v / 1e6
for fp in b.GetFootprints():
    if fp.GetReference() != 'JPAD': continue
    for pad in fp.Pads():
        pos = pad.GetPosition()
        print('JPAD', pad.GetNumber(), pad.GetNetname(), f"{mm2(pos.x):.2f},{mm2(pos.y):.2f}")
