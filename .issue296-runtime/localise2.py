"""Localise round 2: tray/wings remainder, middle-cell sweep clash,
W fin presence, Fly/wings graze, finger-zone lower band."""
import build123d as bd
import json, os

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

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def fuse_all(ss):
    r = ss[0]
    for s in ss[1:]:
        r = r.fuse(s)
    return r

def solids(r):
    if r is None:
        return []
    if isinstance(r, (list, bd.ShapeList)):
        return [x for x in r if hasattr(x, "volume") and x.volume > 0.001]
    try:
        return [r] if r.volume > 0.001 else []
    except Exception:
        return []

def show(label, a, b):
    try:
        ss = solids(a.intersect(b))
    except Exception as e:
        print(f"{label}: intersect failed {e}")
        return
    tot = sum(s.volume for s in ss)
    print(f"{label}: total {tot:.2f} mm3 in {len(ss)} solid(s)")
    for s in ss:
        bb = s.bounding_box()
        print(f"   vol {s.volume:9.2f}  X {bb.min.X:8.2f}..{bb.max.X:8.2f}"
              f"  Y {bb.min.Y:8.2f}..{bb.max.Y:8.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}")

tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
shell, strip_l, strip_r = part("shell-central"), part("strip-left"), part("strip-right")
plate_l, plate_r = part("plate-left"), part("plate-right")
case_nocover = fuse_all([tray_l, tray_r, infill, shell, strip_l, strip_r,
                         plate_l, plate_r])
wing_r = g17("wing_right", 9.5)
und_r = fuse_all([g17(e["name"], 9.5) for e in idx
                  if e["name"].startswith("underside-right")])
wings_r = fuse_all([wing_r, und_r])
fly = None
for e in idx:
    if e["name"].startswith("Fly-official"):
        s = g17(e["name"])
        fly = s if fly is None else fly.fuse(s)
fly = fly.moved(bd.Location((38, -1.80, 0)))

show("tray-right x wings-right", tray_r, wings_r)
show("infill x wings-right", infill, wings_r)
show("Fly x wings-right", fly, wings_r)

wfin = box(-22.25, -7.0, -8.37, -6.72, -0.65, 10.5)
print("tray-left material inside W fin box:", 
      round(sum(s.volume for s in solids(tray_l.intersect(wfin))), 2),
      "of", round(wfin.volume, 2))
efin = box(7.0, 22.25, -8.37, -6.72, -0.65, 10.5)
print("case material inside E fin box:",
      round(sum(s.volume for s in solids(case_nocover.intersect(efin))), 2),
      "of", round(efin.volume, 2))

def aa_cell(cx):
    return bd.Solid.make_cylinder(7.25, 50.5,
                                  bd.Plane(origin=(cx, -59.62, 7.40),
                                           z_dir=(0, 1, 0)))
def sweep(cx, spring):
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
        loc = bd.Location((piv.X, piv.Y, piv.Z)) * \
            bd.Location((0, 0, 0), (1, 0, 0), th if spring == 'S' else -th) * \
            bd.Location((-piv.X, -piv.Y, -piv.Z))
        c2 = cell.moved(loc)
        if c2.bounding_box().max.Z < cell.bounding_box().max.Z:
            loc = bd.Location((piv.X, piv.Y, piv.Z)) * \
                bd.Location((0, 0, 0), (1, 0, 0), -th if spring == 'S' else th) * \
                bd.Location((-piv.X, -piv.Y, -piv.Z))
            c2 = cell.moved(loc)
        swept = swept.fuse(c2)
    return swept

sw_m = sweep(0, 'N')
show("middle sweep x case(no cover)", sw_m, case_nocover)
nwall = box(-30.25, 30.25, -64.37, -62.37, -2.65, 15.15)
show("middle sweep x N wall box", sw_m, nwall)
# clash Z profile vs wall: slice the intersection by Z bands
inter = solids(sw_m.intersect(case_nocover))
if inter:
    both = fuse_all(inter)
    for z0 in range(0, 16, 2):
        ss = solids(both.intersect(box(-40, 40, -70, 0, z0, z0 + 2)))
        if ss:
            print(f"   clash in Z {z0}..{z0+2}: {sum(s.volume for s in ss):.2f} mm3")

for sgn, nm in ((+1, "east"), (-1, "west")):
    zone = box(22.50, 30.25, -59.62, -9.12, 7.40, 9.40) if sgn > 0 else \
        box(-30.25, -22.50, -59.62, -9.12, 7.40, 9.40)
    ss = solids(case_nocover.intersect(zone))
    print(f"finger zone {nm} Z 7.40..9.40 band vs case: "
          f"{sum(s.volume for s in ss):.3f} mm3")
