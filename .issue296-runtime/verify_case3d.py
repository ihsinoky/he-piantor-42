"""Issue #296 Stage 3D — verification of the built case.
Assembly interference at delta=9.5 poses, cell-removal envelope
re-check (zcheck method), power-board insertion path, outline scans.
Numbers come from the solids only.
"""
import build123d as bd
import json, os, math

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
ZC = 2.65
# Fly pose: build writes the centre to asm3d/params.json; the g17
# record centre is (0, -50.14), so the move is centre - record.
FLY_C = json.load(open(f"{ASM}/params.json"))["fly_centre"]
FLYMOVE = (FLY_C[0], FLY_C[1] + 50.14)

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

# ------------------------------------------------------------ case parts
tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
shell, strip_l, strip_r = part("shell-central"), part("strip-left"), part("strip-right")
plate_l, plate_r = part("plate-left"), part("plate-right")
cover = part("battery-cover")
case_all = fuse_all([tray_l, tray_r, infill, shell, strip_l, strip_r,
                     plate_l, plate_r, cover])
case_nocover = fuse_all([tray_l, tray_r, infill, shell, strip_l, strip_r,
                         plate_l, plate_r])

# ------------------------------------------------------------ internals
# Main: D-063 outline extruded (board Z 4.70..5.90)
segs = json.load(open(os.path.join(os.path.dirname(__file__),
                                   "main-outline-asm.json")))
pts = [tuple(segs[0][0]), tuple(segs[0][1])]
rest = [tuple(map(tuple, s)) for s in segs[1:]]
while rest:
    for i, (a, b) in enumerate(rest):
        if a == pts[-1]:
            pts.append(b); rest.pop(i); break
        if b == pts[-1]:
            pts.append(a); rest.pop(i); break
    else:
        break
edges = [bd.Edge.make_line(bd.Vector(*pts[i], 0), bd.Vector(*pts[i + 1], 0))
         for i in range(len(pts) - 1)]
wire = bd.Wire(edges)
face = bd.Face(wire)
_s = bd.extrude(face, 1.2)
if _s.bounding_box().max.Z < 0.6:
    _s = bd.extrude(face, -1.2)
main = _s.moved(bd.Location((0, 0, 4.70 - _s.bounding_box().min.Z)))
_mb = main.bounding_box()
print(f"Main (D-063 outline) vol k: {round(main.volume / 1000, 2)}"
      f"  Z {_mb.min.Z:.2f}..{_mb.max.Z:.2f}")

wing_l, wing_r = g17("wing_left", -9.5), g17("wing_right", 9.5)
und_l = fuse_all([g17(e["name"], -9.5) for e in idx
                  if e["name"].startswith("underside-left")])
und_r = fuse_all([g17(e["name"], 9.5) for e in idx
                  if e["name"].startswith("underside-right")])
wings = fuse_all([wing_l, wing_r, und_l, und_r])
swenv = fuse_all([g17(e["name"], -9.5 if "-L_" in e["name"] else 9.5)
                  for e in idx if e["name"].startswith("switch-envelope")])

def aa_cell(cx):
    c = bd.Solid.make_cylinder(7.25, 50.5,
                               bd.Plane(origin=(cx, -59.62, 7.40),
                                        z_dir=(0, 1, 0)))
    return c
cells = fuse_all([aa_cell(-15), aa_cell(0), aa_cell(15)])

# power board with fin slots (Stage-2 input geometry)
pb = box(-26.25, 26.25, -62.37, -4.37, -0.65, 0.15)
for (sx0, sx1, fy0, fy1) in [(-22.50, -6.50, -8.87, -6.22),
                             (6.50, 22.50, -8.87, -6.22),
                             (-8.5, 8.5, -62.52, -59.87)]:
    pb = pb.cut(box(sx0, sx1, fy0, fy1, -1.0, 0.5))
pb_parts = fuse_all([pb,
                     box(-3, 3, -7.3, -4.37, 0.15, 3.05),       # J1 GH envelope (relocated band)
                     box(-20, -16.8, -6.0, -4.4, 0.15, 1.15)])  # F1 envelope (clear of slot)
