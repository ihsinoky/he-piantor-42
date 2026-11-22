"""Export Y>=48 half-section STLs through the pad centre for
the lap section render: shell, cover, plunger, and the Ø40
module disc, cut at the Y=48 plane."""
import build123d as bd

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


def cyl(cx, cy, r, z0, z1):
    return bd.Solid.make_cylinder(r, z1 - z0,
                                  bd.Plane(origin=(cx, cy, z0)))


north = box(-60, 60, -20, 48.0, -5, 30)
for name in ("shell-central", "trackpad-cover", "plunger-sw1",
             "centre-infill"):
    s = load(name).cut(north)
    bd.export_stl(s, f"{ASM}/section-{name}.stl")
    print("section", name, "vol", round(s.volume, 1))
mod = cyl(0.0, 48.0, 20.0, 11.20, 12.70).cut(north)
bd.export_stl(mod, f"{ASM}/section-module.stl")
print("section module vol", round(mod.volume, 1))
print("done")
