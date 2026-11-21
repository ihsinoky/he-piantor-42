"""Scan Wing/plate presence in the bay wall bands, per Y (and S wall per X)."""
import build123d as bd
import json, os

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ZC = 2.65

def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def fuse_all(ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r

def solids(r):
    if r is None:
        return []
    if isinstance(r, (list, bd.ShapeList)):
        return [x for x in r if hasattr(x, "volume") and x.volume > 0.001]
    return [r] if r.volume > 0.001 else []

wing_r = g17("wing_right", 9.5)
und_names = [e["name"] for e in idx if e["name"].startswith("underside-right")]
unds = {n: g17(n, 9.5) for n in und_names}
plate_r = bd.import_brep(os.path.expanduser(
    "~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d/plate-right.brep"))

print("underside bodies (right):")
for n, s in unds.items():
    bb = s.bounding_box()
    print(f"  {n:28s} X {bb.min.X:7.2f}..{bb.max.X:7.2f} Y {bb.min.Y:7.2f}..{bb.max.Y:7.2f}"
          f" Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}")

print("\nE wall band X 28.25..30.25, per Y (1mm): board / underside-minZ / plate")
for yi in range(-64, 0):
    sl = box(28.25, 30.25, yi, yi + 1, -2.65, 22.0)
    b = solids(wing_r.intersect(sl))
    u = []
    for n, s in unds.items():
        ss = solids(s.intersect(sl))
        if ss:
            u.append(min(x.bounding_box().min.Z for x in ss))
    p = solids(plate_r.intersect(sl))
    if b or u or p:
        print(f"  Y {yi:4d}..{yi+1:4d}: board {'Y' if b else '-'}"
              f"  undMinZ {min(u) if u else None}  plate {'Y' if p else '-'}")

print("\nW wall band X -30.25..-28.25, per Y (1mm): board / underside-minZ / plate")
wing_l = g17("wing_left", -9.5)
unds_l = {n.replace("right", "left"): g17(n.replace("right", "left"), -9.5)
          for n in und_names}
plate_l = bd.import_brep(os.path.expanduser(
    "~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d/plate-left.brep"))
for yi in range(-64, 0):
    sl = box(-30.25, -28.25, yi, yi + 1, -2.65, 22.0)
    b = solids(wing_l.intersect(sl))
    u = []
    for n, s in unds_l.items():
        ss = solids(s.intersect(sl))
        if ss:
            u.append(min(x.bounding_box().min.Z for x in ss))
    p = solids(plate_l.intersect(sl))
    if b or u or p:
        print(f"  Y {yi:4d}..{yi+1:4d}: board {'Y' if b else '-'}"
              f"  undMinZ {min(u) if u else None}  plate {'Y' if p else '-'}")

print("\nS wall band Y -2.37..-0.37, per X (2mm): plate present?")
for xi in range(-32, 32, 2):
    sl = box(xi, xi + 2, -2.37, -0.37, -2.65, 22.0)
    p = solids(plate_r.intersect(sl)) + solids(plate_l.intersect(sl))
    if p:
        print(f"  X {xi:4d}..{xi+2:4d}: plate Y")
