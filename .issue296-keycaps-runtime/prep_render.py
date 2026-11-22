"""Prepare render scene STLs for the keycap design (cad-venv python).

Scenes:
 - close-up / underside: one cap on a simplified Jade Pro (body +
   cross stem at the drawing dims) over a plate slab.
 - row: six switches + caps at 17 mm pitch on a plate slab.
 - in-case: the 42 designed caps placed at the caps.json poses in
   the case frame (z offset = plate top 10.90), one STL per side.
"""
import json
import os
import sys

import build123d as bd

sys.path.insert(0, os.path.expanduser(
    "~/workspace/projects/he-piantor-keycaps/hardware/keycaps"))
import keycap as kc

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "render")
os.makedirs(OUT, exist_ok=True)
RT = os.path.expanduser("~/workspace/projects/he-piantor-keycaps/"
                        ".issue296-runtime")


def switch_solid():
    body = kc._prism(14.00, 1.0, 0.0, kc.LEDGE_Z)
    stem = kc._cross_prism(4.00, kc.ARM_NS, kc.ARM_EW, kc.LEDGE_Z,
                           kc.STEM_TIP_Z)
    return body.fuse(stem)


def plate_slab(w, d):
    return bd.Solid.make_box(w, d, 1.5, bd.Plane(origin=(-w / 2, -d / 2, -1.5)))


def _fuse_all(parts):
    out = parts[0]
    for p in parts[1:]:
        out = out.fuse(p)
    return out

cap = kc.build_cap(17.0)
sw = switch_solid()
bd.export_stl(cap, os.path.join(OUT, "cap-single.stl"))
bd.export_stl(sw, os.path.join(OUT, "switch-single.stl"))
bd.export_stl(plate_slab(34, 34), os.path.join(OUT, "plate-single.stl"))

# row of six at 17 mm pitch
row_caps, row_sws = [], []
for i in range(6):
    x = (i - 2.5) * 17.0
    loc = bd.Location(bd.Vector(x, 0, 0))
    row_caps.append(cap.moved(loc))
    row_sws.append(sw.moved(loc))
bd.export_stl(_fuse_all(row_caps), os.path.join(OUT, "row-caps.stl"))
bd.export_stl(_fuse_all(row_sws), os.path.join(OUT, "row-switches.stl"))
bd.export_stl(plate_slab(6 * 17 + 14, 34), os.path.join(OUT, "row-plate.stl"))

# dish section: three dish variants half-sectioned at y=0 (keep
# y <= 0), in a row — the XZ profile shows pocket / rim / R.
half = bd.Solid.make_box(80, 40, 30, bd.Plane(origin=(-40, -40, -2)))
secs = []
for i, s in enumerate(kc.DISH_VARIANTS):
    loc = bd.Location(bd.Vector((i - 1) * 21.0, 0, 0))
    for p in kc.build_cap(17.0, dish_depth=s).intersect(half).solids():
        secs.append(p.moved(loc))
bd.export_stl(_fuse_all(secs), os.path.join(OUT, "cap-sections.stl"))
print("dish sections exported", kc.DISH_VARIANTS)

# in-case: caps at caps.json poses, case frame
caps = json.load(open(os.path.join(RT, "caps.json")))
for side in ("left", "right"):
    placed = []
    for (x, y, ang) in caps[side]["keys"]:
        loc = bd.Location(bd.Vector(x, y, 10.90), bd.Vector(0, 0, ang))
        placed.append(cap.moved(loc))
    bd.export_stl(_fuse_all(placed),
                  os.path.join(OUT, f"incase-caps-{side}.stl"))
    print(side, len(placed), "caps placed")
print("render STLs in", OUT)
