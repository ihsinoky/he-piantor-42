import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('wires, lengths, centrelines')[0]
exec(head)
from geometry import tube

solids = {}
for side, k in (('L', 1), ('L', 2), ('R', 13), ('R', 14)):
    pts = wire_pts(side, k)
    solids[f'{side}{k}'] = tube([list(p) for p in pts], 0.5)[0]

for a, b in (('L1', 'L2'), ('R13', 'R14')):
    c = solids[a].intersect(solids[b])
    pieces = [] if c is None else (list(c) if hasattr(c, '__iter__') else [c])
    out = []
    for p in pieces:
        bb = p.bounding_box()
        out.append((round(float(p.volume), 4),
                    tuple(round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z))))
    print((a, b), out)
for name in ('L1', 'L2'):
    pts = wire_pts('L', int(name[1:]))
    print(name, [(round(p[0], 1), round(p[1], 1), round(p[2], 2)) for p in pts])
