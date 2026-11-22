"""Seam diagnosis v2: thin-slab run lists at stations (fast)."""
import build123d as bd

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


def subs(s, slab):
    r = s.intersect(slab)
    if r is None:
        return []
    items = r if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and c.volume > 1e-7]


plate = load("plate-right")
tray = load("tray-right")
shell = load("shell-central")

for y in (4.0, 12.0, 20.0, 24.0, 28.0, 32.0, 36.0, 44.0, 52.0,
          60.0, 68.0):
    slab = box(10.0, 58.0, y - 0.1, y + 0.1, 9.90, 10.95)
    runs = []
    for nm, s in (("plate", plate), ("tray", tray), ("shell", shell)):
        for c in subs(s, slab):
            bb = c.bounding_box()
            runs.append((round(bb.min.X, 2), round(bb.max.X, 2), nm))
    runs.sort()
    txt = " | ".join(f"{a}..{b} {n}" for a, b, n in runs)
    print(f"Y={y:5.1f}: {txt}", flush=True)
print("DONE")
