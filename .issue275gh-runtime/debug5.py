import sys, math
exec(open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/debug4.py').read().split("solids = {}")[0])

def common_vol(a, b):
    c = a.intersect(b)
    if c is None:
        return 0.0
    try:
        return float(c.volume)
    except AttributeError:
        return sum(float(s.volume) for s in c)

solids = {}
for k in (1, 2, 5, 14):
    s, path = tube([list(p) for p in wire_pts('R', k)], 0.5)
    solids[k] = s
for pair in ((1, 2), (1, 5), (1, 14), (2, 5)):
    a, b = solids[pair[0]], solids[pair[1]]
    print(f'R{pair[0]}-R{pair[1]}: common_vol={common_vol(a, b):.4f}')
# where do R1/R2 come closest? sample centreline segment-pair distances
import itertools
def seg_seg_min(p1, p2, p3, p4):
    # coarse sampling
    best = 1e9
    for t in [i / 20 for i in range(21)]:
        a = [p1[i] + t * (p2[i] - p1[i]) for i in range(3)]
        for u in [j / 20 for j in range(21)]:
            b = [p3[i] + u * (p4[i] - p3[i]) for i in range(3)]
            d = math.dist(a, b)
            if d < best: best = d
    return best
A = wire_pts('R', 1); Bp = wire_pts('R', 2)
for m in range(5):
    for n in range(5):
        d = seg_seg_min(A[m], A[m + 1], Bp[n], Bp[n + 1])
        print(f'centreline seg {m}-{n}: min {d:.3f}')
