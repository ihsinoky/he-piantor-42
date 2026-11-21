"""Issue #296 P0/P1 — locate the void near the +-85 insert holes."""
import build123d as bd
import os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def cyl(cx, cy, r, z0, z1):
    return bd.Solid.make_cylinder(r, z1 - z0, bd.Plane(origin=(cx, cy, z0)))

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

def solids_of(r):
    if r is None:
        return []
    return [x for x in (list(r) if isinstance(r, (list, bd.ShapeList)) else [r])
            if hasattr(x, "volume") and x.volume > 1e-9]

for X, tray_name in ((85, "tray-right"), (-85, "tray-left")):
    tray = part(tray_name)
    cx = X
    restored = tray.fuse(cyl(cx, -61.37, 1.35, 4.0, 10.90))
    hole = cyl(cx, -60.37, 2.1, 5.0, 10.90)
    void = solids_of(hole.cut(restored))
    print(f"X {cx:+d}: void pieces {len(void)}, total "
          f"{sum(v.volume for v in void):.3f} mm3")
    for v in void:
        bb = v.bounding_box()
        print(f"   void bbox X {bb.min.X:7.2f}..{bb.max.X:7.2f}  Y {bb.min.Y:7.2f}.."
              f"{bb.max.Y:7.2f}  Z {bb.min.Z:5.2f}..{bb.max.Z:5.2f}  vol {v.volume:.3f}")
    # where does tray material end south of the hole? probe columns
    for dy in (-58.0, -58.5, -59.0, -59.5, -60.0):
        p = box(cx - 1.0, cx + 1.0, dy - 0.5, dy + 0.5, 5.0, 10.90)
        print(f"   probe Y {dy:6.1f}: tray fraction "
              f"{inter_vol(restored, p) / p.volume:.3f}")
    # boss candidate: r 4.6 cyl Z 4.0..10.90 — what would it add?
    boss = cyl(cx, -60.37, 4.6, 4.0, 10.90)
    print(f"   boss r4.6 adds {boss.volume - inter_vol(restored, boss):.1f} mm3"
          f" of new material (boss vol {boss.volume:.1f})")
