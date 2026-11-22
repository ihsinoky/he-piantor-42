"""Probe the shell-central geometry around the trackpad (0,48).

- radial top-Z profile of the shell at radii 16..34, 16 directions
- vertical material bands at selected radii (where is shell solid
  between Z 9 and Z 14 -> fixing material map)
- plunger-sw1 brep: bbox + horizontal slices (radius vs Z)
- keycap nearest approach to the pad centre (from caps.json)
"""
import build123d as bd
import json
import math

ASM = "./asm3d"
CX, CY = 0.0, 48.0


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

print("== shell top-Z profile around pad centre (0,48) ==")
print("   (probe: r0.3 vertical pin Z 8..23; top = max Z of hit)")
for r in (18, 20, 21, 22, 22.3, 23, 24, 25, 26, 27, 28, 30, 32, 34):
    row = []
    for k in range(16):
        th = math.radians(k * 22.5)
        x, y = CX + r * math.cos(th), CY + r * math.sin(th)
        hit = cells_of(shell.intersect(cyl(x, y, 0.3, 8.0, 23.0)))
        top = max((c.bounding_box().max.Z for c in hit), default=None)
        row.append("--" if top is None else f"{top:5.2f}")
    print(f"  r={r:5.1f}: " + " ".join(row))
print("   directions: 0=E(+X) 90=N(+Y) 180=W 270=S, step 22.5 deg")

print("== shell material bands (pin r0.5, Z slices) at key points ==")
pts = {"toward plunger (NW, r=23)": None,
       "toward plunger (NW, r=25)": None,
       "north (r=24)": (CX, CY + 24),
       "south (r=24)": (CX, CY - 24),
       "east (r=24)": (CX + 24, CY),
       "west (r=24)": (CX - 24, CY)}
th = math.atan2(16.5, -15.5)
for rr in (23, 25):
    pts[f"toward plunger (NW, r={rr})"] = (
        CX + rr * math.cos(th), CY + rr * math.sin(th))
for label, (x, y) in pts.items():
    bands = []
    for z0 in (9.0, 10.0, 10.9, 11.1, 11.5, 12.0, 12.55, 12.7, 13.0):
        v = vol(shell.intersect(cyl(x, y, 0.5, z0, z0 + 0.45)))
        bands.append(f"{z0}:{v:.2f}")
    print(f"  {label} @({x:.1f},{y:.1f}): " + " ".join(bands))

print("== plunger-sw1 geometry ==")
pl = load("plunger-sw1")
bb = pl.bounding_box()
print(f"  bbox X {bb.min.X:.2f}..{bb.max.X:.2f}  Y {bb.min.Y:.2f}.."
      f"{bb.max.Y:.2f}  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}  "
      f"vol {pl.volume:.2f}")
for z0 in (7.0, 9.0, 11.0, 12.0, 12.7, 12.9, 13.2, 13.6, 14.0):
    v = vol(pl.intersect(cyl(-15.5, 64.5, 6.0, z0, z0 + 0.3)))
    # radius of material at this height: scan r
    rr = None
    for cand in (1.5, 1.8, 2.0, 2.2, 2.5, 3.0):
        if vol(pl.intersect(cyl(-15.5, 64.5, cand, z0, z0 + 0.3))) > 0.001:
            rr = cand
    print(f"  Z {z0:5.2f}..{z0 + 0.3:5.2f}: vol in r6 pin {v:7.3f}, "
          f"min r with material {rr}")

print("== keycaps nearest the pad centre (caps.json) ==")
CAPS_J = json.load(open("./caps.json"))
best = []
for side in ("left", "right"):
    for poly in CAPS_J[side]["cap_polys"]:
        for (x, y) in poly:
            d = math.hypot(x - CX, y - CY)
            best.append((d, side, x, y))
best.sort()
for d, side, x, y in best[:8]:
    print(f"  dist {d:7.3f}  {side} cap vertex ({x:.2f},{y:.2f})")
print("done")
