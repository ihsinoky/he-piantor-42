import sys, math, json
P248 = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, P248 + '/sources/frontier')
sys.path.insert(0, P248)
import common  # noqa
import fitlibF as FF
from geometry import tube

B = 6.75
Z_EXIT, Z_RUN = B - 1.60, 2.60
SITES = {
    'R': dict(centre=(24.255, 41.824), rowdir=(0.731, -0.682), outward=(-0.682, -0.731), sgn=1),
    'L': dict(centre=(-24.255, 41.824), rowdir=(0.731, 0.682), outward=(0.682, -0.731), sgn=-1),
}

def wire_pts(side, k):
    st = SITES[side]
    sgn = st['sgn']
    u = (k - 7.5) * 1.25
    wx = sgn * 27 + (k - 7.5) * 1.25
    bx = sgn * 26 + (k - 7.5) * 1.05
    rp = (st['centre'][0] + st['rowdir'][0] * u, st['centre'][1] + st['rowdir'][1] * u)
    F = (rp[0] + st['outward'][0] * 13, rp[1] + st['outward'][1] * 13)
    M = (rp[0] + st['outward'][0] * 1.0, rp[1] + st['outward'][1] * 1.0)
    return [(wx, -34.5, Z_EXIT), (wx, -27.0, 4.30), (bx, -13.0, Z_RUN),
            (bx, 16.0, Z_RUN), (F[0], F[1], 4.30), (M[0], M[1], Z_EXIT)]

def common(a, b):
    c = a.intersect(b)
    if c is None: return None
    try: return c
    except Exception: return c

def vol(c):
    if c is None: return 0.0
    try: return float(c.volume)
    except AttributeError: return sum(float(s.volume) for s in c)

def bboxs(c):
    out = []
    try:
        items = [c]
        _ = c.volume
    except AttributeError:
        items = list(c)
    for s in items:
        b = s.bounding_box()
        out.append((round(b.min.X, 2), round(b.min.Y, 2), round(b.min.Z, 2),
                    round(b.max.X, 2), round(b.max.Y, 2), round(b.max.Z, 2), round(float(s.volume), 3)))
    return out

r1, _ = tube([list(p) for p in wire_pts('R', 1)], 0.5)
r2, _ = tube([list(p) for p in wire_pts('R', 2)], 0.5)
c = common(r1, r2)
print('R1-R2 common vol:', round(vol(c), 3), 'pieces:', bboxs(c))

# centreline segment-pair sampled min distances R1-R2
def seg_min(p1, p2, p3, p4):
    best = 1e9
    for i in range(41):
        t = i / 40
        a = [p1[j] + t * (p2[j] - p1[j]) for j in range(3)]
        for l in range(41):
            u = l / 40
            b = [p3[j] + u * (p4[j] - p3[j]) for j in range(3)]
            d = math.dist(a, b)
            if d < best: best = d
    return best
A, Bp = wire_pts('R', 1), wire_pts('R', 2)
for m in range(5):
    row = [round(seg_min(A[m], A[m + 1], Bp[n], Bp[n + 1]), 3) for n in range(5)]
    print(f'R1 seg{m} vs R2 segs:', row)

# L14 vs flipped C27 box
raw = dict(FF.bodies_at(17, -0.60))
for nm in ('Main-study-C27', 'Main-study-C26', 'Main-study-C28', 'Main-study-C2', 'Main-study-Y1', 'Main-study-C22'):
    if nm in raw:
        b = raw[nm].bounding_box()
        print(nm, 'normal-pose bbox:', (round(b.min.X, 2), round(b.min.Y, 2), round(b.min.Z, 2), round(b.max.X, 2), round(b.max.Y, 2), round(b.max.Z, 2)))
l14, _ = tube([list(p) for p in wire_pts('L', 14)], 0.5)
print('L14 pts:', [(round(p[0], 1), round(p[1], 1), p[2]) for p in wire_pts('L', 14)])
