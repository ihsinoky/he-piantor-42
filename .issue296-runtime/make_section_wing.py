"""Export a thin Y 43..45 slab through the Wing<->case seam
for the wing-lap section render: tray-right (with the band),
shell-central, plate-right and the Wing board, sliced at
Y=44 so the cross-section profile reads directly (band flush
at 10.90, seam, tongue under the plate edge at X ~37.1,
Wing board below). Uses intersect with a slab solid (chained
cut() proved unreliable on some of these solids)."""
import build123d as bd

ASM = "./asm3d"
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
import json
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


def solids_of(r):
    if isinstance(r, bd.ShapeList):
        return [x for x in r if isinstance(x, bd.Solid)]
    return r.solids()


def as_compound(r):
    ss = solids_of(r)
    assert ss, "empty intersect"
    return bd.Compound(ss), sum(x.volume for x in ss)


slab = box(-80, 80, 43.0, 45.0, -5, 30)
for name in ("tray-right", "shell-central", "plate-right"):
    s, vol = as_compound(load(name).intersect(slab))
    bb = s.bounding_box()
    assert 42.9 < bb.min.Y and bb.max.Y < 45.1, (name, bb.min.Y, bb.max.Y)
    bd.export_stl(s, f"{ASM}/section-wing-{name}.stl")
    print("section", name, "vol", round(vol, 1),
          "Y", round(bb.min.Y, 2), "..", round(bb.max.Y, 2))
wing = bd.import_brep(f"{G17}/{pos['wing_right']}.brep")
wing, wvol = as_compound(
    wing.moved(bd.Location((9.5, 0, -2.65))).intersect(slab))
bb = wing.bounding_box()
assert 42.9 < bb.min.Y and bb.max.Y < 45.1, ("board", bb.min.Y, bb.max.Y)
bd.export_stl(wing, f"{ASM}/section-wing-board.stl")
print("section wing board vol", round(wvol, 1),
      "Y", round(bb.min.Y, 2), "..", round(bb.max.Y, 2))
print("done")
