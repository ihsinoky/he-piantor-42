"""Mouth-view handedness: for each FH12 connector, compute pad-1 side (LEFT/RIGHT)
as seen by a viewer at the mouth looking in, head pointing away from the board's
component side (up_view = toward the board surface in the visual field).
Frame: forward=-m (m = pad centroid -> MP centroid), up = -f (f = mounting-face
outward normal: F.Cu +Z, B.Cu -Z), right = forward x up. Pad1 side = sign of
(pad1-centre).right."""
import sys
import pcbnew as p

def analyse(path, ref):
    b = p.LoadBoard(path)
    for fp in b.GetFootprints():
        if fp.GetReference() != ref:
            continue
        sig = [(int(pad.GetNumber()), pad.GetPosition()) for pad in fp.Pads() if pad.GetNumber().isdigit()]
        mps = [pad.GetPosition() for pad in fp.Pads() if not pad.GetNumber().isdigit()]
        sig.sort()
        cx = sum(q.x for _, q in sig)/len(sig); cy = sum(q.y for _, q in sig)/len(sig)
        mx = sum(q.x for q in mps)/len(mps); my = sum(q.y for q in mps)/len(mps)
        import math
        mv = (mx-cx, my-cy); L = math.hypot(*mv); m = (mv[0]/L, mv[1]/L)
        f = (0, 0, 1) if int(fp.GetLayer()) == 0 else (0, 0, -1)
        fwd = (-m[0], -m[1], 0); up = (0, 0, -f[2])
        right = (fwd[1]*up[2]-fwd[2]*up[1], fwd[2]*up[0]-fwd[0]*up[2], fwd[0]*up[1]-fwd[1]*up[0])
        p1 = sig[0][1]
        off = ((p1.x-cx)/1e6, (p1.y-cy)/1e6, 0)
        d = off[0]*right[0] + off[1]*right[1]
        print(f"{ref} layer={int(fp.GetLayer())} m=({m[0]:.3f},{m[1]:.3f}) pad1 {'RIGHT' if d > 0 else 'LEFT'} ({d:+.2f})")
        return
    print(ref, 'not found in', path)

analyse(sys.argv[1], sys.argv[2])
