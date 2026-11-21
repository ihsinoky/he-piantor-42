"""Localize the F2 finding: added material (new tray-right minus
pre-change tray-right) vs plate-right min distance 0.043 — find the
X band and Z band where the closest approach happens."""
import build123d as bd
import os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
OLD = "/tmp/old296"

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def cells_of(r):
    if r is None:
        return []
    return [x for x in (list(r) if isinstance(r, (list, bd.ShapeList)) else [r])
            if hasattr(x, "volume") and x.volume > 1e-9]

def fuse_all(cs):
    s = cs[0]
    for c in cs[1:]:
        s = s.fuse(c)
    return s

tray_r = bd.import_brep(f"{ASM}/tray-right.brep")
plate_r = bd.import_brep(f"{ASM}/plate-right.brep")
old_r = bd.import_brep(f"{OLD}/tray-right.brep")
added = fuse_all(cells_of(tray_r.cut(old_r)))

bands = [(41, 46), (46, 49), (49, 50.5), (50.5, 52), (52, 54),
         (54, 56), (56, 58), (58, 59), (59, 60), (60, 61)]
for xa, xb in bands:
    ac = cells_of(added.intersect(box(xa, xb, 40.0, 95.0, -3.0, 23.0)))
    pc = cells_of(plate_r.intersect(box(xa, xb, 40.0, 95.0, -3.0, 23.0)))
    if not ac or not pc:
        print(f"X {xa}..{xb}: added {'-' if not ac else 'y'} plate {'-' if not pc else 'y'}")
        continue
    a, p = fuse_all(ac), fuse_all(pc)
    print(f"X {xa}..{xb}: dist {a.distance_to(p):.3f}")
# Z split for the full range
for z0, z1 in ((-2.65, 9.3), (9.3, 10.9)):
    ac = cells_of(added.intersect(box(40.0, 62.0, 40.0, 95.0, z0, z1)))
    if ac:
        a = fuse_all(ac)
        print(f"Z {z0}..{z1}: dist {a.distance_to(plate_r):.3f}")
print("localize done")
