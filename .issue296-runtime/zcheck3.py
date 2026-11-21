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
t = mv(load("tray-right"), 9.5)
for zlo, zhi in [(-0.65, 3.30), (3.30, 4.70), (4.70, 5.90), (5.90, 9.40)]:
    band = box(22.50, 26.25, -45.0, -8.7, zlo+CZ, zhi+CZ)
    r = inter(t, band)
    print("--- tray in overlap col, Zcase %.2f..%.2f ---" % (zlo, zhi))
    if r:
        for s in r.solids():
            if s.volume < 0.3: continue
            bb = s.bounding_box()
            print("vol %8.2f X[%7.2f,%7.2f] Y[%7.2f,%7.2f]" % (s.volume, bb.min.X, bb.max.X, bb.min.Y, bb.max.Y))
    else:
        print("none")