# slide-switch envelope on the bay SOUTH wall inner face, centred X 0
# (Stage B's E-wall site is under the Wing tab; see case-3d.md).
# Body on the pad face (Y -3.37), extending north; floats above J1.
switch_env = box(-4.25, 4.25, -6.87, -3.37, 3.40, 7.40)
fly = None
for e in idx:
    if e["name"].startswith("Fly-official"):
        s = g17(e["name"])
        fly = s if fly is None else fly.fuse(s)
fly = fly.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))   # centre per asm3d/params.json
trackpad = bd.Solid.make_cylinder(22, 1.5, bd.Plane(origin=(0, 48, 11.20)))

internals = {"Main": main, "Wings+underside": wings, "cells": cells,
             "power board": pb_parts, "Fly": fly, "trackpad": trackpad,
             "switch envelopes": swenv, "slide switch env": switch_env}

print("\n== A. case (with cover) vs internals ==")
for n, s in internals.items():
    print(f"cover+case vs {n:18s}: {inter_vol(case_all, s):10.2f} mm3")
print("\n== B. per-part detail (nonzero only) ==")
case_parts = {"tray-left": tray_l, "tray-right": tray_r, "infill": infill,
              "shell": shell, "strip-left": strip_l, "strip-right": strip_r,
              "plate-left": plate_l, "plate-right": plate_r, "cover": cover}
for cn, cs in case_parts.items():
    for n, s in internals.items():
        v = inter_vol(cs, s)
        if v > 0.01:
            print(f"{cn:12s} vs {n:18s}: {v:10.2f} mm3")
print("\n== C. case vs case ==")
names = list(case_parts)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        v = inter_vol(case_parts[names[i]], case_parts[names[j]])
        if v > 0.01:
            print(f"{names[i]:12s} vs {names[j]:12s}: {v:10.2f} mm3")

print("\n== D. outline scans ==")
asm = fuse_all([tray_l, tray_r, infill])
for X in range(-50, 52, 10):
    col = asm.intersect(box(X - 2, X + 2, 40, 90, -2.65, 11.0))
    ss = [s for s in col] if isinstance(col, (list, bd.ShapeList)) else [col]
    ymax = max(s.bounding_box().max.Y for s in ss) if ss else None
    print(f"south Ymax at X {X}: {ymax}")
bb = case_all.bounding_box()
print(f"assembly bbox X {bb.min.X:.2f}..{bb.max.X:.2f} (W {bb.max.X-bb.min.X:.2f})"
      f"  Y {bb.min.Y:.2f}..{bb.max.Y:.2f} (D {bb.max.Y-bb.min.Y:.2f})"
      f"  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")

print("\n== E. removal envelope (cover off) ==")
def cell_sweep(cx, spring):  # spring: 'S' or 'N'
    cell = aa_cell(cx)
    if spring == 'S':
        cell = cell.moved(bd.Location((0, 2.0, 0)))
        piv = bd.Vector(cx, -8.37, 7.40)
        free = bd.Vector(cx, -57.62, 7.40)   # free (north) end centre
    else:
        cell = cell.moved(bd.Location((0, -2.0, 0)))
        piv = bd.Vector(cx, -60.37, 7.40)
        free = bd.Vector(cx, -11.12, 7.40)   # free (south) end centre
    swept = cell
    for k in range(1, 8):
        th = 5.0 * k
        # tip the free end UP: choose the rotation sign by the free-end
        # centre's height after rotation (bbox test was unreliable)
        best = None
        for sgn in (+1, -1):
            loc = bd.Location((piv.X, piv.Y, piv.Z)) * \
                bd.Location((0, 0, 0), (1, 0, 0), sgn * th) * \
                bd.Location((-piv.X, -piv.Y, -piv.Z))
            fz = free.moved(loc).Z if hasattr(free, "moved") else None
            cand = cell.moved(loc)
            # free-end centre height from the moved copy's far end:
            bb = cand.bounding_box()
            score = bb.max.Z
            if best is None or score > best[0]:
                best = (score, cand)
        swept = swept.fuse(best[1])
    return swept

fin_boxes = {"W": box(-22.00, -7.00, -8.37, -6.72, -0.65, 10.5),
             "M": box(-8, 8, -62.02, -60.37, -0.65, 10.5),
             "E": box(7.00, 22.00, -8.37, -6.72, -0.65, 10.5)}
