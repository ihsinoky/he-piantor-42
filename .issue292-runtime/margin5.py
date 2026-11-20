import build123d as bd, json
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
def load(i): return bd.import_brep(f"{G17}/{i}.brep")
def vol(s):
    if s is None: return 0.0
    try: return s.volume
    except AttributeError: return sum(x.volume for x in s.solids())
m = load(2); wr = load(4); wl = load(3)
print("main vol", round(m.volume,1), "wingR vol", round(wr.volume,1))
print("main x wingR:", round(vol(m.intersect(wr)),2))
print("main x wingL:", round(vol(m.intersect(wl)),2))
# where: bbox of intersection
r = m.intersect(wr)
ss = r.solids() if hasattr(r, "solids") else [r]
for s in ss:
    bb = s.bounding_box(); print("  solid X[%.1f,%.1f] Y[%.1f,%.1f] Z[%.2f,%.2f] vol %.1f" % (bb.min.X,bb.max.X,bb.min.Y,bb.max.Y,bb.min.Z,bb.max.Z,s.volume))
