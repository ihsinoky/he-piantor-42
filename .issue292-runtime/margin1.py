import build123d as bd, json, math, sys
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
def load(i): return bd.import_brep(f"{G17}/{i}.brep")
def vol(s):
    if s is None: return 0.0
    try: return s.volume
    except AttributeError:
        return sum(x.volume for x in s.solids())

# old outline (board coords), chained polygon from dump
OLD = [(117.8562,103.1958),(119.8213,103.1964),(132.9488,115.4381),(128.9362,122.3869),
       (135.8927,134.4359),(133.8927,137.9),(66.1073,137.9),(64.1073,134.4359),
       (71.0638,122.3869),(67.0512,115.4381),(80.1787,103.1964),(82.1438,103.1958),
       (98.0,75.7321),(102.0,75.7321)]
def new_outline(d):
    # uniform parallel offset of north boundary by d (normal distance)
    k = 0.577350269  # tan(30)
    cNE = (102 + k*d, 75.7321 - d); cNW = (98 - k*d, 75.7321 - d)
    # NE diag dir (0.5, 0.866025); SE diag through tip (119.8213,103.1964) dir (0.73159,0.68177)
    def inter(p1, d1, p2, d2):
        import numpy as np
        A = np.array([[d1[0], -d2[0]],[d1[1], -d2[1]]], float)
        t, s = np.linalg.solve(A, np.array([p2[0]-p1[0], p2[1]-p1[1]]))
        return (p1[0] + d1[0]*t, p1[1] + d1[1]*t)
    pNE = inter(cNE, (0.5, 0.8660254), (119.8213,103.1964), (0.73159,0.68177))
    pNW = inter(cNW, (-0.5, 0.8660254), (80.1787,103.1964), (-0.73159,0.68177))
    return [pNE,(132.9488,115.4381),(128.9362,122.3869),(135.8927,134.4359),(133.8927,137.9),
            (66.1073,137.9),(64.1073,134.4359),(71.0638,122.3869),(67.0512,115.4381),
            pNW, cNW, cNE]
def poly_solid(pts, z0, z1):
    # board coords -> g17 (x-100, y-70); extrude raw Z
    with bd.BuildPart() as bp:
        with bd.BuildSketch():
            with bd.BuildLine():
                pp = [(x-100.0, y-70.0) for (x,y) in pts]
                bd.Polyline(*pp, close=True)
            bd.make_face()
        bd.extrude(amount=z1-z0)
    s = bp.part.moved(bd.Location((0,0,z0)))
    return s
def strip_solid(d, z0=7.35, z1=8.55):
    new = poly_solid(new_outline(d), z0, z1)
    old = poly_solid(OLD, z0, z1)
    return new.cut(old)

# candidate bodies: bbox overlaps strip region g17 X[-45,45], Y[-20,45]
cand = []
for i,e in enumerate(idx):
    (x0,y0,z0),(x1,y1,z1) = e["bounds"]
    if x0 <= 45 and x1 >= -45 and y0 <= 45 and y1 >= -20:
        cand.append(i)
EXCLUDE = {2} | set(range(275,330))  # main ghost + old-Main study ghosts
cand = [i for i in cand if i not in EXCLUDE]
print("candidates:", [(i, idx[i]["name"]) for i in cand])
bodies = {i: load(i) for i in cand}
for d in (2.0, 4.0, 6.0, 8.0):
    st = strip_solid(d)
    print(f"--- d={d} strip area vol={st.volume:.1f} mm3")
    for i in cand:
        v = vol(st.intersect(bodies[i]))
        if v > 0.01:
            print(f"    HIT {i} {idx[i]['name']}: {v:.2f} mm3")
print("done")
