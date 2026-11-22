import build123d as bd
ASM = "./asm3d"
def load(n): return bd.import_brep(f"{ASM}/{n}.brep")
def cyl(cx, cy, r, z0, z1):
    return bd.Solid.make_cylinder(r, z1 - z0, bd.Plane(origin=(cx, cy, z0)))
def cells_of(r):
    if r is None: return []
    items = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and hasattr(c, "volume") and c.volume > 1e-6]
def vol(r): return sum(c.volume for c in cells_of(r))
pts = [(22.06, 60.75), (-22.06, 60.75), (22.06, 35.25), (-22.06, 35.25)]
hosts = {n: load(n) for n in ("tray-left", "tray-right", "centre-infill", "shell-central")}
for (x, y) in pts:
    b = cyl(x, y, 3.0, 7.30, 9.60)
    print(f"boss @({x},{y}): " + ", ".join(f"{n} {vol(b.intersect(s)):.3f}" for n, s in hosts.items()))
