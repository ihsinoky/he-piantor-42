"""Full-height row profiles over the centre/Wing region: for each
row Y (step 2), one slab intersect per solid; runs along X with
(part, top Z). Reveals exactly what borders each Wing plate and
at what height, all around the inner perimeter.
Output: wingprofile.json + compact text for rows near the plate."""
import build123d as bd
import json

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


SOLIDS = {"plateR": load("plate-right"), "plateL": load("plate-left"),
          "shell": load("shell-central"), "trayR": load("tray-right"),
          "trayL": load("tray-left"), "shelf": load("north-shelf"),
          "infill": load("centre-infill")}


def subs(s, slab):
    r = s.intersect(slab)
    if r is None:
        return []
    items = r if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and c.volume > 1e-7]


out = {}
for y in range(-64, 83, 2):
    slab = box(-60.0, 60.0, y - 0.5, y + 0.5, -3.0, 23.0)
    runs = []
    for name, s in SOLIDS.items():
        for c in subs(s, slab):
            bb = c.bounding_box()
            runs.append([round(bb.min.X, 2), round(bb.max.X, 2),
                         name, round(bb.max.Z, 2)])
    runs.sort()
    out[str(y)] = runs
    print(f"row {y} done ({len(runs)} runs)", flush=True)

json.dump(out, open("wingprofile.json", "w"), indent=1)
print("DONE")
