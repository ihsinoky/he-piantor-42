"""Issue #296 P0/P1 — focused re-checks (fixes to verify_p0p1 B/F):
1. insert min wall at +-55 via the RING grow test (the plain grow
   test in verify_p0p1 was void: it overlapped the hole itself).
2. boss ring fraction at +-85 with the ring clipped to the
   outline (Y >= -64.37; the raw ring includes the by-design
   flush-trim segment outside the outline).
3. axis-to-capline for the left screws (signed column lookup).
4. finger working band only (Z 7.40..9.40), shelf OFF.
5. locate the tray<->Wings+underside intersection pieces (the
   total rose 42.380 -> 42.991 per side vs the shelf round).
"""
import build123d as bd
import json, os

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))
ZC = 2.65
FLUSH_Y = -64.37
ROW_Y = -60.37

def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def cyl(cx, cy, r, z0, z1):
    return bd.Solid.make_cylinder(r, z1 - z0, bd.Plane(origin=(cx, cy, z0)))

def fuse_all(ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r

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
            if hasattr(x, "volume") and x.volume > 1e-6]

tray_l, tray_r = part("tray-left"), part("tray-right")
CAPS = json.load(open(os.path.join(RT, "caps.json")))

print("== 1. insert min wall at +-55 (ring grow test) ==")
for X, tray in ((55, tray_r), (-55, tray_l)):
    wall = 0.0
    for w in (0.25, 0.5, 0.75, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0):
        ring = cyl(X, ROW_Y, 2.1 + w, 5.3, 10.6).cut(cyl(X, ROW_Y, 2.1, 5.2, 10.7))
        if inter_vol(tray, ring) / ring.volume > 0.999:
            wall = w
        else:
            break
    print(f"X {X:+4d}: min wall >= {wall:.2f} mm")

print("\n== 2. boss ring fraction at +-85 (ring clipped to outline) ==")
for X, tray, plate in ((85, tray_r, part("plate-right")),
                       (-85, tray_l, part("plate-left"))):
    ring = cyl(X, ROW_Y, 4.6, 4.0, 10.90).cut(cyl(X, ROW_Y, 2.1, 3.9, 11.0))
    ring = ring.cut(plate)
    ring = ring.intersect(box(X - 6, X + 6, FLUSH_Y, 0, 3.0, 11.5))
    rr = solids_of(ring)
    ring = fuse_all(rr) if rr else ring
    print(f"X {X:+4d}: tray material fraction of boss ring "
          f"{inter_vol(tray, ring) / ring.volume:.3f}")

print("\n== 3. axis-to-capline, left screws (signed lookup) ==")
for X in (-55, -85):
    caps_d = CAPS["left"]["capline"]
    ks = [int(k) for k in caps_d if abs(int(k) - X) <= 4]
    cl = min(caps_d[str(k)] for k in ks)
    print(f"X {X:+4d}: capline near column {cl:.2f}, axis-to-capline {cl - ROW_Y:.2f} mm")

print("\n== 4. finger working band Z 7.40..9.40, shelf OFF ==")
case_noshelf = fuse_all([tray_l, tray_r, part("centre-infill"),
                         part("shell-central"), part("plate-left"),
                         part("plate-right"), part("plunger-sw1"),
                         part("light-pipe-dled")])
for sgn, nm in ((+1, "east"), (-1, "west")):
    zone = box(22.50, 30.25, -59.62, -9.12, 7.40, 9.40) if sgn > 0 else \
        box(-30.25, -22.50, -59.62, -9.12, 7.40, 9.40)
    print(f"finger band {nm}: vs case(no shelf) {inter_vol(case_noshelf, zone):9.3f}")

print("\n== 5. tray <-> Wings+underside intersection pieces ==")
wing_l, wing_r = g17("wing_left", -9.5), g17("wing_right", 9.5)
und_l = fuse_all([g17(e["name"], -9.5) for e in idx
                  if e["name"].startswith("underside-left")])
und_r = fuse_all([g17(e["name"], 9.5) for e in idx
                  if e["name"].startswith("underside-right")])
wings = fuse_all([wing_l, wing_r, und_l, und_r])
for nm, tray in (("tray-right", tray_r), ("tray-left", tray_l)):
    pieces = solids_of(tray.intersect(wings))
    print(f"{nm}: {len(pieces)} pieces, total {sum(p.volume for p in pieces):.3f} mm3")
    for p in pieces:
        bb = p.bounding_box()
        print(f"   vol {p.volume:8.3f}  X {bb.min.X:7.2f}..{bb.max.X:7.2f}"
              f"  Y {bb.min.Y:7.2f}..{bb.max.Y:7.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}")
