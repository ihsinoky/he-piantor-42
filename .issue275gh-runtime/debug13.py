import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('wires, lengths, centrelines')[0]
exec(head)
from geometry import tube

for name in ('underside-right-U_HC1', 'underside-left-U_HC1'):
    bb = fixed[name].bounding_box()
    print(name, tuple(round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)))

for side, k, body in (('L', 1, 'underside-left-U_HC1'), ('R', 13, 'underside-right-U_HC1'),
                      ('R', 14, 'underside-right-U_HC1')):
    pts = wire_pts(side, k)
    solid, _ = tube([list(p) for p in pts], 0.5)
    c = solid.intersect(fixed[body])
    if c is None:
        print(side, k, 'no common')
        continue
    pieces = list(c) if hasattr(c, '__iter__') else [c]
    for p in pieces:
        bb = p.bounding_box()
        print(side, k, 'common vol', round(float(p.volume), 4),
              'bbox', tuple(round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)))
    print('  pts:', [(round(p[0], 1), round(p[1], 1), round(p[2], 2)) for p in pts[:4]])
