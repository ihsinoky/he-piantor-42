"""Stage-2 probe for the hinge round: measure, from the built solids,
the facts the hinge/latch design turns on. Run with the cad venv."""
import json
import build123d as bd

RT = "."
ASM = "./asm3d"
CAPS = json.load(open(RT + "/caps.json"))


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


shelf = load("north-shelf")
plate_r = load("plate-right")
tray_r = load("tray-right")

print("== plateau south edge (shelf solid, Z 11..22) ==")
for xc in (20.0, 40.0, 60.0, 100.0, 140.0):
    for sgn in (+1, -1):
        xa, xb = (xc - 0.5, xc + 0.5) if sgn > 0 else (-xc - 0.5, -xc + 0.5)
        cells = shelf.intersect(box(xa, xb, -70, 30, 11.0, 22.5))
        cells = [c for c in (cells if isinstance(cells, (list, bd.ShapeList))
                             else [cells]) if c is not None and c.volume > 1e-6]
        if cells:
            ymax = max(c.bounding_box().max.Y for c in cells)
            print(f"  X {sgn*xc:+.0f}: shelf south edge Y = {ymax:.3f}")
        else:
            print(f"  X {sgn*xc:+.0f}: no shelf material Z11..22")

print("== lid south edge (centre, |X|<=30) ==")
cells = shelf.intersect(box(-30, 30, -70, 30, 15.0, 22.5))
cells = [c for c in (cells if isinstance(cells, (list, bd.ShapeList))
                     else [cells]) if c is not None and c.volume > 1e-6]
print("  lid (Z>=15) south edge Y =",
      max(c.bounding_box().max.Y for c in cells))

print("== caps at |X| < 32 ==")
n = 0
for side in ("left", "right"):
    for poly in CAPS[side]["cap_polys"]:
        xs = [p[0] for p in poly]
        if min(xs) < 32 and max(xs) > -32:
            n += 1
            print("  cap poly X", min(xs), max(xs),
                  "Y", min(p[1] for p in poly), max(p[1] for p in poly))
print("  count:", n)

print("== plate-right north edge near latch zone X 74..90 ==")
for xc in (76.0, 80.0, 85.0, 89.0):
    cells = plate_r.intersect(box(xc - 0.5, xc + 0.5, -70, 90, 0, 12))
    cells = [c for c in (cells if isinstance(cells, (list, bd.ShapeList))
                         else [cells]) if c is not None and c.volume > 1e-6]
    if cells:
        print(f"  X {xc:.0f}: plate north edge Y =",
              min(c.bounding_box().min.Y for c in cells))
    else:
        print(f"  X {xc:.0f}: no plate")

print("== tray-right top at latch zone (85,-60.37) ==")
cells = tray_r.intersect(box(74, 90, -64, -56, 10.85, 11.0))
cells = [c for c in (cells if isinstance(cells, (list, bd.ShapeList))
                     else [cells]) if c is not None and c.volume > 1e-6]
print("  tray material just below Z10.90 in X74..90,Y-64..-56:",
      sum(c.volume for c in cells))
