import sys
sys.argv = ['west_router.py']
src = open('.issue292-runtime/west_router.py').read().split('ok = True')[0]
exec(compile(src, 'west_router.py', 'exec'))
for (ref, num) in (('J2','6'), ('J2','5'), ('J2','7')):
    for fp in b.GetFootprints():
        if fp.GetReference() != ref: continue
        for pad in fp.Pads():
            if pad.GetNumber() != num: continue
            sh = pad.GetEffectiveShape()
            pts = []
            for seg in sh.GetPoints() if hasattr(sh, 'GetPoints') else []:
                pts.append(seg)
            bb = sh.BBox()
            print(ref, num, pad.GetNetname(), 'bbox', f"{bb.GetLeft()/1e6:.3f},{bb.GetTop()/1e6:.3f} - {bb.GetRight()/1e6:.3f},{bb.GetBottom()/1e6:.3f}")
