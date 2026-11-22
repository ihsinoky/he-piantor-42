"""Issue #296 trackpad LAP round verification.

Base suite as verify_padcover (pairwise, internals, plunger,
caps, hinge sweep, fixing at the NEW r26.7 points, connector
zone, invariants) plus lap-specific checks:
- levelling audit: shell above 10.90 in the annulus
  r22.3..24.6 (plunger disc excluded) = 0.000
- rabbet audit: shell above 10.31 in the annulus r24.6..28.0
  (Y <= 69, plunger disc excluded) = 0.000; rabbet floor
  present (shell material at the floor level)
- through-path ray test: at 24 azimuths x 4 height bands in
  Z 10.32..10.88, a radial probe (r23..31) must be blocked by
  cover or shell somewhere along its length (free volume <
  full probe volume) — run nominal and at tolerance corners
  (cover shifted +-0.20 X, lifted +0.20)
- tolerance corners: cover shifted +-0.20 in X and Y ->
  cover x shell = 0.000 (no interference)
- south slot: the cover's clipped face reaches the field
  level (cover material in the face slab down to <= 10.92)
- plunger rest surface: shell cap at 10.90 under the plunger
  head intact
"""
import build123d as bd
import json
import math

ASM = "./asm3d"
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
ZC = 2.65
AX_Y, AX_Z = -0.57, 19.30
PAD = (0.0, 48.0)
PLUN = (-15.5, 64.50)
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


def cut_all(s, cs):
    for c in cs:
        s = s.cut(c)
    return s


def report(label, v):
    print(f"  {label:52s} {v:12.4f} mm3")
    return v


from OCP.BRepExtrema import BRepExtrema_DistShapeShape


