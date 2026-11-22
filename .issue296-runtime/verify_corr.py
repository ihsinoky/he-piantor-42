"""Issue #296 shelf-CORRECTION round verification.

The trim round cut the shelf to the cover alone (PMO misread the
PO instruction); this round restores the band over both Wing key
fields, ending at X +-152.30 (outermost keycap extent 151.001 +
the 1.30 cap-gap margin). The latch stays at the trim round's
X +12 bay-north-rib seat; the abolished X +85 plateau seat
(groove/dip/slot) is NOT restored.

1. Closed-state interference suite (case parts pairwise; case vs
   internals incl. the synthetic power-board model of
   verify_p0p1).
2. Hinge pin fit (pin in holes/slots = 0.000).
3. Arc sweep: shelf + latch slider (slider at the east ENTRY
   position, the opening configuration) rotated about the hinge
   axis A (Y -0.57, Z 19.30) 0..100 deg vs caps (pressed +
   unpressed), trackpad island, Fly + plugged USB-C envelope,
   desk plane, the fixed case parts and the pin. Expected: the
   ONLY contact is the shelf vs the stop post (inside
   fixed-case), first at ~95 deg.
4. Open state at the stop angle + closed (shelf off): all 3
   cells extract on the established motions of verify_case3d
   (slide 2.0 toward the spring end, tip to 35 deg, swept
   volume); report intersections per obstacle.
5. Latch proof (RELOCATED seat, bay north rib at X +12 — the
   centre span is wall-capped at 7.80 and has no web): lift
   test at the 3 slider positions vs the receiver hosts
   (centre-infill + tray-right).
6. Correction audits: shelf X span = +-152.30 and a single
   solid; closed shelf vs caps and vs the 1.30 cap keep-outs;
   end-face clearance to the nearest cap (min distance shelf vs
   the outermost caps and vs all caps); band-restoration checks
   (the abolished stem slot through the right plateau is solid
   band material again; the old +85 receiver pocket in
   tray-right stays filled).
7. Invariants: outline, Z max, north-face deviation.
"""
import build123d as bd
import json
import math

ASM = "./asm3d"
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
ZC = 2.65
AX_Y, AX_Z = -0.57, 19.30
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))


def cells_of(r):
    if r is None:
        return []
    items = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and hasattr(c, "volume")
            and c.volume > 1e-6]


def vol(r):
    return sum(c.volume for c in cells_of(r))


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


def cyl(cx, cy, r, z0, z1):
    return bd.Solid.make_cylinder(r, z1 - z0,
                                  bd.Plane(origin=(cx, cy, z0)))


def fuse_all(lst):
    f = lst[0]
    for s in lst[1:]:
        f = f.fuse(s)
    return f


def report(label, v):
    print(f"  {label:52s} {v:12.4f} mm3")
    return v


parts = {n: load(n) for n in
         ("tray-left", "tray-right", "centre-infill", "shell-central",
          "north-shelf", "plate-left", "plate-right", "plunger-sw1",
          "light-pipe-dled", "latch-slider")}
names = list(parts)
print("== closed: case parts pairwise ==")
worst = 0.0
for i, a in enumerate(names):
    for b in names[i + 1:]:
        v = vol(parts[a].intersect(parts[b]))
        if v > 0.0005:
            report(f"{a} x {b}", v)
        worst = max(worst, v)
print(f"  pairwise worst: {worst:.4f}")

main = g17("main")
wing_l, wing_r = g17("wing_left", -9.5), g17("wing_right", 9.5)
und = [g17(e["name"], -9.5 if e["name"].startswith("underside-left")
           else 9.5)
       for e in idx if e["name"].startswith("underside-")]
WING = fuse_all([wing_l, wing_r] + und)
# real Fly + real plugged USB-C plug (g17 reference solids at the
# FLYMOVE pose, as verify_case3d section H / verify_p0p1)
FLY_C = json.load(open(f"{ASM}/params.json"))["fly_centre"]
FLYMOVE = (FLY_C[0], FLY_C[1] + 50.14)
fly_real = fuse_all([g17(e["name"]) for e in idx
                     if e["name"].startswith("Fly-official")])
fly_real = fly_real.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
plug_real = fuse_all([g17(n) for n in ("USB-reference-shell",
                                       "USB-reference-overmold",
                                       "USB-reference-cable-exit")])
