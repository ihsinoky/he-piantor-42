"""Issue #296 shelf-trim probe: geometry around the north band.

1. Shelf bbox / volume; cover-only span check.
2. For candidate latch X sites inside |X|<=30.25: tray material
   top Z in the wall band (Y -64.4..-62.4) and the bay band
   (Y -62.4..-58.0); shelf underside min Z over Y -62..-55.
3. Tray top under the strips (|X| 35..150) — exposed-tray audit:
   max Z of tray material under the strip footprint band
   Y -64.4..-5, and any tray feature above Z 11.10 there.
"""
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


shelf = load("north-shelf")
bb = shelf.bounding_box()
print(f"shelf bbox X {bb.min.X:.2f}..{bb.max.X:.2f} "
      f"Y {bb.min.Y:.2f}..{bb.max.Y:.2f} Z {bb.min.Z:.2f}..{bb.max.Z:.2f} "
      f"vol {shelf.volume:.1f}")

trays = [load("tray-left"), load("tray-right"), load("centre-infill")]
tray = trays[0]
for t in trays[1:]:
    tray = tray.fuse(t)

for xc in (-28, -24, -20, -16, -12, 12, 16, 20, 24, 28):
    out = [f"X {xc:+d}:"]
    for label, (y0, y1) in (("wall", (-64.4, -62.4)),
                            ("bayN", (-62.4, -58.0))):
        r = solids(tray.intersect(box(xc - 0.5, xc + 0.5, y0, y1, -1, 23)))
        if r:
            top = max(c.bounding_box().max.Z for c in r)
            vol = sum(c.volume for c in r)
            out.append(f"{label} top {top:.2f} vol {vol:.0f}")
        else:
            out.append(f"{label} --")
    r = solids(shelf.intersect(box(xc - 0.5, xc + 0.5, -62.0, -55.0, -1, 23)))
    if r:
        bot = min(c.bounding_box().min.Z for c in r)
        out.append(f"shelf-under min {bot:.2f}")
    print("  ".join(out))

# tray material above 11.10 under the strip footprint (audit)
for sgn in (+1, -1):
    xa, xb = (31.0, 153.0) if sgn > 0 else (-153.0, -31.0)
    r = solids(tray.intersect(box(xa, xb, -64.4, -5.0, 11.10, 23.0)))
    vol = sum(c.volume for c in r)
    print(f"strip zone {'R' if sgn>0 else 'L'}: tray above 11.10 vol {vol:.1f}")
    for c in r:
        cb = c.bounding_box()
        print(f"   piece vol {c.volume:8.1f} X {cb.min.X:7.2f}..{cb.max.X:7.2f}"
              f" Y {cb.min.Y:7.2f}..{cb.max.Y:7.2f} Z {cb.min.Z:.2f}..{cb.max.Z:.2f}")
