"""Wing-lap round verification (Issue #296):
1. Re-profile the Wing inner perimeter (slab method): the open
   slot must be gone - no PLATE<->CASE void run > 0.35 wide in
   Y -0.4..72; the seam (plate edge -> band face) reads ~0.30.
2. Tongue audit at stations: tray material under the plate edge
   (Z 8.65..9.15, strip edge-1.2..edge+0.05) and band top 10.90
   beside the seam.
3. Through-path probes: columns along the seam must be blocked
   by plate/band (Z 9.40..10.95) or tongue (Z 8.60..9.15).
4. Tolerance corners: plate shifted +-0.30 X/Y - interference
   vs tray/shell/infill stays 0.000; with the plate shifted
   0.30 AWAY, the widened 0.60 hairline still has tongue under
   it (no through-gap).
5. Assembly: plate lifted +2.5 / +5.0 (drop-in / lift-out path)
   vs all case parts = 0.000.
6. Trays remain single solids; tray x caps (rest/pressed) 0.000.
"""
import build123d as bd
import json

ASM = "./asm3d"
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def g17(name, dx=0.0):
    s = bd.import_brep(f"{G17}/{pos[name]}.brep")
    return s.moved(bd.Location((dx, 0, -2.65)))


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


def vol(r):
    if r is None:
        return 0.0
    items = r if isinstance(r, (list, bd.ShapeList)) else [r]
    return sum(c.volume for c in items if c is not None)


def rep(label, v):
    print(f"  {label:56s} {v:12.4f}")
    return v


plate_r, plate_l = load("plate-right"), load("plate-left")
tray_r, tray_l = load("tray-right"), load("tray-left")
shell, infill = load("shell-central"), load("centre-infill")
shelf, cover = load("north-shelf"), load("trackpad-cover")
PLATES = {"plateR": plate_r, "plateL": plate_l}
CASE = {"shell": shell, "trayR": tray_r, "trayL": tray_l,
        "shelf": shelf, "infill": infill}
ALL = dict(CASE)
ALL.update(PLATES)

print("== tray solidity ==")
for nm, t in (("tray-right", tray_r), ("tray-left", tray_l)):
    print(f"  {nm}: {len(t.solids())} solid(s), vol {t.volume/1000:.2f}k")

print("== 1. re-profile inner edges (rows) ==")


def subs(s, slab):
    r = s.intersect(slab)
    if r is None:
        return []
    items = r if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and c.volume > 1e-7]


worst_gap = 0.0
for y in range(0, 73, 4):
    slab = box(-56.0, 56.0, y - 0.25, y + 0.25, 9.90, 10.95)
    runs = []
    for name, s in ALL.items():
        for c in subs(s, slab):
            bb = c.bounding_box()
            runs.append([round(bb.min.X, 2), round(bb.max.X, 2),
                         "PLATE" if name in PLATES else "CASE", name])
    runs.sort()
    for i in range(len(runs) - 1):
        r0, r1 = runs[i], runs[i + 1]
        if {r0[2], r1[2]} == {"PLATE", "CASE"} and r1[0] - r0[1] > 0.05:
            w = r1[0] - r0[1]
            worst_gap = max(worst_gap, w)
            print(f"  Y={y}: seam {r0[1]}..{r1[0]} w={w:.2f} "
                  f"({r0[3]}<->{r1[3]})")
print(f"  worst seam width: {worst_gap:.2f} (expect ~0.30)")

print("== 2/3. tongue + through-path probes at stations ==")


def plate_edge_x(plate, y, sgn):
    slab = box(-60.0, 60.0, y - 0.3, y + 0.3, 9.90, 10.95)
    cs = subs(plate, slab)
    if not cs:
        return None
    if sgn > 0:
        return min(c.bounding_box().min.X for c in cs)
    return max(c.bounding_box().max.X for c in cs)


