"""Issue #296 P0/P1 — pre-change measurements.
1. Insert-hole (O4.2 at Y -60.37) material fraction + min wall +
   floor on the CURRENT trays, with the -61.37 pilot void fused
   back so the probe sees pre-pilot material.
2. Shelf plan outline (convex hull of vertices) + rotated bed fit
   for 220 / 256 / 300 beds, raw and with margins.
3. Notch band probe: shelf outline min Y per X band near the ends.
4. Joint cross-section at X = +-30.25 (shelf material Y/Z extent
   in slabs either side of the plane) for pin placement.
"""
import build123d as bd
import json, os, math

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

tray_r, tray_l = part("tray-right"), part("tray-left")
shelf = part("north-shelf")

print("== 1. insert-hole material at Y -60.37 (pilot void restored) ==")
for X in (55, 85):
    for sgn, tray in ((+1, tray_r), (-1, tray_l)):
        cx = sgn * X
        restored = tray.fuse(cyl(cx, -61.37, 1.35, 4.0, 10.90))
        hole = cyl(cx, -60.37, 2.1, 5.0, 10.90)
        frac = inter_vol(restored, hole) / hole.volume
        # min wall: grow the hole radius until the grown cylinder
        # (Z trimmed to avoid edge effects) is no longer fully inside
        wall = 0.0
        for w in (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0):
            g = cyl(cx, -60.37, 2.1 + w, 5.3, 10.6)
            if inter_vol(restored, g) / g.volume > 0.999:
                wall = w
            else:
                break
        floor = cyl(cx, -60.37, 2.1, 2.5, 5.0)
        ffrac = inter_vol(restored, floor) / floor.volume
        print(f"X {cx:+4d}: hole material fraction {frac:.3f}, min wall >= {wall:.2f} mm,"
              f" floor (Z 2.5..5.0) fraction {ffrac:.3f}")

print("\n== 2. shelf outline + bed fit ==")
vs = {(round(v.X, 3), round(v.Y, 3)) for v in shelf.vertices()}
pts = sorted(vs)
def hull(points):
    def cross(o, a, b):
        return (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0])
    lower = []
    for p in points:
        while len(lower) >= 2 and cross(lower[-2], lower[-1], p) <= 0:
            lower.pop()
        lower.append(p)
    upper = []
    for p in reversed(points):
        while len(upper) >= 2 and cross(upper[-2], upper[-1], p) <= 0:
            upper.pop()
        upper.append(p)
    return lower[:-1] + upper[:-1]
H = hull(pts)
print(f"hull vertices: {len(H)}")
for p in H:
    print(f"   ({p[0]:8.2f}, {p[1]:8.2f})")
import numpy as np
A = np.array(H)
for S in (220, 256, 300):
    best = None
    for th_d in range(0, 9001, 5):
        th = math.radians(th_d / 100.0)
        c, s = math.cos(th), math.sin(th)
        R = A @ np.array([[c, s], [-s, c]]).T
        w = R[:, 0].max() - R[:, 0].min()
        h = R[:, 1].max() - R[:, 1].min()
        slack = S - max(w, h)
        if best is None or slack > best[0]:
            best = (slack, th_d / 100.0, w, h)
    print(f"bed {S}: best slack {best[0]:+.2f} mm at theta {best[1]:.2f} deg"
          f" (rotated bbox {best[2]:.1f} x {best[3]:.1f})")

print("\n== 3. notch band probe: shelf min Y per 2 mm X band (right end) ==")
for xa in range(112, 140, 2):
    sl = shelf.intersect(box(xa, xa + 2, -70, 0, 11.0, 14.7))
    ss = [x for x in (list(sl) if isinstance(sl, (list, bd.ShapeList)) else [sl])
          if x is not None and hasattr(x, "volume") and x.volume > 1e-6]
    if ss:
        print(f"X {xa}..{xa + 2}: shelf material min Y "
              f"{min(c.bounding_box().min.Y for c in ss):7.2f}, vol "
              f"{sum(c.volume for c in ss):8.1f}")
    else:
        print(f"X {xa}..{xa + 2}: no shelf material at Z 11..14.7")

print("\n== 4. joint cross-section at X = +-30.25 ==")
for sgn in (+1, -1):
    for d0, d1 in ((0.0, 12.0), (-12.0, 0.0)):
        xa, xb = (30.25 + d0, 30.25 + d1) if sgn > 0 else (-30.25 - d1, -30.25 - d0)
        sl = shelf.intersect(box(xa, xb, -70, 5, 15.0, 22.5))
        ss = [x for x in (list(sl) if isinstance(sl, (list, bd.ShapeList)) else [sl])
              if x is not None and hasattr(x, "volume") and x.volume > 1e-6]
        if ss:
            bb = ss[0].bounding_box()
            for c in ss[1:]:
                bb = bd.BoundBox(bb.min, bb.max)  # placeholder, use prints below
            ys = (min(c.bounding_box().min.Y for c in ss),
                  max(c.bounding_box().max.Y for c in ss))
            zs = (min(c.bounding_box().min.Z for c in ss),
                  max(c.bounding_box().max.Z for c in ss))
            print(f"sgn {sgn:+d} X {xa:7.2f}..{xb:7.2f} (Z>=15 slab): Y {ys[0]:7.2f}..{ys[1]:6.2f}"
                  f"  Z {zs[0]:5.2f}..{zs[1]:5.2f}  vol {sum(c.volume for c in ss):9.1f}")
        else:
            print(f"sgn {sgn:+d} X {xa:7.2f}..{xb:7.2f}: no material Z>=15")
