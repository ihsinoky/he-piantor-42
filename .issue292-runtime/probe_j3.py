import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
def mm2(v): return v / 1e6
for fp in b.GetFootprints():
    if fp.GetReference() not in ('J3', 'J2'): continue
    for pad in fp.Pads():
        pos = pad.GetPosition()
        print(fp.GetReference(), pad.GetNumber(), pad.GetNetname(), f"{mm2(pos.x):.3f},{mm2(pos.y):.3f}")