for cx, spring, fk in [(-15, 'S', "W"), (0, 'N', "M"), (15, 'S', "E")]:
    sw = cell_sweep(cx, spring)
    v_case = inter_vol(case_nocover, sw)
    v_wing = inter_vol(wings, sw)
    v_fin = inter_vol(fin_boxes[fk], sw)
    v_sw = inter_vol(switch_env, sw)
    print(f"cell cx {cx:+3d} ({spring} spring): sweep vs case {v_case:9.3f}"
          f"  vs wings {v_wing:9.3f}  (of which own-fin box {v_fin:9.3f})"
          f"  vs switch env {v_sw:9.3f}")
for sgn, nm in ((+1, "east"), (-1, "west")):
    zone = box(22.50, 32.25, -59.62, -9.12, 7.40, 16.65) if sgn > 0 else \
        box(-32.25, -22.50, -59.62, -9.12, 7.40, 16.65)
    print(f"finger zone {nm}: vs case(no cover) {inter_vol(case_nocover, zone):9.3f}"
          f"  vs wings {inter_vol(wings, zone):9.3f}")
    zone_in = box(22.50, 30.25, -59.62, -9.12, 7.40, 16.65) if sgn > 0 else \
        box(-30.25, -22.50, -59.62, -9.12, 7.40, 16.65)
    print(f"finger zone {nm} (to X 30.25): vs case {inter_vol(case_nocover, zone_in):9.3f}")

print("\n== F. power-board insertion (vertical drop, wings NOT seated) ==")
drop = pb_parts
swept = drop
z = 0.25
while z <= 12.01:
    swept = swept.fuse(drop.moved(bd.Location((0, 0, z))))
    z += 0.25 if z < 2.0 else 1.0
case_pre = fuse_all([tray_l, tray_r, infill])   # case furniture before wings/plates
v = inter_vol(case_pre, swept)
print(f"drop sweep vs trays+infill: {v:.3f} mm3 (tongue snap overlap expected)")
tongues = fuse_all([box(25.75, 28.25, -53, -47, 0.15, 1.15),
                    box(25.75, 28.25, -23, -17, 0.15, 1.15),
                    box(-28.25, -25.75, -53, -47, 0.15, 1.15),
                    box(-28.25, -25.75, -23, -17, 0.15, 1.15)])
print(f"drop sweep vs tongue boxes only: {inter_vol(tongues, swept):.3f} mm3")

print("\n== G. trackpad island probe ==")
col = shell.intersect(box(-22, 22, 26, 70, 0, 25))
ss = [s for s in col] if isinstance(col, (list, bd.ShapeList)) else [col]
print("shell island region vol k:", round(sum(s.volume for s in ss) / 1000, 2))
print("shell vs trackpad disc:", round(inter_vol(shell, trackpad), 2))
print("\n== H. USB plug check ==")
plug = None
for n in ("USB-reference-shell", "USB-reference-overmold", "USB-reference-cable-exit"):
    s = g17(n)
    plug = s if plug is None else plug.fuse(s)
pbb = plug.bounding_box()
print(f"plug g17 bbox X {pbb.min.X:.2f}..{pbb.max.X:.2f} Y {pbb.min.Y:.2f}..{pbb.max.Y:.2f}"
      f" Z(case) {pbb.min.Z:.2f}..{pbb.max.Z:.2f}")
plug2 = plug.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
print(f"plug at new pose vs tray-right: {inter_vol(tray_r, plug2):.3f} mm3")
print(f"plug at new pose vs plate-right: {inter_vol(plate_r, plug2):.3f} mm3")
print(f"Fly vs tray-right (pocket): {inter_vol(tray_r, fly):.3f} mm3")
print(f"Fly vs plate-right: {inter_vol(plate_r, fly):.3f} mm3")
print(f"Fly vs wings: {inter_vol(wings, fly):.3f} mm3")
fbb = fly.bounding_box()
print(f"Fly at new pose bbox: X {fbb.min.X:.2f}..{fbb.max.X:.2f} Y {fbb.min.Y:.2f}..{fbb.max.Y:.2f}"
      f" Z {fbb.min.Z:.2f}..{fbb.max.Z:.2f}")
