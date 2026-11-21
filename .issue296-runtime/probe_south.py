"""Probe the CURRENT (tip d8b687d4b) south geometry for the plan-A
unification build. Outputs probe_south.json:
- tray face C(X) per side at 0.5 mm sampling, X 43..63.5, in two Z
  bands (low -2.65..0, high 0..10.90) and full band; plus the tray
  Z range at the face columns.
- diagonal fit from tray profile |X| 62..76 (0.5 mm).
- plate south profile plateSouth(X) at 0.5 mm, |X| 40..60.
- shell slice-band content (Y 68.876..69.288): volume + Z range in
  three X zones (centre / transition / corner).
- top-Z scan of the south band surface at X stations.
Run with the cad-venv python.
"""
import build123d as bd
import json, os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))

def part(name):
    return bd.import_brep(f"{ASM}/{name}.brep")

def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))

def cells_of(r):
    if r is None:
        return []
    return [x for x in (list(r) if isinstance(r, (list, bd.ShapeList)) else [r])
            if hasattr(x, "volume") and x.volume > 1e-9]

def southmost(solid, xa, xb, z0, z1):
    cs = cells_of(solid.intersect(box(xa, xb, 40.0, 95.0, z0, z1)))
    if not cs:
        return None
    return max(c.bounding_box().max.Y for c in cs)

tray_r, tray_l = part("tray-right"), part("tray-left")
plate_r, plate_l = part("plate-right"), part("plate-left")
shell = part("shell-central")

out = {"tray_face": {}, "plate_south": {}, "shell_slice": {}, "top_scan": {}}

for sgn, tray in ((+1, tray_r), (-1, tray_l)):
    rows = []
    x = 43.0
    while x <= 63.5:
        xa, xb = (x, x + 0.5) if sgn > 0 else (-x - 0.5, -x)
        full = southmost(tray, xa, xb, -2.65, 10.90)
        low = southmost(tray, xa, xb, -2.65, 0.0)
        high = southmost(tray, xa, xb, 0.0, 10.90)
        rows.append([round(x + 0.25, 2),
                     None if full is None else round(full, 3),
                     None if low is None else round(low, 3),
                     None if high is None else round(high, 3)])
        x += 0.5
    out["tray_face"]["R" if sgn > 0 else "L"] = rows
    print(f"tray face {'R' if sgn>0 else 'L'} done", flush=True)

# diagonal: sample |X| 62..76 on the fused trays (full Z band of the wall)
rows = []
x = 62.0
while x <= 76.0:
    v = southmost(tray_r, x, x + 0.5, -2.65, 10.90)
    rows.append([round(x + 0.25, 2), None if v is None else round(v, 3)])
    x += 0.5
out["diagonal_R"] = rows
print("diagonal done", flush=True)

for sgn, plate in ((+1, plate_r), (-1, plate_l)):
    rows = []
    x = 40.0
    while x <= 60.0:
        xa, xb = (x, x + 0.5) if sgn > 0 else (-x - 0.5, -x)
        v = southmost(plate, xa, xb, -3.0, 23.0)
        rows.append([round(x + 0.25, 2), None if v is None else round(v, 3)])
        x += 0.5
    out["plate_south"]["R" if sgn > 0 else "L"] = rows
    print(f"plate south {'R' if sgn>0 else 'L'} done", flush=True)

# shell slice band content per X zone
for nm, (xa, xb) in {"centre |X|<=30": (-30.0, 30.0),
                     "transition 38..40": (38.0, 40.0),
                     "corner 40..41.25": (40.0, 41.25)}.items():
    cs = cells_of(shell.intersect(box(xa, xb, 68.876, 69.288, -3.0, 23.0)))
    if cs:
        out["shell_slice"][nm] = {
            "vol": round(sum(c.volume for c in cs), 3),
            "zmin": round(min(c.bounding_box().min.Z for c in cs), 3),
            "zmax": round(max(c.bounding_box().max.Z for c in cs), 3),
            "ymax": round(max(c.bounding_box().max.Y for c in cs), 3)}
    else:
        out["shell_slice"][nm] = None
    print(f"shell slice {nm} done", flush=True)

# top-Z scan of the south band: at X stations, walk Y 64..83 in 1 mm
# steps and report the topmost case surface (trays+infill+shell+plates)
infill = part("centre-infill")
case_south = tray_l.fuse(tray_r).fuse(infill).fuse(shell).fuse(plate_l).fuse(plate_r)
for X in (0.0, 30.0, 45.0, 52.0, 56.0):
    rows = []
    y = 64.0
    while y <= 83.0:
        cs = cells_of(case_south.intersect(box(X - 0.5, X + 0.5, y, y + 1.0, -3.0, 23.0)))
        rows.append([round(y + 0.5, 1),
                     None if not cs else round(max(c.bounding_box().max.Z for c in cs), 2)])
        y += 1.0
    out["top_scan"][f"X={X}"] = rows
    print(f"top scan X={X} done", flush=True)

json.dump(out, open(os.path.join(RT, "probe_south.json"), "w"))
print("saved probe_south.json", flush=True)
