"""Probe 2: tray-right top-Z map over the latch zone, and material
presence in the receiver band Z 9.25..10.90."""
import build123d as bd

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


tray = load("tray-right")
print("tray-right top Z (probe column 1x1, Z -2..12):")
print("      " + "".join(f"Y={y:>6.0f}" for y in (-63, -62, -61, -60, -59)))
for x in (75, 77.5, 80, 82, 85, 87.5, 89):
    row = []
    for y in (-63, -62, -61, -60, -59):
        cells = tray.intersect(box(x - 0.5, x + 0.5, y - 0.5, y + 0.5,
                                   -2.0, 12.0))
        cells = [c for c in (cells if isinstance(cells, (list, bd.ShapeList))
                             else [cells]) if c is not None and c.volume > 1e-6]
        row.append(max((c.bounding_box().max.Z for c in cells),
                       default=float("nan")))
    print(f"X={x:>5}: " + "".join(f"{v:7.2f}" for v in row))
