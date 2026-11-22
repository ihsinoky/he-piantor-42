"""Material map of shell-central around the trackpad.

Grid X -30..30, Y 18..78 step 2.5. For each point a r0.4 pin
Z 5..23: report the shell top Z in bands:
  ' ' no material   '.' top <10.5   'f' ~10.90 field
  'r' ~11.10 seat floor   'R' ~12.55 rim   'H' >13 rise
Also: screw-column test at candidate points — is the material
column continuous from the top down to Z 7.5 (vol of pin slices)?
"""
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

xs = [-30 + 2.5 * i for i in range(25)]
ys = [18 + 2.5 * i for i in range(25)]
print("map: rows Y 78 (top, case south) -> 18 (case north); cols X -30..30")
print("     pad centre (0,48) marked @; plunger (-15.5,64.5) approx P")
for y in reversed(ys):
    row = ""
    for x in xs:
        hit = cells_of(shell.intersect(cyl(x, y, 0.4, 5.0, 23.0)))
        if not hit:
            row += " "
            continue
        top = max(c.bounding_box().max.Z for c in hit)
        if top < 10.5:
            ch = "."
        elif top < 11.0:
            ch = "f"
        elif top < 12.0:
            ch = "r"
        elif top < 13.2:
            ch = "R"
        else:
            ch = "H"
        if abs(x) < 1.3 and abs(y - 48) < 1.3:
            ch = "@"
        row += ch
    print(f"  Y={y:5.1f} |{row}|")

print("== screw-column continuity (pin r0.9 slices of 0.5) ==")
cands = {"NE30 (22.9,34.8)": (22.9, 34.8), "NW150 (-22.9,61.3)": (-22.9, 61.3),
         "SW210 (-22.9,34.8)": (-22.9, 34.8), "SE330 (22.9,61.3)": (22.9, 61.3),
         "E (26.5,48)": (26.5, 48.0), "W (-26.5,48)": (-26.5, 48.0),
         "N (0,21.5)": (0.0, 21.5), "N-r24 (0,24)": (0.0, 24.0),
         "E-r24 (24,48)": (24.0, 48.0), "W-r24 (-24,48)": (-24.0, 48.0)}
for label, (x, y) in cands.items():
    slices = []
    z = 11.4
    while z > 7.0:
        v = vol(shell.intersect(cyl(x, y, 0.9, z - 0.5, z)))
        slices.append(f"{z:.1f}:{v:.2f}")
        z -= 0.5
    top = cells_of(shell.intersect(cyl(x, y, 0.4, 5.0, 23.0)))
    tz = max((c.bounding_box().max.Z for c in top), default=None)
    print(f"  {label}: top {tz}  " + " ".join(slices))
print("done")
