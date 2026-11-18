import sys, math
P248 = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, P248 + '/sources/frontier')
sys.path.insert(0, P248)
import common  # sets canonical sys.path (caddeps, raise issue-232-final)
from geometry import tube
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

B = 6.75
Z_EXIT, Z_RUN = B - 1.60, 2.60
SITES = {
    'R': dict(centre=(24.255, 41.824), rowdir=(0.731, -0.682), outward=(0.682, -0.731), sgn=1),
    'L': dict(centre=(-24.255, 41.824), rowdir=(0.731, 0.682), outward=(-0.682, -0.731), sgn=-1),
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

def dist(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return float(d.Value()) if d.IsDone() else -1.0

solids = {}
for k in (1, 2, 5, 14):
    s, path = tube([list(p) for p in wire_pts('R', k)], 0.5)
    solids[k] = s
    expect = math.pi * 0.25 * float(path.length)
    print(f'R{k}: type={type(s).__name__} valid={s.is_valid} vol={float(s.volume):.2f} expect~{expect:.2f} len={float(path.length):.2f}')
print('extrema R1-R2 (expect ~0.05):', round(dist(solids[1], solids[2]), 3))
print('extrema R1-R5 (expect ~3.2):', round(dist(solids[1], solids[5]), 3))
print('extrema R1-R14 (expect ~12.65):', round(dist(solids[1], solids[14]), 3))
