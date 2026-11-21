"""Diagnostics for the north-flush revision verification anomalies.
1. shell material in the centre slab Y 6..20 (verify_north F printed nothing)
2. what is at X 19..21, Y 20..35 with top 12.55 in the shell
3. shell at the SW1 column + plunger intersection location
4. plateau built south-edge clearance vs caps.json capline - 1.0
5. finger-zone working band Z 7.40..9.40 vs case (no cover)
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

def pieces(r):
    if r is None:
        return []
    xs = list(r) if isinstance(r, (list, bd.ShapeList)) else [r]
    return [x for x in xs if hasattr(x, "volume") and x.volume > 1e-6]

def inter(a, b):
    try:
        return pieces(a.intersect(b))
    except Exception as e:
        print("  intersect error:", e)
        return []

shell = part("shell-central")
plunger = part("plunger-sw1")
strip_r, strip_l = part("strip-right"), part("strip-left")

print("== 1. shell centre slab X -1..1, per Y bin ==")
for y0 in range(0, 24, 2):
    ps = inter(shell, box(-1, 1, y0, y0 + 2, 0, 23))
    if ps:
        zm = max(p.bounding_box().max.Z for p in ps)
        print(f"  Y {y0}..{y0+2}: vol {sum(p.volume for p in ps):8.2f}  top {zm:.2f}")
    else:
        print(f"  Y {y0}..{y0+2}: EMPTY")

print("== 2. shell in X 19..21, Y 20..35 ==")
for p in inter(shell, box(19, 21, 20, 35, 0, 23)):
    bb = p.bounding_box()
    print(f"  piece vol {p.volume:8.2f}  X {bb.min.X:.2f}..{bb.max.X:.2f}"
          f"  Y {bb.min.Y:.2f}..{bb.max.Y:.2f}  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")

print("== 3. SW1 column ==")
for p in inter(shell, box(-16.5, -14.5, 63.5, 65.5, 0, 23)):
    bb = p.bounding_box()
    print(f"  shell piece vol {p.volume:8.2f}  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")
print("  (no output above = no shell material in the 2x2 column)")
for p in inter(shell, plunger):
    bb = p.bounding_box()
    print(f"  plunger^shell vol {p.volume:.3f}  X {bb.min.X:.2f}..{bb.max.X:.2f}"
          f"  Y {bb.min.Y:.2f}..{bb.max.Y:.2f}  Z {bb.min.Z:.2f}..{bb.max.Z:.2f}")

print("== 4. plateau built south edge vs capline - 1.0 ==")
CAPS = json.load(open(os.path.join(RT, "caps.json")))
for nm, st, sgn in (("strip-right", strip_r, +1), ("strip-left", strip_l, -1)):
    caps = CAPS["right" if sgn > 0 else "left"]["capline"]
    worst = None
    for xi in range(31, 152):
        xa, xb = (xi, xi + 1) if sgn > 0 else (-xi - 1, -xi)
        ps = inter(st, box(xa, xb, -70, 30, 21.0, 22.5))
        if not ps:
            continue
        edge = max(p.bounding_box().max.Y for p in ps)
        ks = [k for k in range(xi - 1, xi + 2) if str(k) in caps]
        if ks:
            line = min(caps[str(k)] for k in ks) - 1.0
        else:
            near = min((int(k) for k in caps), key=lambda c: abs(c - xi))
            line = caps[str(near)] - 1.0
        clr = line - edge
        if worst is None or clr < worst[0]:
            worst = (clr, xi, edge, line)
    print(f"  {nm}: min built clearance {worst[0]:.2f} mm at column {worst[1]}"
          f" (edge Y {worst[2]:.2f}, capline-1.0 Y {worst[3]:.2f})")

print("== 5. finger-zone working band Z 7.40..9.40 ==")
tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
plate_l, plate_r = part("plate-left"), part("plate-right")
case_nc = tray_l.fuse(tray_r, infill, shell, strip_l, strip_r, plate_l, plate_r)
for nm, zb in (("east", box(28.25, 38.25, -47, -17, 7.40, 9.40)),
               ("west", box(-38.25, -28.25, -47, -17, 7.40, 9.40))):
    ps = inter(case_nc, zb)
    print(f"  {nm}: {sum(p.volume for p in ps):.3f} mm3 (expect 0.000)")
