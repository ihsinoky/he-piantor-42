"""Issue #296 — lid-integral north shelf verification.
A. shelf identity (single solid; diff vs the old 3-part union)
B. fixing (pilots landed, holes/countersinks empty, head envelope,
   driver access)
C. bridge clearances over the bay E/W sills
D. shelf removal trajectory (pure +Z lift)
E. battery removal sweeps with the shelf OFF
F. full interference table (shelf on) + outline + north flatness
G. Fly / USB with shelf on and off
H. power-board drop re-check (tray pilots changed)
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

def slabs(s, b):
    r = s.intersect(b)
    if r is None:
        return []
    return [x for x in (list(r) if isinstance(r, (list, bd.ShapeList)) else [r])
            if hasattr(x, "volume") and x.volume > 1e-6]

# ------------------------------------------------------------ parts
tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
shell = part("shell-central")
shelf = part("north-shelf")
plate_l, plate_r = part("plate-left"), part("plate-right")
plunger, pipe = part("plunger-sw1"), part("light-pipe-dled")
case_all = fuse_all([tray_l, tray_r, infill, shell, shelf,
                     plate_l, plate_r, plunger, pipe])
case_noshelf = fuse_all([tray_l, tray_r, infill, shell,
                         plate_l, plate_r, plunger, pipe])
old_union = fuse_all([part("battery-cover"), part("strip-left"), part("strip-right")])

# ------------------------------------------------------------ internals
segs = json.load(open(os.path.join(RT, "main-outline-asm.json")))
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
_s = bd.extrude(bd.Face(bd.Wire(edges)), 1.2)
if _s.bounding_box().max.Z < 0.6:
    _s = bd.extrude(bd.Face(bd.Wire(edges)), -1.2)
main = _s.moved(bd.Location((0, 0, 4.70 - _s.bounding_box().min.Z)))

wing_l, wing_r = g17("wing_left", -9.5), g17("wing_right", 9.5)
und_l = fuse_all([g17(e["name"], -9.5) for e in idx
                  if e["name"].startswith("underside-left")])
und_r = fuse_all([g17(e["name"], 9.5) for e in idx
                  if e["name"].startswith("underside-right")])
wings = fuse_all([wing_l, wing_r, und_l, und_r])
wing_boards = fuse_all([wing_l, wing_r])
swenv = fuse_all([g17(e["name"], -9.5 if "-L_" in e["name"] else 9.5)
                  for e in idx if e["name"].startswith("switch-envelope")])

def aa_cell(cx):
    return bd.Solid.make_cylinder(7.25, 50.5,
                                  bd.Plane(origin=(cx, -59.62, 7.40),
                                           z_dir=(0, 1, 0)))
cells = fuse_all([aa_cell(-15), aa_cell(0), aa_cell(15)])
pb = box(-26.25, 26.25, -62.37, -4.37, -0.65, 0.15)
for (sx0, sx1, fy0, fy1) in [(-22.50, -6.50, -8.87, -6.22),
                             (6.50, 22.50, -8.87, -6.22),
                             (-8.5, 8.5, -62.52, -59.87)]:
    pb = pb.cut(box(sx0, sx1, fy0, fy1, -1.0, 0.5))
pb_parts = fuse_all([pb,
                     box(-3, 3, -7.3, -4.37, 0.15, 3.05),
                     box(-20, -16.8, -6.0, -4.4, 0.15, 1.15)])
switch_env = box(-4.25, 4.25, -6.87, -3.37, 3.40, 7.40)
fly = None
for e in idx:
    if e["name"].startswith("Fly-official"):
        s = g17(e["name"])
        fly = s if fly is None else fly.fuse(s)
fly = fly.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
trackpad = bd.Solid.make_cylinder(22, 1.5, bd.Plane(origin=(0, 48, 11.20)))
plug = None
for n in ("USB-reference-shell", "USB-reference-overmold", "USB-reference-cable-exit"):
    s = g17(n)
    plug = s if plug is None else plug.fuse(s)
plug = plug.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))

CAPS = json.load(open(os.path.join(RT, "caps.json")))
def cap_solids(z1):
    ss = []
    for side in ("left", "right"):
        for poly in CAPS[side]["cap_polys"]:
            pts2 = [bd.Vector(p[0], p[1], 0) for p in poly]
            w = bd.Wire.make_polygon(pts2 + [pts2[0]])
            s = bd.extrude(bd.Face(w), z1 - 10.90)
            ss.append(s.moved(bd.Location((0, 0, 10.90))))
    return fuse_all(ss)
caps_un = cap_solids(22.00)
caps_pr = cap_solids(19.00)

internals = {"Main": main, "Wings+underside": wings, "cells": cells,
             "power board": pb_parts, "Fly": fly, "trackpad": trackpad,
             "switch envelopes": swenv, "slide switch env": switch_env}

SCREWS = [(55, tray_r), (-55, tray_l), (85, tray_r), (-85, tray_l)]

print("== A. shelf identity ==")
ns = len(shelf.solids()) if hasattr(shelf, "solids") else "?"
print(f"shelf solids: {ns} (expect 1)")
bb = shelf.bounding_box()
print(f"shelf bbox X {bb.min.X:.2f}..{bb.max.X:.2f}  Y {bb.min.Y:.2f}..{bb.max.Y:.2f}"
      f"  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
print(f"shelf vol {shelf.volume / 1000:.2f}k   old 3-part union {old_union.volume / 1000:.2f}k")
print(f"old-union minus shelf: {inter_vol(old_union, shelf):.3f} mm3 is the overlap;"
      f" shelf inside old union by {shelf.volume - inter_vol(old_union, shelf):.3f} mm3"
      f" (shelf-minus-old, expect ~0)")
print(f"old-minus-shelf (the 4 screw holes + countersinks): "
      f"{old_union.volume - inter_vol(old_union, shelf):.3f} mm3")

print("\n== B. fixing ==")
for (X, tray) in SCREWS:
    pv = inter_vol(tray, cyl(X, -61.37, 1.35, 4.0, 10.9))
    hv = inter_vol(shelf, cyl(X, -61.37, 1.5, 10.9, 22.0))
    cv = inter_vol(shelf, bd.Solid.make_cone(1.5, 2.75, 1.25,
                                             bd.Plane(origin=(X, -61.37, 20.75))))
    print(f"screw X {X:+4d}: tray pilot void {pv:7.3f} (expect ~0 = hole cut),"
          f" shelf hole void {hv:7.3f}, countersink void {cv:7.3f}")
for (X, tray) in SCREWS:
    head = fuse_all([bd.Solid.make_cone(1.45, 2.70, 1.20,
                                         bd.Plane(origin=(X, -61.37, 20.80))),
                     cyl(X, -61.37, 1.45, 10.90, 20.80)])
    hb = head.bounding_box()
    print(f"head X {X:+4d}: top Z {hb.max.Z:.2f} (expect 22.00), north rim Y "
          f"{hb.min.Y:.2f} (face -64.37), vs shelf {inter_vol(shelf, head):.3f},"
          f" vs caps unpressed {inter_vol(caps_un, head):.3f},"
          f" vs caps pressed {inter_vol(caps_pr, head):.3f}")
    bit = cyl(X, -61.37, 3.175, 22.0, 55.0)
    side = "right" if X > 0 else "left"
    caps = CAPS[side]["capline"]
    ks = [int(k) for k in caps if abs(int(k) - abs(X)) <= 4]
    cl = min(caps[str(k)] for k in ks) if ks else float("nan")
    print(f"          driver bit O6.35 vs caps un {inter_vol(caps_un, bit):.3f},"
          f" pressed {inter_vol(caps_pr, bit):.3f}; capline near column {cl:.2f},"
          f" axis-to-capline {cl - (-61.37):.2f} mm")

print("\n== C. bridge clearances over the bay E/W sills ==")
for sgn, nm in ((+1, "E"), (-1, "W")):
    bx0, bx1 = (28.25, 30.25) if sgn > 0 else (-30.25, -28.25)
    band = box(bx0, bx1, -62.37, -0.37, 0.0, 30.0)
    sh = slabs(shelf, band)
    pl = slabs(fuse_all([plate_l, plate_r]), band)
    wb = slabs(wing_boards, band)
    if sh:
        print(f"{nm} band: shelf min Z {min(c.bounding_box().min.Z for c in sh):.2f}"
              f" (skirt bottom, expect 11.15)")
    if pl:
        print(f"        plate max Z {max(c.bounding_box().max.Z for c in pl):.2f}"
              f" (expect 10.90) -> skirt-to-plate clearance "
              f"{11.15 - max(c.bounding_box().max.Z for c in pl):.2f}")
    if wb:
        print(f"        wing board max Z {max(c.bounding_box().max.Z for c in wb):.2f}"
              f" (expect 5.90) -> skirt-to-board clearance "
              f"{11.15 - max(c.bounding_box().max.Z for c in wb):.2f}")
print(f"shelf vs Wings+underside (incl. J_WING envelopes): {inter_vol(shelf, wings):.3f} mm3")
print(f"shelf vs plates: {inter_vol(shelf, fuse_all([plate_l, plate_r])):.3f} mm3")

print("\n== D. shelf removal trajectory (pure +Z lift, screws removed) ==")
targets = {"rest of case": case_noshelf, "caps unpressed": caps_un,
           "caps pressed": caps_pr, "trackpad": trackpad, "Fly": fly,
           "plug": plug, "Wings+underside": wings, "Main": main,
           "cells": cells, "power board": pb_parts,
           "switch envelopes": swenv, "slide switch env": switch_env}
for dz in (2.0, 5.0, 10.0, 25.0):
    lifted = shelf.moved(bd.Location((0, 0, dz)))
    row = "  ".join(f"{n} {inter_vol(lifted, s):.3f}" for n, s in targets.items())
    print(f"+{dz:4.1f}: {row}")

print("\n== E. battery removal sweeps, shelf OFF ==")
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
            loc = bd.Location((piv.X, piv.Y, piv.Z)) * \
                bd.Location((0, 0, 0), (1, 0, 0), sgn * th) * \
                bd.Location((-piv.X, -piv.Y, -piv.Z))
            cand = cell.moved(loc)
            score = cand.bounding_box().max.Z
            if best is None or score > best[0]:
                best = (score, cand)
        swept = swept.fuse(best[1])
    return swept

fin_boxes = {"W": box(-22.00, -7.00, -8.37, -6.72, -0.65, 10.5),
             "M": box(-8, 8, -62.02, -60.37, -0.65, 10.5),
             "E": box(7.00, 22.00, -8.37, -6.72, -0.65, 10.5)}
for cx, spring, fk in [(-15, 'S', "W"), (0, 'N', "M"), (15, 'S', "E")]:
    sw = cell_sweep(cx, spring)
    print(f"cell cx {cx:+3d} ({spring}): vs case(no shelf) {inter_vol(case_noshelf, sw):9.3f}"
          f"  vs wings {inter_vol(wings, sw):9.3f}"
          f"  (own-fin box {inter_vol(fin_boxes[fk], sw):9.3f})"
          f"  vs switch env {inter_vol(switch_env, sw):9.3f}")
for sgn, nm in ((+1, "east"), (-1, "west")):
    zone_in = box(22.50, 30.25, -59.62, -9.12, 7.40, 16.65) if sgn > 0 else \
        box(-30.25, -22.50, -59.62, -9.12, 7.40, 16.65)
    print(f"finger zone {nm} (inboard, to X 30.25): vs case(no shelf) "
          f"{inter_vol(case_noshelf, zone_in):9.3f}  vs wings {inter_vol(wings, zone_in):9.3f}")

print("\n== F. interference table (shelf on) + outline + flatness ==")
for n, s in internals.items():
    print(f"case vs {n:18s}: {inter_vol(case_all, s):10.3f} mm3")
case_parts = {"tray-left": tray_l, "tray-right": tray_r, "infill": infill,
              "shell": shell, "shelf": shelf, "plate-left": plate_l,
              "plate-right": plate_r, "plunger": plunger, "pipe": pipe}
print("-- per-part nonzero detail --")
for cn, cs in case_parts.items():
    for n, s in internals.items():
        v = inter_vol(cs, s)
        if v > 0.01:
            print(f"{cn:12s} vs {n:18s}: {v:10.3f} mm3")
print("-- case vs case (nonzero only) --")
names = list(case_parts)
for i in range(len(names)):
    for j in range(i + 1, len(names)):
        v = inter_vol(case_parts[names[i]], case_parts[names[j]])
        if v > 0.01:
            print(f"{names[i]:12s} vs {names[j]:12s}: {v:10.3f} mm3")
bb = case_all.bounding_box()
print(f"assembly bbox X {bb.min.X:.2f}..{bb.max.X:.2f} (W {bb.max.X - bb.min.X:.2f})"
      f"  Y {bb.min.Y:.2f}..{bb.max.Y:.2f} (D {bb.max.Y - bb.min.Y:.2f})"
      f"  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
north_asm = fuse_all([tray_l, tray_r, infill, shelf])
worst = 0.0
for xi in range(-117, 117, 2):
    cs = slabs(north_asm, box(xi, xi + 2, -70, -60, -2.65, 22.0))
    if cs:
        worst = max(worst, abs(min(c.bounding_box().min.Y for c in cs) - FLUSH_Y))
print(f"north flatness: max |Ymin - (-64.37)| over |X|<=117: {worst:.3f} mm")

print("\n== G. Fly / USB ==")
fbb = fly.bounding_box()
print(f"Fly bbox Y {fbb.min.Y:.2f}..{fbb.max.Y:.2f} Z {fbb.min.Z:.2f}..{fbb.max.Z:.2f}"
      f" -> mouth protrusion {FLUSH_Y - fbb.min.Y:+.2f} (0.00 = flush)")
print(f"Fly vs shelf {inter_vol(shelf, fly):.3f}   plug vs shelf {inter_vol(shelf, plug):.3f}")
print(f"plug vs case(no shelf) {inter_vol(case_noshelf, plug):.3f}"
      f"   Fly vs tray-right {inter_vol(tray_r, fly):.3f}"
      f"   Fly vs Wings {inter_vol(wings, fly):.3f}")

print("\n== H. power-board drop re-check (wings NOT seated) ==")
drop = pb_parts
swept = drop
z = 0.25
while z <= 12.01:
    swept = swept.fuse(drop.moved(bd.Location((0, 0, z))))
    z += 0.25 if z < 2.0 else 1.0
case_pre = fuse_all([tray_l, tray_r, infill])
print(f"drop sweep vs trays+infill: {inter_vol(case_pre, swept):.3f} mm3"
      f" (expect 12.000 = tongue snap overlaps)")
tongues = fuse_all([box(25.75, 28.25, -53, -47, 0.15, 1.15),
                    box(25.75, 28.25, -23, -17, 0.15, 1.15),
                    box(-28.25, -25.75, -53, -47, 0.15, 1.15),
                    box(-28.25, -25.75, -23, -17, 0.15, 1.15)])
print(f"drop sweep vs tongue boxes only: {inter_vol(tongues, swept):.3f} mm3")
