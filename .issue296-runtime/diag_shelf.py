"""Issue #296 shelf: choose the outboard screw column XS.
Measures, per candidate column: (1) built plateau Y extent (north
face -> key line) from the strip BREPs; (2) tray material backing a
O2.7 pilot at (XS, -63.37): pilot-cylinder fill fraction in the
tray, and the tray material band depth at that column.
"""
import build123d as bd
import json, os, math

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
FLUSH_Y = -64.37

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

def slabs(s, b):
    r = s.intersect(b)
    if r is None:
        return []
    return [x for x in (list(r) if isinstance(r, (list, bd.ShapeList)) else [r])
            if hasattr(x, "volume") and x.volume > 1e-6]

strip_r, strip_l = part("strip-right"), part("strip-left")
tray_r, tray_l = part("tray-right"), part("tray-left")

pilot_full = math.pi * 1.35 ** 2 * 7.9   # cyl Z 3.0..10.9
print(f"pilot cyl full vol: {pilot_full:.2f} mm3")
print(f"{'XS':>5} {'plateau Y range (R)':>22} {'depth':>6} "
      f"{'pilot fill R':>12} {'band->Y R':>10} {'pilot fill L':>12} {'band->Y L':>10}")
for XS in (55, 65, 75, 80, 85, 90, 95, 100, 105):
    row = [f"{XS:5d}"]
    for strip, tray, sgn in ((strip_r, tray_r, +1), (strip_l, tray_l, -1)):
        x0, x1 = (XS - 0.5, XS + 0.5) if sgn > 0 else (-XS - 0.5, -XS + 0.5)
        cells = slabs(strip, box(x0, x1, -70, 10, 10.9, 22.0))
        if cells:
            ymin = min(c.bounding_box().min.Y for c in cells)
            ymax = max(c.bounding_box().max.Y for c in cells)
            row.append(f"Y {ymin:7.2f}..{ymax:6.2f}  d={ymax - FLUSH_Y:5.2f}" if sgn > 0
                       else f"{ymax:9.2f}")
            if sgn > 0:
                pass
        else:
            row.append("no plateau" if sgn > 0 else "none")
        cx = XS if sgn > 0 else -XS
        pv = inter_vol(tray, cyl(cx, -63.37, 1.35, 3.0, 10.9))
        band = slabs(tray, box(cx - 0.25, cx + 0.25, -64.37, -50, 3.0, 10.9))
        bmax = max(c.bounding_box().max.Y for c in band) if band else float("nan")
        row.append(f"{pv / pilot_full:11.1%}")
        row.append(f"{bmax:9.2f}" if band else "     none")
    print(" ".join(row))
