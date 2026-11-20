import json
import numpy as np
from shapely.geometry import Polygon, Point, LineString
w = json.load(open("/home/hatch/workspace/projects/he-piantor-wmain2/.issue292-runtime/wing17R.json"))
ch = max(w["chains"], key=len)
f = np.load("/home/hatch/workspace/projects/he-piantor-wmain2/.issue292-runtime/wing-fit.npz")
R, t = f["R"], f["t"]
W = (R @ np.array(ch).T).T + t   # Wing outline in g17
wing = Polygon(W)
OLDd = [(117.8562,103.1958),(119.8213,103.1964),(132.9488,115.4381),(128.9362,122.3869),
       (135.8927,134.4359),(133.8927,137.9),(66.1073,137.9),(64.1073,134.4359),
       (71.0638,122.3869),(67.0512,115.4381),(80.1787,103.1964),(82.1438,103.1958),
       (98.0,75.7321),(102.0,75.7321)]
OLD = Polygon([(x-100.0, y-70.0) for (x,y) in OLDd])
print("Wing placed bbox X[%.1f,%.1f] Y[%.1f,%.1f]" % (min(W[:,0]), max(W[:,0]), min(W[:,1]), max(W[:,1])))
print("min distance OLD Main <-> WingR:", round(OLD.distance(wing), 3))
# distance profile along NE diagonal (board (102,75.73)->(117.86,103.20)) in g17
p0 = np.array([2.0, 5.7321]); p1 = np.array([17.8562, 33.1958])
for s in np.linspace(0, 1, 8):
    p = p0 + s*(p1-p0)
    print(f"  diag s={s:.2f} g17 ({p[0]:.1f},{p[1]:.1f}): dist to Wing = {Point(p).distance(wing):.2f}")
# max uniform offset d with residual >= 1.0 to Wing (NE side governs; check full polygon)
def new_outline(d, h):
    k = 0.577350269
    tNE = ((75.7321 - h) - (75.7321 - 0.5*d)) / 0.8660254
    cNE = (102 + 0.8660254*d + 0.5*tNE, 75.7321 - h)
    cNW = (98 - 0.8660254*d - 0.5*tNE, 75.7321 - h)
    def inter(p1, d1, p2, d2):
        A = np.array([[d1[0], -d2[0]],[d1[1], -d2[1]]], float)
        tt, ss = np.linalg.solve(A, np.array([p2[0]-p1[0], p2[1]-p1[1]]))
        return (p1[0] + d1[0]*tt, p1[1] + d1[1]*tt)
    pNE = inter(cNE, (0.5, 0.8660254), (119.8213,103.1964), (0.73159,0.68177))
    pNW = inter(cNW, (-0.5, 0.8660254), (80.1787,103.1964), (-0.73159,0.68177))
    return [pNE,(132.9488,115.4381),(128.9362,122.3869),(135.8927,134.4359),(133.8927,137.9),
            (66.1073,137.9),(64.1073,134.4359),(71.0638,122.3869),(67.0512,115.4381),
            pNW, cNW, cNE]
for (d, h) in [(4,4),(5,5),(6,6),(6,3),(7,3),(8,4),(8,8),(10,5)]:
    poly = Polygon([(x-100.0, y-70.0) for (x,y) in new_outline(d,h)])
    print(f"d={d} h={h}: dist new outline -> WingR = {poly.distance(wing):.2f}")

print("=== contact analysis")
inter = OLD.intersection(wing)
print("OLD x Wing intersection:", inter.geom_type, "area", round(inter.area,3))
if inter.area > 0:
    print("  bounds:", [round(v,1) for v in inter.bounds])
else:
    # touching: find closest points
    from shapely.ops import nearest_points
    a, b = nearest_points(OLD, wing)
    print("  nearest:", (round(a.x,2), round(a.y,2)), (round(b.x,2), round(b.y,2)))
for (d, h) in [(2,2),(3,3),(4,4),(5,3),(6,3),(6,6)]:
    newp = Polygon([(x-100.0, y-70.0) for (x,y) in new_outline(d,h)])
    strip = newp.difference(OLD)
    print(f"d={d} h={h}: strip->Wing dist = {strip.distance(wing):.3f}, new∩Wing area = {newp.intersection(wing).area:.3f}")
