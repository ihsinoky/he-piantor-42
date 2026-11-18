import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('# ---------- Main GH plug envelopes')[0]
exec(head)

for pitch in (17, 16):
    b16 = dict(FF.bodies_at(pitch, -0.60))
    for nm in ('underside-right-J_WING', 'underside-left-J_WING'):
        bb = b16[nm].bounding_box()
        print(pitch, nm, tuple(round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)))
