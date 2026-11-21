"""Issue #296 north-flush + PO-profile revision — verification.
A. north face flatness (assembly, per 2mm column)
B. outline / band top / cover top
C. keycap clearance (solids, unpressed + pressed) + built south-edge audit
D. lid lift path
E. Fly mouth flush + Fly/plug vs band plateau
F. shell centre profile (slope) audit
G. SW1 plunger / DLED pipe re-trim audit
H. old-strip disposition (what was removed, where)
"""
import build123d as bd
import json, os, math

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))
ZC = 2.65
FLUSH_Y = -64.37

def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -ZC)))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

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

def slab(s, b):
    r = s.intersect(b)
    if r is None:
        return []
    return [x for x in (list(r) if isinstance(r, (list, bd.ShapeList)) else [r])
            if hasattr(x, "volume") and x.volume > 1e-6]

tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
shell, strip_l, strip_r = part("shell-central"), part("strip-left"), part("strip-right")
plate_l, plate_r = part("plate-left"), part("plate-right")
cover = part("battery-cover")
plunger, pipe = part("plunger-sw1"), part("light-pipe-dled")
case_all = fuse_all([tray_l, tray_r, infill, shell, strip_l, strip_r,
                     plate_l, plate_r, cover, plunger, pipe])
case_nocover = fuse_all([tray_l, tray_r, infill, shell, strip_l, strip_r,
                         plate_l, plate_r])

print("== A. north face flatness (fused north parts) ==")
north_asm = fuse_all([tray_l, tray_r, infill, strip_l, strip_r, cover])
worst = 0.0
for xi in range(-117, 117, 2):
    cells = slab(north_asm, box(xi, xi + 2, -70, -60, -2.65, 22.0))
    if cells:
        ymin = min(c.bounding_box().min.Y for c in cells)
        worst = max(worst, abs(ymin - FLUSH_Y))
print(f"max |Ymin - (-64.37)| over |X|<=117 columns: {worst:.3f} mm")
print("end columns (angled end edge, informational):")
for xi in (118, 124, 130, 140, 150, -120, -126, -132, -142, -152):
    cells = slab(north_asm, box(xi, xi + 2, -70, -60, -2.65, 22.0))
    if cells:
        ymin = min(c.bounding_box().min.Y for c in cells)
        print(f"  X {xi}..{xi+2}: Ymin {ymin:.2f}")