plug_real = plug_real.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
# power board: synthetic model from verify_p0p1 (board + tongues)
pb = box(-26.25, 26.25, -62.37, -4.37, -0.65, 0.15)
for (sx0, sx1, fy0, fy1) in [(-22.50, -6.50, -8.87, -6.22),
                             (6.50, 22.50, -8.87, -6.22),
                             (-8.5, 8.5, -62.52, -59.87)]:
    pb = pb.cut(box(sx0, sx1, fy0, fy1, -1.0, 0.5))
pb_parts = fuse_all([pb, box(-3, 3, -7.3, -4.37, 0.15, 3.05),
                     box(-20, -16.8, -6.0, -4.4, 0.15, 1.15)])
track = cyl(0.0, 48.0, 22.0, 11.10, 12.60)
internals = {"main": main, "wings": WING, "power board": pb_parts,
             "fly-real": fly_real, "usb-plug-real": plug_real,
             "trackpad44": track}
print("== closed: case vs internals ==")
for pn in names:
    for iname, s in internals.items():
        report(f"{pn} x {iname}", vol(parts[pn].intersect(s)))

# ---- battery extraction sweeps (machinery of verify_case3d) ----
def aa_cell(cx):
    return bd.Solid.make_cylinder(7.25, 50.5,
                                  bd.Plane(origin=(cx, -59.62, 7.40),
                                           z_dir=(0, 1, 0)))


def cell_sweep(cx, spring):
    cell = aa_cell(cx)
    if spring == 'S':
        cell = cell.moved(bd.Location((0, 2.0, 0)))
        piv = bd.Vector(cx, -8.37, 7.40)
    else:
        cell = cell.moved(bd.Location((0, -2.0, 0)))
        piv = bd.Vector(cx, -60.37, 7.40)
    swept = cell
    for k in range(1, 8):
        th = 5.0 * k
        best = None
        for sgn in (+1, -1):
            loc = (bd.Location((piv.X, piv.Y, piv.Z))
                   * bd.Location((0, 0, 0), (1, 0, 0), sgn * th)
                   * bd.Location((-piv.X, -piv.Y, -piv.Z)))
            cand = cell.moved(loc)
            score = cand.bounding_box().max.Z
            if best is None or score > best[0]:
                best = (score, cand)
        swept = swept.fuse(best[1])
    return swept


switch_env = box(-4.25, 4.25, -6.87, -3.37, 3.40, 7.40)
fixed = {n: parts[n] for n in names
         if n not in ("north-shelf", "latch-slider")}
CELLDEF = [(-15, 'S', "W"), (0, 'N', "M"), (15, 'S', "E")]
print("== closed (shelf off): cell extraction sweeps ==")
for cx, spring, tag in CELLDEF:
    sw = cell_sweep(cx, spring)
    hits = {n: vol(sw.intersect(s)) for n, s in fixed.items()}
    hits["wings"] = vol(sw.intersect(WING))
    hits["power board"] = vol(sw.intersect(pb_parts))
    hits["switch env"] = vol(sw.intersect(switch_env))
    print(f"  cell {tag} (cx {cx:+d}, spring {spring}): "
          + ", ".join(f"{k} {v:.3f}" for k, v in hits.items()))

print("== hinge pin fit (closed) ==")
def one_pin(sgn):
    shaft = bd.Solid.make_cylinder(
        1.0, 10.3, bd.Plane(origin=(0.5 if sgn > 0 else -10.80,
                                    AX_Y, AX_Z),
                            x_dir=(0, 1, 0), z_dir=(1, 0, 0)))
    head = bd.Solid.make_cylinder(
        1.7, 0.4, bd.Plane(origin=(0.1 if sgn > 0 else -0.5,
                                   AX_Y, AX_Z),
                           x_dir=(0, 1, 0), z_dir=(1, 0, 0)))
    return shaft.fuse(head)


pin = one_pin(+1).fuse(one_pin(-1))
for pn in ("centre-infill", "tray-left", "north-shelf"):
    report(f"pin x {pn}", vol(pin.intersect(parts[pn])))


def rot(s, deg):
    loc = (bd.Location((0, AX_Y, AX_Z))
           * bd.Location((0, 0, 0), (-deg, 0, 0))
           * bd.Location((0, -AX_Y, -AX_Z)))
    return s.moved(loc)


shelf = parts["north-shelf"]
bb = rot(shelf, 90).bounding_box()
print(f"  rot sanity: shelf at 90 deg: Y {bb.min.Y:.1f}..{bb.max.Y:.1f} "
      f"Z {bb.min.Z:.1f}..{bb.max.Z:.1f} (north edge should be UP)")
