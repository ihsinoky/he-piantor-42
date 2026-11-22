"""Probe 4: (a) real Fly + real USB plug (g17 reference solids at
the FLYMOVE pose) vs tray-right and vs the rotating shelf;
(b) localize the arc sweep's fixed-case first contact at 2.5 deg."""
import build123d as bd
import json

ASM = "./asm3d"
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
ZC = 2.65
AX_Y, AX_Z = -0.57, 19.30
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
FLY_C = json.load(open(f"{ASM}/params.json"))["fly_centre"]
FLYMOVE = (FLY_C[0], FLY_C[1] + 50.14)


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


def fuse_all(lst):
    f = lst[0]
    for s in lst[1:]:
        f = f.fuse(s)
    return f


fly = fuse_all([g17(e["name"]) for e in idx
                if e["name"].startswith("Fly-official")])
fly = fly.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
plug = fuse_all([g17(n) for n in ("USB-reference-shell",
                                  "USB-reference-overmold",
                                  "USB-reference-cable-exit")])
plug = plug.moved(bd.Location((FLYMOVE[0], FLYMOVE[1], 0)))
pb = plug.bounding_box()
print(f"real plug bbox: X {pb.min.X:.2f}..{pb.max.X:.2f} "
      f"Y {pb.min.Y:.2f}..{pb.max.Y:.2f} Z {pb.min.Z:.2f}..{pb.max.Z:.2f}")
tray_r = load("tray-right")
print(f"tray-right x real Fly: {vol(tray_r.intersect(fly)):.4f}")
print(f"tray-right x real plug: {vol(tray_r.intersect(plug)):.4f}")
print(f"closed shelf x real plug: {vol(load('north-shelf').intersect(plug)):.4f}")
print(f"closed shelf x real Fly: {vol(load('north-shelf').intersect(fly)):.4f}")


def rot(s, deg):
    loc = (bd.Location((0, AX_Y, AX_Z))
           * bd.Location((0, 0, 0), (-deg, 0, 0))
           * bd.Location((0, -AX_Y, -AX_Z)))
    return s.moved(loc)


shelf = load("north-shelf")
print("== arc vs real plug / real Fly ==")
for deg in (0.5, 1.0, 1.5, 2.0, 2.5, 4.0, 6.0, 8.0, 12.0, 20.0, 40.0):
    rs = rot(shelf, deg)
    print(f"  {deg:5.1f} deg: plug {vol(rs.intersect(plug)):9.4f}   "
          f"fly {vol(rs.intersect(fly)):9.4f}")

print("== localize fixed-case contact at 2.5 deg ==")
rs = rot(shelf, 2.5)
for pn in ("tray-left", "tray-right", "centre-infill", "shell-central",
           "plate-left", "plate-right", "plunger-sw1", "light-pipe-dled",
           "latch-slider"):
    for c in cells_of(rs.intersect(load(pn))):
        bb = c.bounding_box()
        print(f"  shelf(2.5) x {pn}: vol {c.volume:.3f} "
              f"X {bb.min.X:.2f}..{bb.max.X:.2f} "
              f"Y {bb.min.Y:.2f}..{bb.max.Y:.2f} "
              f"Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
