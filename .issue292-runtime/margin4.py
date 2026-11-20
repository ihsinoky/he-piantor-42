import build123d as bd, json
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
def load(i): return bd.import_brep(f"{G17}/{i}.brep")
w = load(4)
# slice at Z raw 8.0 -> section faces; get edges' vertices in region
sec = w.section(bd.Plane.XY.offset(8.0)) if hasattr(w, "section") else None
print(type(sec))
# fallback: intersect with thin slab and take top face outline points
slab = bd.Solid.make_box(60, 80, 0.2).moved(bd.Location((-5, -20, 7.9)))
r = w.intersect(slab)
ss = r.solids() if hasattr(r, "solids") else [r]
pts = set()
for s in ss:
    for v in s.vertices():
        pts.add((round(v.X,2), round(v.Y,2)))
pts = sorted(pts)
print("section vertices in region:", len(pts))
for p in pts: print(p)
