"""Top-Z grid map of old vs new shell-central over the centre region."""
import build123d as bd
import os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def topz(s, x, y):
    try:
        r = s.intersect(box(x - 0.5, x + 0.5, y - 0.5, y + 0.5, 0, 23))
    except Exception:
        return None
    xs = list(r) if isinstance(r, (list, bd.ShapeList)) else ([r] if r is not None else [])
    xs = [q for q in xs if hasattr(q, "volume") and q.volume > 1e-6]
    if not xs:
        return None
    return max(q.bounding_box().max.Z for q in xs)

new = bd.import_brep(f"{ASM}/shell-central.brep")
old = bd.import_step("/tmp/oldshell/shell-central.step")

xs = list(range(-39, 40, 3))
ys = list(range(0, 36, 3))
print("Y\\X " + " ".join(f"{x:5d}" for x in xs))
for y in ys:
    row = []
    for x in xs:
        o, n = topz(old, x, y), topz(new, x, y)
        if o is None and n is None:
            row.append("    .")
        elif n is None:
            row.append(" HOLE")
        elif o is None:
            row.append("  NEW")
        else:
            row.append(f"{n:5.1f}")
    print(f"Y{y:3d} " + " ".join(row))
print("\n(old top for HOLE cells, same grid)")
for y in ys:
    row = []
    for x in xs:
        o, n = topz(old, x, y), topz(new, x, y)
        row.append(f"{o:5.1f}" if (o is not None and n is None) else "    .")
    print(f"Y{y:3d} " + " ".join(row))
