"""Follow-up checks for verify_south S3/S4, with the measurement
contamination removed:
F1. wall inner face measured BELOW the skin (Z 0..9.0), so the skin
    slab cannot pollute the min-Y -> antenna band depth.
F2. plate<->skin gap measured on the ADDED material only
    (new tray minus pre-change tray from git d8b687d4b), so the
    tray's plate-seat contact cannot pollute the distance.
F3. arc zone compared against the BUILD's arc (centre
    (58.275, 77.700), R 4.0) at each 0.5-slab's west edge (the slab
    max of an arc sits at the west edge).
F4. junction step at Xt2 = 60.735: build arc endpoint (on the fitted
    diagonal) vs the pre-change face interpolated at Xt2.
"""
import build123d as bd
import json, os, math

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
OLD = "/tmp/old296"
RT = os.path.dirname(os.path.abspath(__file__))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

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

tray_r = part("tray-right")
tray_l = part("tray-left")
infill = part("centre-infill")
plate_r = part("plate-right")
case_all = tray_r.fuse(tray_l).fuse(infill)

print("== F1. wall inner face below the skin ==")
cs = cells_of(case_all.intersect(box(-0.5, 0.5, 75.0, 82.0, 0.0, 9.0)))
wall_inner = min(c.bounding_box().min.Y for c in cs)
print(f"wall inner face at X=0 (Z 0..9.0): {wall_inner:.3f}"
      f" -> band depth {wall_inner - 67.900:.3f} (expect 79.700 / 11.800)")

print("\n== F2. added material vs plate ==")
old_r = bd.import_brep(f"{OLD}/tray-right.brep")
added = cells_of(tray_r.cut(old_r))
add_s = fuse_all(added)
print(f"added material (tray-right): {len(added)} cells,"
      f" volume {add_s.volume:.1f} mm3")
print(f"added vs plate-right: intersection"
      f" {add_s.intersect(plate_r).volume if cells_of(add_s.intersect(plate_r)) else 0.0:.3f},"
      f" min distance {add_s.distance_to(plate_r):.3f} (expect ~0.300)")

print("\n== F3. arc vs build constants (slab west edge) ==")
XT1, CY, R = 58.275, 77.700, 4.0
for xc in (58.75, 59.25, 59.75, 60.25, 60.75):
    cs = cells_of(case_all.intersect(box(xc - 0.25, xc + 0.25, 40.0, 95.0, -5.0, 55.0)))
    prof = max(c.bounding_box().max.Y for c in cs)
    xw = xc - 0.25
    arc = CY + math.sqrt(max(R ** 2 - (xw - XT1) ** 2, 0.0)) if xw <= 60.735 else None
    print(f"  col {xc:6.2f}: profile {prof:.3f}, arc at west edge {xw:.2f}:"
          f" {arc:.3f}, diff {prof - arc:+.3f}")

print("\n== F4. junction step at Xt2 ==")
probe = json.load(open(os.path.join(RT, "probe_south.json")))
face = {r[0]: r[1] for r in probe["tray_face"]["R"]}
# linear interp of the pre-change face at Xt2 = 60.735
xs = sorted(face)
for a, b in zip(xs, xs[1:]):
    if a <= 60.735 <= b:
        f_xt2 = face[a] + (face[b] - face[a]) * (60.735 - a) / (b - a)
        break
arc_end = 128.2161 - 0.7798 * 60.735   # build fit line at Xt2
print(f"pre-change face at Xt2 (interp): {f_xt2:.3f}; arc endpoint"
      f" (on fitted diagonal): {arc_end:.3f}; step {arc_end - f_xt2:+.3f}")
print("verify_south_fix done")