def colmat(solids, x, y, z0, z1, half=0.06):
    cell = box(x - half, x + half, y - half, y + half, z0, z1)
    return sum(vol(s.intersect(cell)) for s in solids)


for sgn, plate, tray in ((+1, plate_r, tray_r), (-1, plate_l, tray_l)):
    for y in (0, 10, 20, 30, 40, 45, 50, 60, 68):
        e = plate_edge_x(plate, float(y), sgn)
        if e is None:
            print(f"  sgn={sgn} Y={y}: no plate in row")
            continue
        # tongue: tray material under the plate edge strip
        tx = e - sgn * 0.6
        tv = colmat([tray], tx, float(y), 8.60, 9.15, half=0.5)
        # band top beside the seam (0.35..2.0 out from the edge)
        bx = e - sgn * 1.2
        bv = colmat([tray], bx, float(y), 10.30, 10.95, half=0.5)
        # through-path: probe the hairline centre (0.15 out)
        hx = e - sgn * 0.15
        blocked = colmat([plate, tray, shell, infill], hx, float(y),
                         9.40, 10.95) + \
            colmat([tray], hx, float(y), 8.60, 9.15)
        print(f"  sgn={sgn:+d} Y={y:2d} edge={e:7.2f} "
              f"tongue={tv:8.3f} bandtop={bv:8.3f} seamblock={blocked:8.3f}")

print("== 4. tolerance corners (plate shifted) ==")
for dx, dy, tag in ((0.30, 0, "away +X"), (-0.30, 0, "toward -X"),
                    (0, 0.30, "+Y"), (0, -0.30, "-Y")):
    for sgn, plate, tray in ((+1, plate_r, tray_r), (-1, plate_l, tray_l)):
        ps = plate.moved(bd.Location((dx * sgn, dy, 0)))
        rep(f"plate{sgn:+d} shift {tag} x tray",
            vol(ps.intersect(tray)))
        rep(f"plate{sgn:+d} shift {tag} x shell",
            vol(ps.intersect(shell)))
# widened-hairline tongue cover: plate shifted 0.30 away (+X right)
for sgn, plate, tray in ((+1, plate_r, tray_r), (-1, plate_l, tray_l)):
    ps = plate.moved(bd.Location((0.30 * sgn, 0, 0)))
    for y in (10, 30, 50):
        e = plate_edge_x(ps, float(y), sgn)
        hx = e - sgn * 0.45  # inside the widened 0.60 hairline
        tv = colmat([tray], hx, float(y), 8.60, 9.15)
        print(f"  away-shift sgn={sgn:+d} Y={y}: tongue under widened "
              f"hairline = {tv:.3f} (must be > 0)")

print("== 5. assembly: plate lift path ==")
others = [tray_r, tray_l, shell, infill, shelf, cover]
for dz in (2.5, 5.0):
    for sgn, plate in ((+1, plate_r), (-1, plate_l)):
        ps = plate.moved(bd.Location((0, 0, dz)))
        v = sum(vol(ps.intersect(o)) for o in others)
        rep(f"plate{sgn:+d} at +{dz} vs case", v)

print("== 6. tray x caps ==")
CAPS_J = json.load(open("./caps.json"))


def cap_solids(z1):
    ss = []
    for side in ("left", "right"):
        for poly in CAPS_J[side]["cap_polys"]:
            pts2 = [bd.Vector(p[0], p[1], 0) for p in poly]
            w = bd.Wire.make_polygon(pts2 + [pts2[0]])
            s = bd.extrude(bd.Face(w), z1 - 10.90)
            ss.append(s.moved(bd.Location((0, 0, 10.90))))
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r


for z1, tag in ((22.00, "unpressed"), (19.00, "pressed")):
    caps = cap_solids(z1)
    rep(f"tray-right x caps {tag}", vol(tray_r.intersect(caps)))
    rep(f"tray-left x caps {tag}", vol(tray_l.intersect(caps)))
print("DONE")
