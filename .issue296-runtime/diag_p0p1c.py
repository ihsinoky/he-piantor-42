"""Issue #296 P0/P1 — does the shelf overhang the tray plan outline
at the end columns? Grid-probe: at each (X, Y) near the ends, a
point is 'shelf' if the shelf occupies it at Z 15 (shelf-only
height) and 'tray' if the tray occupies the vertical column at
any Z in -2.65..10.95. Report shelf points with no tray below."""
import build123d as bd
import os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def inter_vol(a, b):
    try:
        r = a.intersect(b)
    except Exception:
        return 0.0
    if r is None:
        return 0.0
    if isinstance(r, (list, bd.ShapeList)):
        return sum(x.volume for x in r if hasattr(x, "volume"))
    return r.volume

shelf = part("north-shelf")
trays = part("tray-left").fuse(part("tray-right")).fuse(part("centre-infill"))

bad = []
for sgn in (+1, -1):
    x = 116.0 * sgn
    while abs(x) < 155.5:
        y = -66.0
        while y < 2.0:
            probe_s = box(x - 0.2, x + 0.2, y - 0.2, y + 0.2, 14.9, 15.1)
            if inter_vol(shelf, probe_s) > 0.001:
                probe_t = box(x - 0.2, x + 0.2, y - 0.2, y + 0.2, -2.65, 10.95)
                if inter_vol(trays, probe_t) < 0.001:
                    bad.append((round(x, 1), round(y, 1)))
            y += 0.5
        x += 0.5 * sgn
print(f"overhang probe points (shelf present, no tray below): {len(bad)}")
for p in bad[:40]:
    print("   ", p)
