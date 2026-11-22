"""Y-Z material map of the tray union at given X slices, plus the
same map at the ORIGINAL latch site (X +82) for comparison, and
the shelf underside profile at the same slices."""
import build123d as bd

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


def solids(r):
    if r is None:
        return []
    if isinstance(r, (list, bd.ShapeList)):
        return [c for c in r if c is not None and c.volume > 1e-9]
    return [r] if r.volume > 1e-9 else []


trays = [load("tray-left"), load("tray-right"), load("centre-infill")]
tray = trays[0]
for t in trays[1:]:
    tray = tray.fuse(t)
shelf = load("north-shelf")

for xc in (82, 20, -20):
    print(f"--- X {xc:+d} (slab +-0.4) ---")
    y = -65.0
    while y < -54.0:
        r = solids(tray.intersect(box(xc - 0.4, xc + 0.4, y, y + 0.5, -1, 23)))
        if r:
            spans = sorted((round(c.bounding_box().min.Z, 2),
                            round(c.bounding_box().max.Z, 2)) for c in r)
            print(f"  tray Y {y:6.1f}..{y+0.5:6.1f}: {spans}")
        y += 0.5
    y = -65.0
    while y < -54.0:
        r = solids(shelf.intersect(box(xc - 0.4, xc + 0.4, y, y + 0.5, -1, 23)))
        if r:
            spans = sorted((round(c.bounding_box().min.Z, 2),
                            round(c.bounding_box().max.Z, 2)) for c in r)
            print(f"  shelf Y {y:6.1f}..{y+0.5:6.1f}: {spans}")
        y += 0.5