print("\n== B. outline / tops ==")
bb = case_all.bounding_box()
print(f"assembly bbox X {bb.min.X:.2f}..{bb.max.X:.2f} (W {bb.max.X-bb.min.X:.2f})"
      f"  Y {bb.min.Y:.2f}..{bb.max.Y:.2f} (D {bb.max.Y-bb.min.Y:.2f})"
      f"  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
print(f"cover bbox Zmax {cover.bounding_box().max.Z:.2f} (lid top, expect 22.00)")
for nm, st in (("strip-right", strip_r), ("strip-left", strip_l)):
    zs = []
    for xi in (35, 60, 90, 120):
        cells = slab(st, box(xi if nm.endswith("right") else -xi - 2,
                             xi + 2 if nm.endswith("right") else -xi,
                             -70, 0, 10.9, 22.5))
        if cells:
            zs.append(max(c.bounding_box().max.Z for c in cells))
    print(f"{nm} band top at sample columns: {[round(z, 2) for z in zs]} (expect 22.00)")

print("\n== C. keycap clearance ==")
CAPS = json.load(open(os.path.join(RT, "caps.json")))
def cap_solids(z1):
    ss = []
    for side in ("left", "right"):
        for poly in CAPS[side]["cap_polys"]:
            pts = [bd.Vector(p[0], p[1], 0) for p in poly]
            w = bd.Wire.make_polygon(pts + [pts[0]])
            f = bd.Face(w)
            s = bd.extrude(f, z1 - 10.90)
            ss.append(s.moved(bd.Location((0, 0, 10.90))))
    return fuse_all(ss)
for label, z1 in (("unpressed (top 22.00)", 22.00), ("pressed model (top 19.00)", 19.00)):
    caps = cap_solids(z1)
    print(f"caps {label}: vs case {inter_vol(case_all, caps):.3f} mm3 (expect 0.000)")
# built south-edge audit from strip south faces (normal +Y)
for nm, st, side in (("strip-right", strip_r, "right"), ("strip-left", strip_l, "left")):
    caps = CAPS[side]["capline"]
    faces = []
    for f in st.faces():
        n = f.normal_at()
        if abs(n.Y - 1) < 1e-6 and abs(n.X) < 1e-6 and abs(n.Z) < 1e-6:
            fb = f.bounding_box()
            if fb.min.Z > 21.0:   # full-height south faces only (the cliff)
                faces.append((fb.min.X, fb.max.X, fb.min.Y))
    worst = 99.0
    for (fx0, fx1, fy) in faces:
        ks = [int(k) for k in caps if fx0 - 0.01 <= int(k) <= fx1 + 0.01]
        if ks:
            cl = min(caps[str(k)] for k in ks)
            worst = min(worst, cl - fy)
    print(f"{nm}: south faces {len(faces)}, min clearance to capline {worst:.2f} mm (design 1.00)")

print("\n== D. lid lift path ==")
for dz in (2.0, 5.0, 10.0, 25.0):
    lifted = cover.moved(bd.Location((0, 0, dz)))
    print(f"lid +{dz:4.1f} Z vs rest of case: {inter_vol(case_nocover, lifted):.3f} mm3")

print("\n== E. Fly / plug vs band ==")
FLY_C = json.load(open(f"{ASM}/params.json"))["fly_centre"]
FLYMOVE = (FLY_C[0], FLY_C[1] + 50.14)
fly = None
for e in idx:
    if e["name"].startswith("Fly-official"):
        s = g17(e["name"])
        fly = s if fly is None else fly.fuse(s)
fly = fly.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
fbb = fly.bounding_box()
print(f"Fly bbox Y {fbb.min.Y:.2f}..{fbb.max.Y:.2f}  Z {fbb.min.Z:.2f}..{fbb.max.Z:.2f}"
      f"  -> mouth protrusion vs face: {FLUSH_Y - fbb.min.Y:+.2f} mm (0.00 = flush)")
print(f"Fly vs strip-right (band): {inter_vol(strip_r, fly):.3f} mm3")
plug = None
for n in ("USB-reference-shell", "USB-reference-overmold", "USB-reference-cable-exit"):
    s = g17(n)
    plug = s if plug is None else plug.fuse(s)
plug2 = plug.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
print(f"plug vs strip-right (band): {inter_vol(strip_r, plug2):.3f} mm3")
print(f"plug vs tray-right: {inter_vol(tray_r, plug2):.3f} mm3")
print(f"plug vs plate-right: {inter_vol(plate_r, plug2):.3f} mm3")

print("\n== F. shell centre profile audit (X -1..1 slab) ==")
def profile_z(y):
    if y <= -0.37:
        return 22.00
    if y >= 20.0:
        return 10.90
    return 22.00 - (y + 0.37) * (11.10 / 20.37)
for y0 in range(0, 22, 2):
    cells = slab(shell, box(-1, 1, y0, y0 + 2, 0, 23))
    if cells:
        zm = max(c.bounding_box().max.Z for c in cells)
        print(f"  Y {y0}..{y0+2}: shell top {zm:.2f}  (profile at band north edge "
              f"{profile_z(y0):.2f})")
cells = slab(shell, box(19, 21, 20, 35, 0, 23))
if cells:
    print(f"  X~20, Y 20..35: shell top {max(c.bounding_box().max.Z for c in cells):.2f}"
          f"  (expect 10.90, outside island)")

print("\n== G. plunger / pipe audit ==")
print(f"plunger vs shell: {inter_vol(shell, plunger):.3f} mm3 (expect 0.000)")
cells = slab(shell, box(-16.5, -14.5, 63.5, 65.5, 0, 23))
if cells:
    print(f"shell top at SW1 column: {max(c.bounding_box().max.Z for c in cells):.2f}"
          f"  (expect 10.90; plunger head bottom 10.90, top "
          f"{plunger.bounding_box().max.Z:.2f})")
print(f"pipe vs shell: {inter_vol(shell, pipe):.3f} mm3 (expect 0.000)")
print(f"pipe top {pipe.bounding_box().max.Z:.2f} (slope profile at Y=13: "
      f"{profile_z(13):.2f})")

print("\n== H. old-strip disposition ==")
G17S = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
for sgn, nm in ((+1, "right"), (-1, "left")):
    old = g17(f"strip-{nm}", 9.5 * sgn)
    old = old.cut(box(-30.25, 30.25, -64.37, -0.37, 0.0, 30.0))
    new = strip_r if sgn > 0 else strip_l
    kept = inter_vol(old, fuse_all([new, shell]))
    print(f"strip-{nm}: old vol {old.volume/1000:.2f}k, inside new strip+shell "
          f"{kept/1000:.2f}k, removed {(old.volume-kept)/1000:.2f}k")
