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

j = mv(load("underside-right-J_WING"), 9.5)
b = j.bounding_box()
print("J_WING body full bbox @d9.5: X[%.2f,%.2f] Y[%.2f,%.2f] Zcase[%.2f,%.2f] vol %.1f" % (b.min.X,b.max.X,b.min.Y,b.max.Y,b.min.Z-CZ,b.max.Z-CZ, j.volume))
u = mv(load("underside-right-U_MUX_C"), 9.5)
b = u.bounding_box()
print("U_MUX_C body full bbox @d9.5: X[%.2f,%.2f] Y[%.2f,%.2f] Zcase[%.2f,%.2f] vol %.1f" % (b.min.X,b.max.X,b.min.Y,b.max.Y,b.min.Z-CZ,b.max.Z-CZ, u.volume))

t = mv(load("tray-right"), 9.5)
strip = box(22.50, 30.25, -45.0, -8.7, -5, 35)
r = inter(t, strip)
print("--- tray-right solids in wall strip X22.50..30.25 Y-45..-8.7 ---")
if r:
    for s in r.solids():
        if s.volume < 0.5: continue
        bb = s.bounding_box()
        print("vol %8.2f X[%7.2f,%7.2f] Y[%7.2f,%7.2f] Zcase[%6.2f,%6.2f]" % (s.volume, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z-CZ, bb.max.Z-CZ))
# wall line only X 28.25..30.25
strip2 = box(28.25, 30.25, -45.0, -8.7, -5, 35)
r = inter(t, strip2)
print("--- tray-right in X28.25..30.25 (Stage B wall line) ---")
if r:
    for s in r.solids():
        if s.volume < 0.5: continue
        bb = s.bounding_box()
        print("vol %8.2f X[%7.2f,%7.2f] Y[%7.2f,%7.2f] Zcase[%6.2f,%6.2f]" % (s.volume, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z-CZ, bb.max.Z-CZ))
# floor band only in overlap column: Z below 0
col = box(22.50, 26.25, -45.0, -8.7, -5, 35)
r = inter(t, col)
print("--- tray-right solids in overlap col ---")
if r:
    for s in r.solids():
        if s.volume < 0.5: continue
        bb = s.bounding_box()
        print("vol %8.2f X[%7.2f,%7.2f] Y[%7.2f,%7.2f] Zcase[%6.2f,%6.2f]" % (s.volume, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z-CZ, bb.max.Z-CZ))
