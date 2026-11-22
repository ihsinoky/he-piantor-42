"""X-Z material map of tray + shelf at the bay E/W ends, for Y
slices along the bay, to find a latch seat: a fixed sill/wall
top with shelf material above it, clear of the cells."""
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

for yc in (-58, -48, -38, -28, -18, -8):
    print(f"--- Y {yc:+d} (slab +-0.4) ---")
    for label, part in (("tray", tray), ("shelf", shelf)):
        x = 24.0
        cells = []
        while x < 34.0:
            r = solids(part.intersect(box(x, x + 1.0, yc - 0.4, yc + 0.4, -1, 23)))
            if r:
                spans = sorted({(round(c.bounding_box().min.Z, 2),
                                 round(c.bounding_box().max.Z, 2)) for c in r})
                cells.append(f"X{x:.0f}:{spans}")
            x += 1.0
        print(f"  {label}: " + " ".join(cells))
