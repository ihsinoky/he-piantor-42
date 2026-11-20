import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for fp in b.GetFootprints():
    if fp.GetReference() != 'U1': continue
    for pad in fp.Pads():
        pos = pad.GetPosition()
        sz = pad.GetSize()
        print(pad.GetNumber(), round(pos.x/1e6, 2), round(pos.y/1e6, 2), round(sz.x/1e6, 2), round(sz.y/1e6, 2), pad.GetNetname())
