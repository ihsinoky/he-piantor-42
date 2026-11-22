"""Seam diagnosis: full run lists at selected rows + fine
distance probes between the plate inner edge and the band face
(right side), sampled along Y."""
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

for y in (28.0, 32.0):
    slab = box(-56.0, 56.0, y - 0.25, y + 0.25, 9.90, 10.95)
    print(f"--- row Y={y} ---")
    for nm, s in (("plate", plate), ("tray", tray), ("shell", shell)):
        for c in subs(s, slab):
            bb = c.bounding_box()
            print(f"  {nm:6s} X {bb.min.X:8.2f}..{bb.max.X:8.2f} "
                  f"top {bb.max.Z:.2f} vol {c.volume:9.1f}")

# fine seam probes: at each Y, walk X in 0.05 steps across the
# seam in the Z band 10.0..10.9; record plate start, band end.
print("--- seam walk (right) ---")
for y in (4, 12, 20, 24, 28, 32, 36, 44, 52, 60, 68):
    cells = {}
    x = 15.0
    while x < 58.0:
        cell = box(x, x + 0.05, y - 0.1, y + 0.1, 10.0, 10.90)
        cells[round(x, 2)] = (bool(subs(plate, cell)),
                              bool(subs(tray, cell)))
        x += 0.05
    xs = sorted(cells)
    plate_xs = [v for v in xs if cells[v][0]]
    tray_xs = [v for v in xs if cells[v][1]]
    if plate_xs and tray_xs:
        pe = min(plate_xs)
        west_tray = [v for v in tray_xs if v < pe]
        if west_tray:
            bf = max(west_tray) + 0.05
            print(f"  Y={y:2d}: plate edge {pe:7.2f}  band face "
                  f"{bf:7.2f}  seam {pe - bf:6.3f}")
        else:
            print(f"  Y={y:2d}: plate edge {pe:7.2f}  no tray west")
    else:
        print(f"  Y={y:2d}: plate={bool(plate_xs)} tray={bool(tray_xs)}")
print("DONE")
