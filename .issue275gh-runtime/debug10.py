import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('wires, lengths, centrelines')[0]
exec(head)
from geometry import tube

for side in 'RL':
    for k in range(1, 15):
        pts = wire_pts(side, k)
        try:
            solid, path = tube([list(p) for p in pts], 0.5)
        except Exception as e:
            print(f'{side}{k} FAILED: {type(e).__name__}')
            for i, p in enumerate(pts):
                print('  ', i, tuple(round(x, 2) for x in p))
            # consecutive distances
            ds = [round(math.dist(pts[i], pts[i + 1]), 2) for i in range(len(pts) - 1)]
            print('   seg lens:', ds)
