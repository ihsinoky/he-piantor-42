"""Underside probe: at candidate screw points, the shell's
material Z range in an r1.2 pin (Z 4..12): top, bottom, and
whether the column is continuous 10.90 -> bottom."""
import build123d as bd

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def cyl(cx, cy, r, z0, z1):
    return bd.Solid.make_cylinder(r, z1 - z0,
                                  bd.Plane(origin=(cx, cy, z0)))


def cells_of(r):
    if r is None:
        return []
    items = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and hasattr(c, "volume")
            and c.volume > 1e-6]


def vol(r):
    return sum(c.volume for c in cells_of(r))


shell = load("shell-central")
pts = {"S-E (22.06,60.75)": (22.06, 60.75), "S-W (-22.06,60.75)": (-22.06, 60.75),
       "N-E (22.06,35.25)": (22.06, 35.25), "N-W (-22.06,35.25)": (-22.06, 35.25),
       "N (0,21.5)": (0.0, 21.5),
       "N-E2 (18,30)": (18.0, 30.0), "N-W2 (-18,30)": (-18.0, 30.0),
       "E (26.5,48)": (26.5, 48.0), "W (-26.5,48)": (-26.5, 48.0),
       "N-E3 (14,24.5)": (14.0, 24.5), "N-W3 (-14,24.5)": (-14.0, 24.5)}
for label, (x, y) in pts.items():
    hit = cells_of(shell.intersect(cyl(x, y, 1.2, 4.0, 12.0)))
    if not hit:
        print(f"  {label}: NO material")
        continue
    top = max(c.bounding_box().max.Z for c in hit)
    bot = min(c.bounding_box().min.Z for c in hit)
    # continuity: slices of 0.4 from top down to bot
    gaps = []
    z = top
    while z > bot + 0.01:
        v = vol(shell.intersect(cyl(x, y, 1.2, z - 0.4, z)))
        if v < 0.05:
            gaps.append(f"{z:.1f}")
        z -= 0.4
    print(f"  {label}: top {top:.2f} bottom {bot:.2f} "
          f"vol {vol(hit):.2f} gaps at {gaps if gaps else 'none'}")
print("done")
