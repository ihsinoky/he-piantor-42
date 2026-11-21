"""Centre section view (Y-Z plane at X=0) of the revised case.
Slab X -0.6..0.6 through: trays+infill, power board, middle cell,
battery cover (band over the bay), shell (slope + trackpad island),
trackpad pad, Main. Drawn from tessellated section solids.
Output: goal files/case296-3d-section-centre.png"""
import build123d as bd
import json, os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
OUTP = os.path.expanduser("~/workspace/goals/he-piantor-42-keyboard-pmo/files/case296-3d-section-centre.png")
ZC = 2.65

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

SLAB = box(-0.6, 0.6, -90, 95, -5, 25)

def section(s):
    r = s.intersect(SLAB)
    if r is None:
        return None
    ss = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    ss = [x for x in ss if hasattr(x, "volume") and x.volume > 1e-6]
    return fuse_all(ss) if ss else None

def polys_of(s):
    if s is None:
        return []
    bd.export_stl(s, "/tmp/section_tmp.stl")
    import struct
    import numpy as np
    with open("/tmp/section_tmp.stl", "rb") as f:
        data = f.read()
    n = struct.unpack("<I", data[80:84])[0]
    dt = np.dtype([("n", "<f4", (3,)), ("v", "<f4", (3, 3)), ("a", "<u2")])
    arr = np.frombuffer(data[84:84 + n * 50], dtype=dt)["v"]
    return [[(float(p[1]), float(p[2])) for p in tri] for tri in arr]

# Main from the D-063 outline (same construction as verify_case3d.py)
segs = json.load(open(os.path.join(ASM, "..", "main-outline-asm.json")))
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
face = bd.Face(bd.Wire(edges))
_s = bd.extrude(face, 1.2)
if _s.bounding_box().max.Z < 0.6:
    _s = bd.extrude(face, -1.2)
main = _s.moved(bd.Location((0, 0, 4.70 - _s.bounding_box().min.Z)))

cell = bd.Solid.make_cylinder(7.25, 50.5, bd.Plane(origin=(0, -59.62, 7.40),
                                                   z_dir=(0, 1, 0)))
pb = box(-26.25, 26.25, -62.37, -4.37, -0.65, 0.15)
pad = bd.Solid.make_cylinder(22, 1.5, bd.Plane(origin=(0, 48, 11.20)))

layers = [
    ("tray + infill", fuse_all([part("tray-left"), part("tray-right"),
                                part("centre-infill")]), "#b8bec9", 1),
    ("power board", pb, "#7a4a21", 3),
    ("cell (AA)", cell, "#e8e4da", 3),
    ("Main board", main, "#2e7d4f", 3),
    ("battery cover (lid)", part("battery-cover"), "#8fa3c7", 4),
    ("shell-central", part("shell-central"), "#d7dce6", 2),
    ("trackpad", pad, "#444a55", 5),
]

fig, ax = plt.subplots(figsize=(13.5, 5.6), dpi=200)
for name, solid, color, zo in layers:
    ps = polys_of(section(solid))
    if ps:
        ax.add_collection(PolyCollection(ps, facecolor=color, edgecolor="#3a3f4a",
                                         linewidth=0.3, zorder=zo, alpha=0.95))
ax.axhline(22.00, color="#c0392b", lw=1.0, ls="--", zorder=6)
ax.axhline(10.90, color="#2471a3", lw=0.8, ls=":", zorder=6)
ax.axvline(-64.37, color="#c0392b", lw=0.8, ls="--", zorder=6)
ax.text(83.5, 22.3, "keytop datum Z22.00", color="#c0392b", fontsize=8, ha="right")
ax.text(83.5, 11.3, "plate top Z10.90", color="#2471a3", fontsize=8, ha="right")
ax.text(-63.9, -4.3, "flush north face Y-64.37", color="#c0392b", fontsize=8)
ax.annotate("north band: lid top 22.00", xy=(-40, 22.0), xytext=(-58, 24.6),
            fontsize=9, arrowprops=dict(arrowstyle="-", lw=0.7))
ax.annotate("slope 22.00 -> 10.90 (Y -0.37..20)", xy=(10, 16.4), xytext=(16, 24.6),
            fontsize=9, arrowprops=dict(arrowstyle="-", lw=0.7))
ax.annotate("trackpad: island kept, pad surface 12.70", xy=(0, 12.7),
            xytext=(30, 19.5), fontsize=9,
            arrowprops=dict(arrowstyle="-", lw=0.7))
ax.annotate("centre / south at plate height 10.90", xy=(30, 10.9),
            xytext=(38, 5.0), fontsize=9,
            arrowprops=dict(arrowstyle="-", lw=0.7))
ax.set_xlim(-72, 86)
ax.set_ylim(-5, 27)
ax.set_xlabel("Y (mm, + south) — section at X = 0")
ax.set_ylabel("Z (mm)")
ax.set_title("Issue #296 wireless case — centre section (X=0), north-flush + PO profile revision")
ax.set_aspect("equal")
ax.grid(True, lw=0.3, alpha=0.4)
fig.tight_layout()
fig.savefig(OUTP)
print("saved", OUTP)
