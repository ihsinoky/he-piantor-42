"""Localise the A-D interference items (bboxes) + g17 baselines."""
import build123d as bd
import json, os

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(__file__)
ZC = 2.65

def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def fuse_all(ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r

def inter(a, b):
    try:
        r = a.intersect(b)
    except Exception:
        return []
    if r is None:
        return []
    if isinstance(r, (list, bd.ShapeList)):
        return [x for x in r if hasattr(x, "volume") and x.volume > 0.001]
    return [r] if r.volume > 0.001 else []

def show(label, a, b):
    ss = inter(a, b)
    tot = sum(s.volume for s in ss)
    print(f"{label}: total {tot:.2f} mm3 in {len(ss)} solid(s)")
    for s in ss:
        bb = s.bounding_box()
        print(f"   vol {s.volume:9.2f}  X {bb.min.X:8.2f}..{bb.max.X:8.2f}"
              f"  Y {bb.min.Y:8.2f}..{bb.max.Y:8.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}")

tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
shell, plate_r, cover = part("shell-central"), part("plate-right"), part("battery-cover")

segs = json.load(open(os.path.join(RT, "main-outline-asm.json")))
pts = [tuple(segs[0][0]), tuple(segs[0][1])]
rest = [tuple(map(tuple, s)) for s in segs[1:]]
while rest:
    for i, (a, b) in enumerate(rest):
        if a == pts[-1]:
            pts.append(b); rest.pop(i); break
        if b == pts[-1]:
            pts.append(a); rest.pop(i); break
    else:
        break
edges = [bd.Edge.make_line(bd.Vector(*pts[i], 0), bd.Vector(*pts[i + 1], 0))
         for i in range(len(pts) - 1)]
main = bd.extrude(bd.Face(bd.Wire(edges)), 1.2).moved(bd.Location((0, 0, 4.70)))

wing_r = g17("wing_right", 9.5)
und_r = fuse_all([g17(e["name"], 9.5) for e in idx
                  if e["name"].startswith("underside-right")])
wings_r = fuse_all([wing_r, und_r])
fly = None
for e in idx:
    if e["name"].startswith("Fly-official"):
        s = g17(e["name"])
        fly = s if fly is None else fly.fuse(s)
fly = fly.moved(bd.Location((38, -1.80, 0)))

show("tray-right x Main(D-063)", tray_r, main)
show("infill x Main(D-063)", infill, main)
show("tray-right x wings-right", tray_r, wings_r)
show("cover x Fly", cover, fly)
show("plate-right x Fly", plate_r, fly)
show("tray-right x plate-right", tray_r, plate_r)

print("\n-- g17 baselines (delta=0, original poses) --")
g_tray_r, g_tray_l = g17("tray-right"), g17("tray-left")
g_wing_r = g17("wing_right")
g_und_r = fuse_all([g17(e["name"]) for e in idx
                    if e["name"].startswith("underside-right")])
g_plate_r = g17("plate-right")
g_main = g17("main")
show("g17 tray-right x wing-right+und", g_tray_r, fuse_all([g_wing_r, g_und_r]))
show("g17 tray-right x plate-right", g_tray_r, g_plate_r)
show("g17 tray-right x main(g17)", g_tray_r, g_main)
show("g17 tray-left x main(g17)", g_tray_l, g_main)
