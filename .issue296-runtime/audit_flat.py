"""(B) audit: shell-central top over the centre field must be the
flat 10.90 (no holes, no slope remnants), outside the trackpad
keep-disc; pipe top at 10.90; plunger rest surface 10.90."""
import build123d as bd

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


shell = load("shell-central")
bad = []
holes = []
for gx in range(-40, 41, 2):
    for gy in range(0, 71, 2):
        if (gx ** 2 + (gy - 48) ** 2) ** 0.5 < 24.5:
            continue  # trackpad island exempt
        cells = shell.intersect(box(gx - 0.9, gx + 0.9, gy - 0.9,
                                    gy + 0.9, -3, 23))
        cells = [c for c in (cells if isinstance(cells, (list, bd.ShapeList))
                             else [cells])
                 if c is not None and c.volume > 1e-6]
        if not cells:
            continue  # outside the shell footprint
        top = max(c.bounding_box().max.Z for c in cells)
        if abs(top - 10.90) > 0.01:
            bad.append((gx, gy, round(top, 3)))
        # skin presence: material in Z 8.9..10.9 over the column
        skin = shell.intersect(box(gx - 0.9, gx + 0.9, gy - 0.9,
                                   gy + 0.9, 8.9, 10.9))
        skin = [c for c in (skin if isinstance(skin, (list, bd.ShapeList))
                            else [skin]) if c is not None and c.volume > 1e-6]
        if not skin:
            holes.append((gx, gy))
print("non-10.90 tops (gx, gy, top):", bad[:20], "count", len(bad))
print("skin holes:", holes[:20], "count", len(holes))
pipe = load("light-pipe-dled")
print("pipe bbox Z:", pipe.bounding_box().min.Z, pipe.bounding_box().max.Z)
pl = load("plunger-sw1")
print("plunger vs shell:", pl.intersect(shell).volume)
print("pipe vs shell:", pipe.intersect(shell).volume)
