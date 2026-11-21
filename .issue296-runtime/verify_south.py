"""Issue #296 — south unification (plan A) verification.
Regression is covered by verify_p0p1.py run unchanged; this script
adds the south-specific checks:
S1. south profile re-extraction (whole case + per part) and the
    R1/R2/R3 closure values; arc-zone fit against the refit diagonal
S2. C0.5 chamfer line (top slab profile)
S3. south band surface (top Z along the band), skin underside,
    antenna cavity hollow, band depth, Main plan gaps
S4. skin joints: shell<->skin and plate<->skin distances (~0.30)
"""
import build123d as bd
import json, os, math

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")
RT = os.path.dirname(os.path.abspath(__file__))
ZC = 2.65

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
    return max((c.bounding_box().max.Y for c in cs), default=None)

tray_l, tray_r, infill = part("tray-left"), part("tray-right"), part("centre-infill")
shell = part("shell-central")
shelf = part("north-shelf")
plate_l, plate_r = part("plate-left"), part("plate-right")
plunger, pipe = part("plunger-sw1"), part("light-pipe-dled")
case_all = tray_l.fuse(tray_r).fuse(infill).fuse(shell).fuse(shelf) \
    .fuse(plate_l).fuse(plate_r).fuse(plunger).fuse(pipe)

print("== S1. south profile (0.5 mm slabs, full Z) ==")
prof = {}
for x in [0.25 + 0.5 * k for k in range(0, 170)]:
    prof[x] = southmost(case_all, x - 0.25, x + 0.25, -5.0, 55.0)
straight = [prof[x] for x in prof if x <= 58.25]
print(f"straight zone |X|<=58.25: min {min(straight):.3f} max {max(straight):.3f}"
      f" (expect 81.700 / 81.700)")
for x in (50.25, 54.25, 57.25, 58.75, 59.25, 59.75, 60.25, 60.75, 61.25):
    print(f"  profile |X|={x:6.2f}: {prof[x]:.3f}   (pre-change R1 bottom was"
          f" 74.286 at 50.25; shoulder peak 81.702 at ~57.75)")
# refit the diagonal on the NEW profile and compare the arc zone
pts = [(x, prof[x]) for x in prof if 62.0 <= x <= 76.0 and prof[x] is not None]
n = len(pts)
sx = sum(p[0] for p in pts); sy = sum(p[1] for p in pts)
sxx = sum(p[0] ** 2 for p in pts); sxy = sum(p[0] * p[1] for p in pts)
MD = (n * sxy - sx * sy) / (n * sxx - sx * sx)
AD = (sy - MD * sx) / n
YS, R = 81.700, 4.0
XI = (YS - AD) / MD
TH = math.atan(-MD)
TL = R * math.tan(TH / 2)
XT1 = XI - TL
CY = YS - R
print(f"refit diagonal Y = {AD:.4f} {MD:+.4f}|X| -> Xi {XI:.3f}, Xt1 {XT1:.3f}")
worst = 0.0
for x in (58.75, 59.25, 59.75, 60.25):
    arc = CY + math.sqrt(max(R ** 2 - (x - XT1) ** 2, 0.0))
    d = prof[x] - arc
    worst = max(worst, abs(d))
    print(f"  arc zone |X|={x:6.2f}: profile {prof[x]:.3f} vs arc {arc:.3f}"
          f" (diff {d:+.3f})")
print(f"arc zone max |diff| (profile is a 0.5-slab max, arc is the"
      f" centreline value): {worst:.3f}")

print("\n-- shell south edge (R2) --")
for x in (0.25, 10.25, 20.25, 30.25, 38.25, 39.25, 40.25, 41.25):
    v = southmost(shell, x - 0.25, x + 0.25, -5.0, 55.0)
    print(f"  shell |X|={x:6.2f}: {v if v is None else round(v, 3)}"
          f"   (expect 69.700; pre-change 69.202 centre / 69.700 corners)")

