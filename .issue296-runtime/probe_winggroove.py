"""Wing<->case groove measurement, slab method: each scan line is
ONE thin-slab intersect per solid (not per cell). A line at fixed
Y (row) or X (col) is cut with the Z 9.90..10.95 band slab; the
returned sub-solids' bounding intervals along the line are the
material runs. Between a PLATE run and a CASE run, the gap is
measured, and a second full-height slab gives the gap floor
(highest top below 10.89) and the adjacent case top.
Output: winggroove.json + text summary."""
import build123d as bd
import json

ASM = "./asm3d"


def load(name):
    return bd.import_brep(f"{ASM}/{name}.brep")


def box(x0, x1, y0, y1, z0, z1):
    return bd.Solid.make_box(x1 - x0, y1 - y0, z1 - z0,
                             bd.Plane(origin=(x0, y0, z0)))


PLATES = {"plateR": load("plate-right"), "plateL": load("plate-left")}
CASE = {"shell": load("shell-central"), "trayR": load("tray-right"),
        "trayL": load("tray-left"), "shelf": load("north-shelf"),
        "infill": load("centre-infill")}
ALL = dict(CASE)
ALL.update(PLATES)


def subs(s, slab):
    r = s.intersect(slab)
    if r is None:
        return []
    items = r if isinstance(r, (list, bd.ShapeList)) else [r]
    return [c for c in items if c is not None and c.volume > 1e-7]


def runs_on_line(kind, fixed, lo, hi):
    """Material runs in the plate band along one scan line."""
    if kind == "row":
        slab = box(lo, hi, fixed - 0.25, fixed + 0.25, 9.90, 10.95)
        ax = "X"
    else:
        slab = box(fixed - 0.25, fixed + 0.25, lo, hi, 9.90, 10.95)
        ax = "Y"
    runs = []
    for name, s in ALL.items():
        for c in subs(s, slab):
            bb = c.bounding_box()
            a, b = (bb.min.X, bb.max.X) if ax == "X" else (bb.min.Y, bb.max.Y)
            runs.append([round(a, 2), round(b, 2),
                         "PLATE" if name in PLATES else "CASE",
                         name, round(bb.max.Z, 3)])
    runs.sort()
    return runs


def gap_info(kind, fixed, a, b):
    """Floor + depth inside gap interval (a,b) on the scan line."""
    if kind == "row":
        slab = box(a + 0.05, b - 0.05, fixed - 0.25, fixed + 0.25,
                   -3.0, 10.89)
    else:
        slab = box(fixed - 0.25, fixed + 0.25, a + 0.05, b - 0.05,
                   -3.0, 10.89)
    floor, fname = None, None
    for name, s in ALL.items():
        for c in subs(s, slab):
            t = c.bounding_box().max.Z
            if floor is None or t > floor:
                floor, fname = t, name
    return (None if floor is None else round(floor, 3)), fname


def grooves(kind, fixed, lo, hi):
    runs = runs_on_line(kind, fixed, lo, hi)
    out = []
    for i in range(len(runs) - 1):
        r0, r1 = runs[i], runs[i + 1]
        kinds = {r0[2], r1[2]}
        if kinds != {"PLATE", "CASE"}:
            continue
        a, b = r0[1], r1[0]
        if b - a < 0.05:
            continue
        floor, fname = gap_info(kind, fixed, a, b)
        case_run = r0 if r0[2] == "CASE" else r1
        out.append(dict(a=a, b=b, width=round(b - a, 2), floor=floor,
                        floor_part=fname,
                        depth=None if floor is None
                        else round(10.90 - floor, 2),
                        case_part=case_run[3], case_top=case_run[4]))
    return out


result = {"rows": {}, "cols": {}}
for y in range(-60, 81, 5):
    gs = []
    for lo, hi in ((16.0, 52.0), (-52.0, -16.0)):
        gs.extend(grooves("row", float(y), lo, hi))
    if gs:
        result["rows"][str(y)] = gs
    print(f"row {y} done", flush=True)
for x in list(range(30, 151, 10)) + list(range(-150, -29, 10)):
    gs = grooves("col", float(x), -67.0, -54.0)
    gs += grooves("col", float(x), 74.0, 85.0)
    if gs:
        result["cols"][str(x)] = gs
    print(f"col {x} done", flush=True)

json.dump(result, open("winggroove.json", "w"), indent=1)
for axis in ("rows", "cols"):
    for k, gs in result[axis].items():
        for g in gs:
            print(f"{axis} {k}: groove {g['a']}..{g['b']} w={g['width']} "
                  f"floor={g['floor']}({g['floor_part']}) "
                  f"depth={g['depth']} case={g['case_part']} "
                  f"top={g['case_top']}")
print("DONE")
