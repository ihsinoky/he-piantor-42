import build123d as bd, json
import numpy as np
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
def load(i): return bd.import_brep(f"{G17}/{i}.brep")
def solids(s):
    if s is None: return []
    try: return s.solids()
    except AttributeError: return list(s)
def vol(s): return sum(x.volume for x in solids(s))
def bboxs(s):
    out = []
    for x in solids(s):
        bb = x.bounding_box()
        out.append("X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.2f,%.2f]" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z, bb.max.Z))
    return out
OLD = [(117.8562,103.1958),(119.8213,103.1964),(132.9488,115.4381),(128.9362,122.3869),
       (135.8927,134.4359),(133.8927,137.9),(66.1073,137.9),(64.1073,134.4359),
       (71.0638,122.3869),(67.0512,115.4381),(80.1787,103.1964),(82.1438,103.1958),
       (98.0,75.7321),(102.0,75.7321)]
def new_outline(d, h):
    k = 0.577350269
    # shifted NE diagonal line: point (102+0.866d, 75.7321-0.5d), dir (0.5,0.866)
    # tab edge at Y = 75.7321-h; corner = line at that Y
    tNE = ((75.7321 - h) - (75.7321 - 0.5*d)) / 0.8660254
    cNE = (102 + 0.8660254*d + 0.5*tNE, 75.7321 - h)
    tNW = ((75.7321 - h) - (75.7321 - 0.5*d)) / 0.8660254
    cNW = (98 - 0.8660254*d - 0.5*tNW, 75.7321 - h)
    def inter(p1, d1, p2, d2):
        A = np.array([[d1[0], -d2[0]],[d1[1], -d2[1]]], float)
        t, s = np.linalg.solve(A, np.array([p2[0]-p1[0], p2[1]-p1[1]]))
        return (p1[0] + d1[0]*t, p1[1] + d1[1]*t)
    pNE = inter(cNE, (0.5, 0.8660254), (119.8213,103.1964), (0.73159,0.68177))
    pNW = inter(cNW, (-0.5, 0.8660254), (80.1787,103.1964), (-0.73159,0.68177))
    return [pNE,(132.9488,115.4381),(128.9362,122.3869),(135.8927,134.4359),(133.8927,137.9),
            (66.1073,137.9),(64.1073,134.4359),(71.0638,122.3869),(67.0512,115.4381),
            pNW, cNW, cNE]
def poly_solid(pts, z0, z1):
    with bd.BuildPart() as bp:
        with bd.BuildSketch():
            with bd.BuildLine():
                bd.Polyline(*[(x-100.0, y-70.0) for (x,y) in pts], close=True)
            bd.make_face()
        bd.extrude(amount=z1-z0)
    return bp.part.moved(bd.Location((0,0,z0)))
def strip(d, h, z0=7.35, z1=8.55):
    return poly_solid(new_outline(d,h), z0, z1).cut(poly_solid(OLD, z0, z1))
B = {i: load(i) for i in (3,4,131,221,123,207,121,205)}
print("== localize tray hit, uniform h=d=2")
st = strip(2.0, 2.0)
for i in (131,221):
    r = st.intersect(B[i]); print(i, idx[i]["name"], round(vol(r),2), bboxs(r))
print("== wing onset scan (h=d)")
for d in (2.5, 3.0, 3.5):
    st = strip(d, d)
    for i in (3,4):
        r = st.intersect(B[i])
        if vol(r) > 0.01: print(f"d={d}", i, idx[i]["name"], round(vol(r),2), bboxs(r))
print("== h=0 variant: wing + tray + screws")
for d in (4.0, 6.0, 8.0, 10.0):
    st = strip(d, 0.0)
    hits = []
    for i in (3,4,131,221,123,207):
        v = vol(st.intersect(B[i]))
        if v > 0.01: hits.append((idx[i]["name"], round(v,2)))
    print(f"h=0 d={d}:", hits)
    if d == 6.0:
        for i in (3,4):
            r = st.intersect(B[i])
            if vol(r) > 0.01: print("   wing bbox:", bboxs(r))