# opening configuration: slider slid to the EAST entry, riding
# with the shelf (the bar exits through its keyhole entry)
slider_entry = parts["latch-slider"].moved(bd.Location((3.8, 0, 0)))
shelf_asm = shelf.fuse(slider_entry)

CAPS_J = json.load(open("./caps.json"))


def cap_solids(z1):
    """Keycap prisms from caps.json polygons (as verify_p0p1):
    extruded from the plate top 10.90 to z1 (22.00 unpressed,
    19.00 pressed)."""
    ss = []
    for side in ("left", "right"):
        for poly in CAPS_J[side]["cap_polys"]:
            pts2 = [bd.Vector(p[0], p[1], 0) for p in poly]
            w = bd.Wire.make_polygon(pts2 + [pts2[0]])
            s = bd.extrude(bd.Face(w), z1 - 10.90)
            ss.append(s.moved(bd.Location((0, 0, 10.90))))
    return fuse_all(ss)


CAPS = {"caps-unpressed": cap_solids(22.00),
        "caps-pressed": cap_solids(19.00)}
obstacles = {"caps-unpressed": CAPS["caps-unpressed"],
             "caps-pressed": CAPS["caps-pressed"],
             "trackpad44": track,
             "fly-real": fly_real,
             "plug-real": plug_real,
             "desk": box(-160, 160, -70, 90, -20, -2.65),
             "pin": pin}
obstacles.update({f"fixed:{n}": s for n, s in fixed.items()})
print("== arc sweep: ALL contacts (angle, obstacle, mm3) ==")
contacts = []
angles = sorted(set([i * 2.5 for i in range(41)]
                    + [88 + 0.5 * i for i in range(25)]))
for deg in angles:
    if deg == 0:
        continue
    rs = rot(shelf_asm, deg)
    for onm, o in obstacles.items():
        v = vol(rs.intersect(o))
        if v > 0.0005:
            contacts.append((deg, onm, round(v, 3)))
for deg, onm, v in contacts:
    print(f"  {deg:6.1f} deg  {onm:18s} {v:10.3f}")
shell_hits = [c for c in contacts if c[1] == "fixed:shell-central"]
stop_angle = shell_hits[0][0] if shell_hits else 95.0
print(f"  -> stop contact (first shelf x shell-central): {stop_angle}")

print(f"== open state at {stop_angle} deg: cell extraction ==")
open_shelf = rot(shelf_asm, stop_angle)
for cx, spring, tag in CELLDEF:
    sw = cell_sweep(cx, spring)
    hits = {}
    for n, s in fixed.items():
        try:
            hits[n] = vol(sw.intersect(s))
        except Exception:
            hits[n] = -1.0
    try:
        hits["open-shelf+slider"] = vol(sw.intersect(open_shelf))
    except Exception:
        hits["open-shelf+slider"] = -1.0
    hits["wings"] = vol(sw.intersect(WING))
    hits["power board"] = vol(sw.intersect(pb_parts))
    print(f"  cell {tag} (cx {cx:+d}, spring {spring}): "
          + ", ".join(f"{k} {v:.3f}" for k, v in hits.items()))

print("== latch proof (relocated: bay north rib at X +12) ==")
slider = parts["latch-slider"]
receiver = parts["centre-infill"].fuse(parts["tray-right"])
for label, dx in (("centred (locked)", 0.0), ("east (entry)", 3.8),
                  ("west (entry)", -3.8)):
    mv = slider.moved(bd.Location((dx, 0, 0)))
    a = vol(mv.intersect(receiver))
    b = vol(mv.intersect(parts["tray-left"]))
    c2 = vol(mv.intersect(shelf))
    pair = slider.moved(bd.Location((dx, 0, 1.0)))
    eng = vol(pair.intersect(receiver))
    print(f"  slider {label}: vs receiver {a:.3f}, vs tray-left "
          f"{b:.3f}, vs shelf {c2:.3f}; lifted 1 mm slider x "
          f"receiver {eng:.3f}")

print("== correction audits ==")
sbb = parts["north-shelf"].bounding_box()
print(f"  shelf span X {sbb.min.X:.2f}..{sbb.max.X:.2f}  "
      f"vol {parts['north-shelf'].volume:.1f}")