def min_dist(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return d.Value()


parts = {n: load(n) for n in
         ("tray-left", "tray-right", "centre-infill", "shell-central",
          "north-shelf", "plate-left", "plate-right", "plunger-sw1",
          "light-pipe-dled", "latch-slider", "trackpad-cover")}
names = list(parts)
cover = parts["trackpad-cover"]
shell = parts["shell-central"]
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
FLY_C = json.load(open(f"{ASM}/params.json"))["fly_centre"]
FLYMOVE = (FLY_C[0], FLY_C[1] + 50.14)
fly_real = fuse_all([g17(e["name"]) for e in idx
                     if e["name"].startswith("Fly-official")])
fly_real = fly_real.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
plug_real = fuse_all([g17(n) for n in ("USB-reference-shell",
                                       "USB-reference-overmold",
                                       "USB-reference-cable-exit")])
plug_real = plug_real.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
pb = box(-26.25, 26.25, -62.37, -4.37, -0.65, 0.15)
for (sx0, sx1, fy0, fy1) in [(-22.50, -6.50, -8.87, -6.22),
                             (6.50, 22.50, -8.87, -6.22),
                             (-8.5, 8.5, -62.52, -59.87)]:
    pb = pb.cut(box(sx0, sx1, fy0, fy1, -1.0, 0.5))
pb_parts = fuse_all([pb, box(-3, 3, -7.3, -4.37, 0.15, 3.05),
                     box(-20, -16.8, -6.0, -4.4, 0.15, 1.15)])
module = cyl(PAD[0], PAD[1], 20.0, 11.20, 12.70)
track44 = cyl(PAD[0], PAD[1], 22.0, 11.10, 12.60)
internals = {"main": main, "wings": WING, "power board": pb_parts,
             "fly-real": fly_real, "usb-plug-real": plug_real,
             "module40": module}
print("== closed: case vs internals ==")
for pn in names:
    for iname, s in internals.items():
        report(f"{pn} x {iname}", vol(parts[pn].intersect(s)))
report("cover x legacy Ø44 envelope (by design: fills the gap)",
       vol(cover.intersect(track44)))

print("== cover-specific ==")
report("cover x module40", vol(cover.intersect(module)))
plunger = parts["plunger-sw1"]
report("cover x plunger (rest)", vol(cover.intersect(plunger)))
pressed = plunger.moved(bd.Location((0, 0, -1.0)))
report("cover x plunger (pressed -1.0)", vol(cover.intersect(pressed)))
print(f"  min dist cover <-> plunger: {min_dist(cover, plunger):.3f}")

CAPS_J = json.load(open("./caps.json"))


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


def cap_solids(z1):
    ss = []
    for side in ("left", "right"):
        for poly in CAPS_J[side]["cap_polys"]:
            ss.append(prism2d([(p[0], p[1]) for p in poly], 10.90, z1))
    return fuse_all(ss)


for nm, z1 in (("caps-unpressed", 22.00), ("caps-pressed", 19.00)):
    cs = cap_solids(z1)
    report(f"cover x {nm}", vol(cover.intersect(cs)))
    print(f"  min dist cover <-> {nm}: {min_dist(cover, cs):.3f}")

sensing = cyl(PAD[0], PAD[1], 19.0, 12.0, 12.70)
report("cover x sensing disc Ø38 (must be 0 = fully exposed)",
       vol(cover.intersect(sensing)))
cbb = cover.bounding_box()
print(f"  cover bbox X {cbb.min.X:.2f}..{cbb.max.X:.2f}  "
      f"Y {cbb.min.Y:.2f}..{cbb.max.Y:.2f}  "
      f"Z {cbb.min.Z:.2f}..{cbb.max.Z:.2f}  vol {cover.volume:.1f}")
report("cover x shell (face contacts only, expect 0.000)",
       vol(cover.intersect(shell)))
print(f"  min dist cover <-> shell: {min_dist(cover, shell):.3f}")

print("== lap audits ==")
annulus_level = cut_all(cyl(PAD[0], PAD[1], 24.6, 10.90, 30.0),
                        [cyl(PAD[0], PAD[1], 22.3, 10.90, 30.0),
                         cyl(PLUN[0], PLUN[1], 3.2, 10.90, 30.0)])
report("shell above 10.90 in annulus r22.3..24.6 (excl plunger)",
       vol(shell.intersect(annulus_level)))
annulus_rabbet = cut_all(cyl(PAD[0], PAD[1], 28.0, 10.31, 30.0),
                         [cyl(PAD[0], PAD[1], 24.6, 10.31, 30.0),
                          cyl(PLUN[0], PLUN[1], 3.2, 10.31, 30.0)])
annulus_rabbet = fuse_all(cells_of(annulus_rabbet.intersect(
    box(-40, 40, 0.0, 69.0, 10.31, 30.0))))
report("shell above 10.31 in rabbet r24.6..28.0 (excl plunger)",
       vol(shell.intersect(annulus_rabbet)))
floor_probe = cut_all(cyl(PAD[0], PAD[1], 27.0, 10.20, 10.29),
                      [cyl(PAD[0], PAD[1], 26.0, 10.20, 10.29)])
report("shell material at rabbet floor level r26..27 (>0)",
       vol(shell.intersect(floor_probe)))
report("plunger rest cap: shell in cyl r2.0 @10.89..10.91 (>0)",
       vol(shell.intersect(cyl(PLUN[0], PLUN[1], 2.0, 10.89, 10.91))))
face_slab = cover.intersect(box(-12, 12, 68.90, 69.0, 10.90, 11.35))
report("cover material in south face slab Z10.90..11.35 (>0)",
       vol(face_slab))
face_cells = cells_of(cover.intersect(box(-12, 12, 68.95, 69.0,
                                          10.0, 12.0)))
fmin = min((c.bounding_box().min.Z for c in face_cells), default=None)
print(f"  cover min Z at the south face (expect <= 10.92): {fmin}")


def ray_test(cov, label):
    """Radial probes r23.5..29.5 (across the joint), width
    0.2, 4 Z bands in 10.32..10.88, azimuths every 15 deg
    EXCLUDING the south clip sector 60..120 deg (the flange
    is clipped away there; that joint is the apron/face,
    checked separately): a through-path exists iff some probe
    is entirely free of cover+shell."""
    worst_ratio = 0.0
    worst_at = None
    for k in range(24):
        ang = k * 15.0
        if 60.0 <= ang <= 120.0:
            continue
        for (z0, z1) in [(10.32, 10.46), (10.46, 10.60),
                         (10.60, 10.74), (10.74, 10.88)]:
            pr = box(23.5, 29.5, -0.1, 0.1, z0, z1)
            loc = (bd.Location((PAD[0], PAD[1], 0))
                   * bd.Location((0, 0, 0), (0, 0, ang)))
            pr = pr.moved(loc)
            free = vol(cut_all(pr, [cov, shell]))
            ratio = free / pr.volume
            if ratio > worst_ratio:
                worst_ratio, worst_at = ratio, (ang, z0)
    print(f"  through-path ray test [{label}]: worst free ratio "
          f"{worst_ratio:.3f} at {worst_at} (1.000 = open path)")
    return worst_ratio


print("== through-path / tolerance corners ==")
ray_test(cover, "nominal")
for (dx, dy, dz, lab) in [(0.20, 0, 0, "cover +0.20 X"),
                          (-0.20, 0, 0, "cover -0.20 X"),
                          (0, 0.20, 0, "cover +0.20 Y"),
                          (0, -0.20, 0, "cover -0.20 Y"),
                          (0, 0, 0.20, "cover +0.20 Z lift")]:
    cov2 = cover.moved(bd.Location((dx, dy, dz)))
    report(f"{lab}: cover x shell (interference)",
           vol(cov2.intersect(shell)))
    if dz == 0 and (dx or dy):
        ray_test(cov2, lab)
    if dz:
        ray_test(cov2, lab)

print("== hinge arc sweep vs cover ==")
shelf = parts["north-shelf"]
slider_entry = parts["latch-slider"].moved(bd.Location((3.8, 0, 0)))
shelf_asm = shelf.fuse(slider_entry)


def rot(s, deg):
    loc = (bd.Location((0, AX_Y, AX_Z))
           * bd.Location((0, 0, 0), (-deg, 0, 0))
           * bd.Location((0, -AX_Y, -AX_Z)))
    return s.moved(loc)


worst = 0.0
for deg in [i * 2.5 for i in range(41)]:
    if deg == 0:
        continue
    v = vol(rot(shelf_asm, deg).intersect(cover))
    worst = max(worst, v)
    if v > 0.0005:
        print(f"  {deg:6.1f} deg  shelf x cover {v:10.3f}")
print(f"  arc sweep worst (shelf+slider vs cover): {worst:.4f}")

print("== fixing (modelled M2 screws, r26.7) ==")
SCREW_PTS = []
for _a in (30, 150, 210, 330):
    _t = math.radians(_a)
    SCREW_PTS.append((PAD[0] + 26.7 * math.cos(_t),
                      PAD[1] + 26.7 * math.sin(_t)))
for (sx, sy) in SCREW_PTS:
    head = bd.Solid.make_cone(1.0, 1.7, 0.7,
                              bd.Plane(origin=(sx, sy, 11.20)))
    shank = cyl(sx, sy, 1.0, 7.60, 11.20)
    screw = head.fuse(shank)
    eng = vol(shank.intersect(shell))
    print(f"  screw @({sx:.2f},{sy:.2f}): shank x shell (engagement) "
          f"{eng:.3f}; screw x main {vol(screw.intersect(main)):.3f}; "
          f"x module {vol(screw.intersect(module)):.3f}; "
          f"x plunger {vol(screw.intersect(plunger)):.3f}; "
          f"x cover {vol(screw.intersect(cover)):.3f}")
    boss = cyl(sx, sy, 3.0, 7.30, 9.60)
    bossmat = vol(boss.intersect(shell)) - \
        vol(cyl(sx, sy, 0.8, 7.0, 11.2).intersect(boss))
    print(f"    boss material in shell (boss cyl minus pilot): "
          f"{bossmat:.3f}")

print("== connector zone / trim audits ==")
zone = box(-3.0, 3.0, 26.0, 30.0, 0.0, 11.0)
report("cover x connector-zone box", vol(cover.intersect(zone)))
for (sx, sy) in SCREW_PTS:
    report(f"boss cyl @({sx:.1f},{sy:.1f}) x connector-zone box",
           vol(cyl(sx, sy, 3.0, 7.30, 9.60).intersect(zone)))
report("shell above 11.25 within r25.6 of pad (trim audit)",
       vol(shell.intersect(cyl(PAD[0], PAD[1], 25.6, 11.25, 30.0))))

print("== invariants ==")
allb = [parts[n].bounding_box() for n in names]
x0 = min(b.min.X for b in allb); x1 = max(b.max.X for b in allb)
y0 = min(b.min.Y for b in allb); y1 = max(b.max.Y for b in allb)
z1 = max(b.max.Z for b in allb)
print(f"  outline X {x1 - x0:.2f}  Y {y1 - y0:.2f}  Z max {z1:.2f}")
shelf_p = parts["north-shelf"]
probe = shelf_p.intersect(box(-160, 160, -70, -64.365, -3, 23))
print(f"  shelf material north of Y -64.365: {vol(probe):.4f}")
print("done")
