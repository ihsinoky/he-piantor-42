import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('# ---------- Main GH plug envelopes')[0]
exec(head)

for name, b in raw.items():
    if 'J_WING' in name or 'slab' in name.lower() or 'DRAWING' in name or 'wing' in name.lower():
        bb = b.bounding_box()
        print(name, tuple(round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)))
