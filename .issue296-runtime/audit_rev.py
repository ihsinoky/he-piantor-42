"""Successor audit for the north-flush revision fixes.
1. shell centre slope surface: top vs PO profile (spine slab X -3..3,
   and lobe band X 24..28) — the sheet must have closed the hole
2. SW1: shell top at the column + plunger vs shell
3. plateau vs keycap solids: minimum distance (true built clearance)
4. finger-zone working band Z 7.40..9.40 (Stage-3 criterion footprint)
   vs case (no cover)
5. shell material above profile inside the keep-disc ring
   (22.3 < dist((0,48)) < 23.5), excluding the island itself
"""
import build123d as bd
import json, os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def pieces(r):
    if r is None:
        return []
    xs = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [x for x in xs if hasattr(x, "volume") and x.volume > 1e-6]

def inter(a, b):
    try:
        return pieces(a.intersect(b))
    except Exception:
        return []

def fuse_all(ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r

shell = part("shell-central")
plunger = part("plunger-sw1")
strip_r, strip_l = part("strip-right"), part("strip-left")

def profile_z(y):
    if y <= -0.37:
        return 22.00
    if y >= 20.0:
        return 10.90
    return 22.00 - (y + 0.37) * (11.10 / 20.37)

print("== 1. slope surface audit ==")
for label, (xa, xb) in (("spine X -3..3", (-3, 3)), ("lobe R X 24..28", (24, 28)),
                        ("lobe L X -28..-24", (-28, -24))):
    bad = []
    for y0 in range(0, 34, 2):
        ps = inter(shell, box(xa, xb, y0, y0 + 2, 0, 23))
        if not ps:
            bad.append(f"Y{y0}..{y0+2} EMPTY")
        else:
            zm = max(p.bounding_box().max.Z for p in ps)
            want = profile_z(y0)
            if abs(zm - want) > 0.35:
                bad.append(f"Y{y0}..{y0+2} top {zm:.2f} vs profile {want:.2f}")
    print(f"  {label}: {'OK (top = profile, no holes)' if not bad else '; '.join(bad)}")

print("== 2. SW1 ==")
ps = inter(shell, box(-18, -13, 61, 68, 0, 23))
top = max((p.bounding_box().max.Z for p in ps), default=None)
print(f"  shell top near SW1 column: {top} (expect 10.90)")
iv = sum(p.volume for p in inter(shell, plunger))
print(f"  plunger vs shell: {iv:.3f} mm3 (expect 0.000)")

print("== 3. plateau vs keycaps: minimum distance ==")
CAPS = json.load(open(os.path.join(RT, "caps.json")))
caps_solids = []
for side in ("left", "right"):
    for poly in CAPS[side]["cap_polys"]:
        pts = [bd.Vector(p[0], p[1], 0) for p in poly]
        w = bd.Wire.make_polygon(pts + [pts[0]])
        s = bd.extrude(bd.Face(w), 22.00 - 10.90)
        caps_solids.append(s.moved(bd.Location((0, 0, 10.90))))
caps_all = fuse_all(caps_solids)
for nm, st in (("strip-right", strip_r), ("strip-left", strip_l)):
    try:
        d = st.distance_to(caps_all)
        print(f"  {nm}: min distance to cap solids {d:.3f} mm (design clearance 1.00 plan)")
    except Exception as e:
        print(f"  {nm}: distance_to unavailable ({e})")

print("== 4. finger-zone working band Z 7.40..9.40 ==")
tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
plate_l, plate_r = part("plate-left"), part("plate-right")
cover = part("battery-cover")
pipe = part("light-pipe-dled")
case_nc = fuse_all([tray_l, tray_r, infill, shell, strip_l, strip_r,
                    plate_l, plate_r])
for nm, zb in (("east", box(22.50, 32.25, -59.62, -9.12, 7.40, 9.40)),
               ("west", box(-32.25, -22.50, -59.62, -9.12, 7.40, 9.40))):
    ps = inter(case_nc, zb)
    tot = sum(p.volume for p in ps)
    extra = ""
    if tot > 0.001:
        bb = ps[0].bounding_box()
        extra = (f"  first piece X {bb.min.X:.2f}..{bb.max.X:.2f}"
                 f" Y {bb.min.Y:.2f}..{bb.max.Y:.2f} Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
    print(f"  {nm}: {tot:.3f} mm3 (Stage-3 criterion: 0.000){extra}")

print("== 5. keep-disc ring above profile ==")
ring = bd.Solid.make_cylinder(23.5, 23.0, bd.Plane(origin=(0, 48, 0)))
inner = bd.Solid.make_cylinder(22.3, 23.0, bd.Plane(origin=(0, 48, 0)))
ring = ring.cut(inner)
ps = inter(shell, ring)
hi = [p for p in ps if p.bounding_box().max.Z > 10.91]
print(f"  ring pieces above 10.90: {len(hi)}"
      + ("" if not hi else "  max top " + f"{max(p.bounding_box().max.Z for p in hi):.2f}"))
