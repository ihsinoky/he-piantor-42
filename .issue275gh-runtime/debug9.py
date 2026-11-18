import sys, math
src = open('/home/hatch/workspace/projects/he-piantor-ghcheck/.issue275gh-runtime/build_audit.py').read()
head = src.split('# ---------- audit ----------')[0]
# stop head before it builds all wires: cut at the wires loop
head = head.split('wires, lengths, centrelines')[0]
exec(head)
from geometry import tube

def sample_path(path, n=400):
    # discretize the path wire by arc length via vertices of a dense discretisation
    from OCP.BRepAdaptor import BRepAdaptor_Curve
    from OCP.GCPnts import GCPnts_QuasiUniformDeflection
    from OCP.BRepAdaptor import BRepAdaptor_CompCurve
    ad = BRepAdaptor_CompCurve(path.wrapped)
    d = GCPnts_QuasiUniformDeflection(ad, 0.05)
    pts = []
    for i in range(1, d.NbPoints() + 1):
        p = d.Value(i)
        pts.append((p.X(), p.Y(), p.Z()))
    return pts

res = {}
for name in ('R13', 'R14', 'R1', 'R2'):
    pts = wire_pts(name[0], int(name[1:]))
    solid, path = tube([list(p) for p in pts], 0.5)
    res[name] = sample_path(path)
    print(name, 'path samples:', len(res[name]))

def min_dist(A, B):
    best = (1e9, None, None)
    for a in A:
        for b in B:
            d = math.dist(a, b)
            if d < best[0]: best = (d, a, b)
    return best

for pair in (('R13', 'R14'), ('R1', 'R2')):
    d, a, b = min_dist(res[pair[0]], res[pair[1]])
    print(pair, 'path min dist:', round(d, 3), 'at', tuple(round(x, 1) for x in a), tuple(round(x, 1) for x in b))