print("\n== S2. chamfer (top slab Z 10.85..10.95) ==")
for x in (-30.25, 0.25, 30.25, 55.25):
    v = southmost(case_all, x - 0.25, x + 0.25, 10.85, 10.95)
    print(f"  top-slab southmost |X|={x:6.2f}: {v if v is None else round(v, 3)}"
          f"   (chamfer line at slab bottom Z=10.85 gives 81.250)")

print("\n== S3. band surface / cavity / Main gaps ==")
for X in (0.0, 30.0, 45.0):
    tops = []
    y = 70.0
    while y < 81.7:
        cs = cells_of(case_all.intersect(box(X - 0.5, X + 0.5, y, y + 1.0, -3.0, 23.0)))
        tops.append(None if not cs else round(max(c.bounding_box().max.Z for c in cs), 2))
        y += 1.0
    print(f"  band top Z at X={X}: {tops} (expect 10.90 throughout"
          f" Y 70..81.7; pre-change trench floor -0.65 at X=0/30/45)")
# cavity at X=0: material between floor and skin underside?
cs = cells_of(case_all.intersect(box(-0.5, 0.5, 70.0, 79.7, 0.0, 9.30)))
print(f"  antenna cavity X=0, Y 70..79.7, Z 0..9.30: material volume"
      f" {sum(c.volume for c in cs):.3f} mm3 (expect 0 = hollow)")
cs = cells_of(case_all.intersect(box(-0.5, 0.5, 70.0, 79.7, 9.0, 11.5)))
print(f"  skin slab X=0, Y 70..79.7, Z 9..11.5: Z range"
      f" {min(c.bounding_box().min.Z for c in cs):.2f}.."
      f"{max(c.bounding_box().max.Z for c in cs):.2f} (expect 9.30..10.90)")
# wall inner face at X=0 (Z restricted so the trench floor is excluded)
cs = cells_of(case_all.intersect(box(-0.5, 0.5, 75.0, 82.0, 0.0, 10.90)))
wall_inner = min(c.bounding_box().min.Y for c in cs)
segs = json.load(open(os.path.join(RT, "main-outline-asm.json")))
main_south = max(max(s[0][1], s[1][1]) for s in segs)
main_south_xs = sorted({round(s[i][0], 2) for s in segs for i in (0, 1)
                        if abs(s[i][1] - main_south) < 0.01})
print(f"  Main south edge Y = {main_south:.3f} at X {main_south_xs}")
print(f"  wall inner face at X=0: {wall_inner:.3f} -> antenna band depth"
      f" {wall_inner - main_south:.3f} (expect 11.80)")
print(f"  Main south edge -> outer line: {81.700 - main_south:.3f}"
      f" (expect 13.80); shell edge 69.700 -> plan gap"
      f" {69.700 - main_south:.3f}; skin boundary 70.000 -> gap"
      f" {70.000 - main_south:.3f}")

print("\n== S4. skin joints ==")
skin_c = cells_of(infill.intersect(box(-20.0, 20.0, 69.0, 82.0, 9.0, 11.5)))
if skin_c:
    sk = skin_c[0]
    for c in skin_c[1:]:
        sk = sk.fuse(c)
    print(f"  shell <-> centre skin min distance {shell.distance_to(sk):.3f}"
          f" (expect 0.300)")
skin_r = cells_of(tray_r.intersect(box(45.0, 60.0, 60.0, 82.0, 9.0, 11.5)))
pl_r = cells_of(plate_r.intersect(box(45.0, 60.0, 60.0, 82.0, 9.0, 11.5)))
if skin_r and pl_r:
    sk = skin_r[0]
    for c in skin_r[1:]:
        sk = sk.fuse(c)
    pl = pl_r[0]
    for c in pl_r[1:]:
        pl = pl.fuse(c)
    print(f"  plate-R <-> skin-R min distance {pl.distance_to(sk):.3f}"
          f" (expect ~0.300)")
print("verify_south done")
