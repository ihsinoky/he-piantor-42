import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('wires, lengths, centrelines')[0]
exec(head)
from geometry import tube

for name, b in fixed.items():
    if 'joint-screw' in name:
        bb = b.bounding_box()
        print(name, tuple(round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)))
pts = wire_pts('R', 1)
print('R1 pts:', [(round(p[0], 1), round(p[1], 1)) for p in pts])