nsol = len(parts["north-shelf"].solids())
print(f"  shelf solids: {nsol} (expect 1)")
for nm, cs in CAPS.items():
    report(f"closed shelf x {nm}", vol(parts["north-shelf"].intersect(cs)))


def prism2d(pts, z0, z1):
    area = 0.0
    for i in range(len(pts)):
        x0, y0 = pts[i]
        x1, y1 = pts[(i + 1) % len(pts)]
        area += x0 * y1 - x1 * y0
    if area < 0:
        pts = pts[::-1]
    w = bd.Wire.make_polygon([bd.Vector(x, y, 0) for (x, y) in pts] +
                             [bd.Vector(*pts[0], 0)])
    s = bd.extrude(bd.Face(w), z1 - z0)
    return s.moved(bd.Location((0, 0, z0)))


def cap_keepout(poly, g, z0, z1):
    pts = [(p[0], p[1]) for p in poly]
    n = len(pts)
    cen = (sum(p[0] for p in pts) / n, sum(p[1] for p in pts) / n)
    solids = [prism2d(pts, z0, z1)]
    for i in range(n):
        ax, ay = pts[i]
        bx, by = pts[(i + 1) % n]
        ex, ey = bx - ax, by - ay
        ln = (ex * ex + ey * ey) ** 0.5
        nx, ny = ey / ln, -ex / ln
        mx, my = (ax + bx) / 2 + nx, (ay + by) / 2 + ny
        if (mx - cen[0]) ** 2 + (my - cen[1]) ** 2 < \
           ((ax + bx) / 2 - cen[0]) ** 2 + ((ay + by) / 2 - cen[1]) ** 2:
            nx, ny = -nx, -ny
        quad = [(ax, ay), (bx, by), (bx + g * nx, by + g * ny),
                (ax + g * nx, ay + g * ny)]
        solids.append(prism2d(quad, z0, z1))
        solids.append(cyl(ax, ay, g, z0, z1))
    return fuse_all(solids)


ko = None
for side in ("left", "right"):
    for poly in CAPS_J[side]["cap_polys"]:
        k = cap_keepout(poly, 1.30, 10.5, 22.5)
        ko = k if ko is None else ko.fuse(k)
report("shelf x cap keep-outs (1.30)",
       vol(parts["north-shelf"].intersect(ko)))

# end-face clearance: min distance from the shelf to the cap
# solids (unpressed), global and to the two outermost caps
from OCP.BRepExtrema import BRepExtrema_DistShapeShape


def min_dist(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value()


caps_u = CAPS["caps-unpressed"]
print(f"  min dist shelf <-> all caps (unpressed): "
      f"{min_dist(parts['north-shelf'], caps_u):.3f}")
for side in ("left", "right"):
    outer = max(CAPS_J[side]["cap_polys"],
                key=lambda p: max(abs(q[0]) for q in p))
    pts2 = [bd.Vector(p[0], p[1], 0) for p in outer]
    w = bd.Wire.make_polygon(pts2 + [pts2[0]])
    oc = bd.extrude(bd.Face(w), 22.00 - 10.90).moved(
        bd.Location((0, 0, 10.90)))
    print(f"  min dist shelf <-> outermost {side} cap: "
          f"{min_dist(parts['north-shelf'], oc):.3f}")
# band restoration: the abolished stem slot through the right
# plateau (X 76.2..87.8, Y -62.2..-59.8, Z 10.5..22.5) was a
# through-hole in the hinge round; it must be solid band now
report("shelf material in old stem-slot box (expect ~300)",
       vol(parts["north-shelf"].intersect(
           box(76.2, 87.8, -62.2, -59.8, 10.5, 22.5))))
report("tray-right in old pocket box (75..89, -63.3..-58.7, "
       "9.25..10.0) (expect ~48.3 = filled)",
       vol(parts["tray-right"].intersect(
           box(75, 89, -63.3, -58.7, 9.25, 10.0))))

print("== invariants ==")
allb = [parts[n].bounding_box() for n in names]
x0 = min(b.min.X for b in allb); x1 = max(b.max.X for b in allb)
y0 = min(b.min.Y for b in allb); y1 = max(b.max.Y for b in allb)
z1 = max(b.max.Z for b in allb)
print(f"  outline X {x1 - x0:.2f}  Y {y1 - y0:.2f}  Z max {z1:.2f}")
probe = shelf.intersect(box(-160, 160, -70, -64.365, -3, 23))
print(f"  shelf material north of Y -64.365: {vol(probe):.4f}")
print("done")
