import json
import numpy as np
from shapely.geometry import Polygon
w = json.load(open("/home/hatch/workspace/projects/he-piantor-wmain2/.issue292-runtime/wing17R.json"))
ch = max(w["chains"], key=len)
f = np.load("/home/hatch/workspace/projects/he-piantor-wmain2/.issue292-runtime/wing-fit.npz")
W = (f["R"] @ np.array(ch).T).T + f["t"] + np.array([100.0, 70.0])
wingR = Polygon(W)
wingL = Polygon([(-x, y) for (x, y) in W])  # mirror about X=100 -> in board frame mirror about x=100: (200-x, y)
wingL = Polygon([(200.0 - x, y) for (x, y) in W])
OLDd = [(117.8562,103.1958),(119.8213,103.1964),(132.9488,115.4381),(128.9362,122.3869),
       (135.8927,134.4359),(133.8927,137.9),(66.1073,137.9),(64.1073,134.4359),
       (71.0638,122.3869),(67.0512,115.4381),(80.1787,103.1964),(82.1438,103.1958),
       (98.0,75.7321),(102.0,75.7321)]
OLD = Polygon(OLDd)
def new_outline(d, h):
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
            pNW, cNW, cNE], cNE, cNW
for (d, h) in [(1.0,2.0),(1.0,2.7),(1.0,3.5),(1.0,4.5),(0.5,2.7)]:
    pts, cNE, cNW = new_outline(d, h)
    newp = Polygon(pts)
    strip = newp.difference(OLD)
    print(f"d={d} h={h}: tab width at new edge = {cNE[0]-cNW[0]:.2f}mm, strip area = {strip.area:.1f}mm2, "
          f"strip∩WingR = {strip.intersection(wingR).area:.2f}, strip∩WingL = {strip.intersection(wingL).area:.2f}, "
          f"strip->WingR dist = {strip.distance(wingR):.2f}, strip->WingL dist = {strip.distance(wingL):.2f}")
