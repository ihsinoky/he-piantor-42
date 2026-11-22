"""Localise the tolerance-corner interference: bbox of the
cover x shell overlap solid for +-0.20 shifts."""
import build123d as bd

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def cells_of(r):
    if r is None:
        return []
    items = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and hasattr(c, "volume")
            and c.volume > 1e-6]


cover = load("trackpad-cover")
shell = load("shell-central")
for (dx, dy, lab) in [(0.20, 0, "+0.20 X"), (-0.20, 0, "-0.20 X"),
                      (0, 0.20, "+0.20 Y"), (0, -0.20, "-0.20 Y")]:
    cov2 = cover.moved(bd.Location((dx, dy, 0)))
    cells = cells_of(cov2.intersect(shell))
    print(f"{lab}: {len(cells)} cell(s), total "
          f"{sum(c.volume for c in cells):.4f} mm3")
    for c in cells:
        bb = c.bounding_box()
        print(f"   vol {c.volume:8.4f}  X {bb.min.X:7.2f}..{bb.max.X:7.2f}"
              f"  Y {bb.min.Y:7.2f}..{bb.max.Y:7.2f}"
              f"  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}")
print("done")
