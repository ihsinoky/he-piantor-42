"""Issue #296 shelf: confirm the final fixing positions.
Four flat-head M3 at (±55, -61.37) and (±85, -61.37), all in the
plateaus, pilots into the tray north fill. (Centre wall pair at
-63.37 cannot take a standard head: axis is 1.00 from the flush
face, any head radius > 1.0 stands proud of the outline — see
shelf-plan.md addendum in case-3d.md.)
Checks per position: pilot fill fraction in the CURRENT trays
(Z 4.0..10.9); screw-shaft cylinder (r1.5, Z 3.0..10.9) vs Wings /
plates / Main (must be 0 — the shaft lives inside tray material).
"""
import build123d as bd
import json, os, math

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
ZC = 2.65

def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

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

tray_r, tray_l = part("tray-right"), part("tray-left")
plate_r, plate_l = part("plate-right"), part("plate-left")
wing_l, wing_r = g17("wing_left", -9.5), g17("wing_right", 9.5)
und = fuse_all([g17(e["name"], -9.5 if e["name"].endswith("left") or "-L" in e["name"] else 9.5)
                for e in idx if e["name"].startswith("underside-")])
wings = fuse_all([wing_l, wing_r, und])
plates = fuse_all([plate_l, plate_r])

pilot_full = math.pi * 1.35 ** 2 * 6.9    # Z 4.0..10.9
for X in (55, 85):
    for sgn, tray in ((+1, tray_r), (-1, tray_l)):
        cx = sgn * X
        pv = inter_vol(tray, cyl(cx, -61.37, 1.35, 4.0, 10.9))
        shaft = cyl(cx, -61.37, 1.5, 3.0, 10.9)
        print(f"X {cx:+4d}: pilot fill {pv:6.2f} / {pilot_full:.2f} = {pv / pilot_full:6.1%}"
              f"   shaft vs wings {inter_vol(wings, shaft):7.3f}"
              f"  vs plates {inter_vol(plates, shaft):7.3f}")
