import build123d as bd, json
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
byname = {e["name"]: i for i, e in enumerate(idx)}
def load(name): return bd.import_brep(f"{G17}/{byname[name]}.brep")
def mv(s, dx): return s.moved(bd.Location((dx, 0, 0)))
CZ = 2.65
def box(x0,x1,y0,y1,z0,z1):
    return bd.Solid.make_box(x1-x0, y1-y0, z1-z0).moved(bd.Location((x0,y0,z0)))
def inter(a,b):
    try: return a.intersect(b)
    except Exception: return None
def report(tag, solid):
    if solid is None: print(tag, "no intersect"); return
    ss = [s for s in solid.solids() if s.volume > 0.01]
    if not ss: print(tag, "vol~0"); return
    for s in ss:
        b = s.bounding_box()
        print("%s vol %8.2f  X[%7.2f,%7.2f] Y[%7.2f,%7.2f] Zcase[%6.2f,%6.2f]" %
              (tag, s.volume, b.min.X, b.max.X, b.min.Y, b.max.Y, b.min.Z-CZ, b.max.Z-CZ))

w = mv(load("wing_right"), 9.5)
b = w.bounding_box()
print("wing_right @d9.5 full bbox: X[%.2f,%.2f] Y[%.2f,%.2f] Zcase[%.2f,%.2f]" % (b.min.X, b.max.X, b.min.Y, b.max.Y, b.min.Z-CZ, b.max.Z-CZ))
col = box(22.50, 26.25, -45.0, -8.7, -5, 35)
report("WING in overlap col", inter(w, col))
colw = box(20.0, 30.25, -45.0, -8.7, -5, 35)
report("WING in wider col", inter(w, colw))
print("--- underside bodies (right), shifted, in overlap col ---")
for name in byname:
    if name.startswith("underside-right-"):
        s = mv(load(name), 9.5)
        r = inter(s, col)
        bb = s.bounding_box()
        tag = name.replace("underside-right-","")
        if r is not None and any(x.volume > 0.01 for x in r.solids()):
            report("UNDER "+tag, r)
        else:
            print("UNDER %-10s outside col (bbox X[%.1f,%.1f] Y[%.1f,%.1f] Zcase[%.2f,%.2f])" % (tag, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z-CZ, bb.max.Z-CZ))
print("--- tray-right in wall strip / overlap col ---")
t = mv(load("tray-right"), 9.5)
report("TRAY in overlap col", inter(t, col))
strip = box(22.50, 30.25, -45.0, -8.7, -5, 35)
report("TRAY in wall strip", inter(t, strip))
print("--- plate-right in overlap col ---")
p = mv(load("plate-right"), 9.5)
report("PLATE in overlap col", inter(p, col))
