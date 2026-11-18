import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('wires, lengths, centrelines')[0]
exec(head)
from geometry import rounded

for side, k in (('R', 4), ('R', 5), ('L', 11)):
    pts = wire_pts(side, k)
    path = rounded([list(p) for p in pts], 5)
    lens = [round(float(e.length), 3) for e in path.edges()]
    print(f'{side}{k}: edges={len(lens)} min={min(lens)} lens={lens}')
