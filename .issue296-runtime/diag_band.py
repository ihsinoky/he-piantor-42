"""Finger working band restricted to inboard of the bay walls (|X|<=30.25),
plus per-part attribution of the outboard intruder."""
import build123d as bd
import os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def pieces(r):
    if r is None:
        return []
    xs = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [x for x in xs if hasattr(x, "volume") and x.volume > 1e-6]

def inter(a, b):
    try:
        return pieces(a.intersect(b))
    except Exception:
        return []

names = ["tray-left", "tray-right", "centre-infill", "shell-central",
         "strip-left", "strip-right", "plate-left", "plate-right"]
parts = {n: part(n) for n in names}
case_nc = parts[names[0]]
for n in names[1:]:
    case_nc = case_nc.fuse(parts[n])

for nm, zb in (("east inboard", box(22.50, 30.25, -59.62, -9.12, 7.40, 9.40)),
               ("west inboard", box(-30.25, -22.50, -59.62, -9.12, 7.40, 9.40))):
    tot = sum(p.volume for p in inter(case_nc, zb))
    print(f"{nm}: {tot:.3f} mm3")

band_e = box(22.50, 32.25, -59.62, -9.12, 7.40, 9.40)
for n in names:
    tot = sum(p.volume for p in inter(parts[n], band_e))
    if tot > 0.001:
        print(f"east band intruder part: {n} {tot:.3f} mm3")
