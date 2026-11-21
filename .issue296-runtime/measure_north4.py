"""Precise north-side profile measurement (BREP):
1. Face sampling tray-right / strip-right: Ymin per 2mm X column + face-band Z extent.
2. Circle fit of the plan arc.
3. Strip slope profile: top Z vs Y at X stations.
4. Shell-central: north edge straightness + top profile."""
import build123d as bd
import numpy as np, os

ASM = os.path.expanduser("~/workspace/projects/he-piantor-case296b/.issue296-runtime/asm3d")

def box(x0,x1,y0,y1,z0,z1):
    return bd.Solid.make_box(x1-x0, y1-y0, z1-z0, bd.Plane(origin=(x0,y0,z0)))

def inter(s, b):
    r = s.intersect(b)
    if r is None: return []
    return list(r) if isinstance(r, (list, bd.ShapeList)) else [r]

def sample_face(part, x0, x1, step=2.0):
    rows = []
    x = x0
    while x < x1:
        cells = inter(part, box(x, x+step, -70, -30, -3, 23))
        if cells:
            ymin = min(c.bounding_box().min.Y for c in cells)
            band = inter(part, box(x, x+step, ymin-0.1, ymin+2.0, -3, 23))
            if band:
                zmin = min(c.bounding_box().min.Z for c in band)
                zmax = max(c.bounding_box().max.Z for c in band)
            else:
                zmin = zmax = float('nan')
            rows.append((x+step/2, ymin, zmin, zmax))
        x += step
    return rows

tray = bd.import_brep(f"{ASM}/tray-right.brep")
strip = bd.import_brep(f"{ASM}/strip-right.brep")
shell = bd.import_brep(f"{ASM}/shell-central.brep")

print("== tray-right face (x, Ymin, face-band Zmin..Zmax) ==")
tr = sample_face(tray, 31, 125)
for r in tr: print(f"  {r[0]:6.1f}  {r[1]:8.2f}  {r[2]:6.2f}..{r[3]:6.2f}")
print("== strip-right face ==")
sr = sample_face(strip, 31, 125)
for r in sr: print(f"  {r[0]:6.1f}  {r[1]:8.2f}  {r[2]:6.2f}..{r[3]:6.2f}")

# circle fit on tray face points with -64 < Y < -50 (the arc span)
pts = np.array([(x, y) for x, y, _, _ in tr if -64.0 < y < -50.0])
A = np.c_[2*pts[:,0], 2*pts[:,1], np.ones(len(pts))]
b = pts[:,0]**2 + pts[:,1]**2
sol, *_ = np.linalg.lstsq(A, b, rcond=None)
cx, cy, c = sol
R = np.sqrt(c + cx**2 + cy**2)
resid = np.abs(np.hypot(pts[:,0]-cx, pts[:,1]-cy) - R)
print(f"\nARC FIT: centre ({cx:.2f}, {cy:.2f})  R {R:.2f}  max resid {resid.max():.3f}  n={len(pts)}")

print("\n== strip-right slope profile: Zmax per 3mm Y band (from face southward) ==")
for xst in [40, 70, 100]:
    face = min(y for x, y, _, _ in sr if abs(x-xst) <= 2)
    row = []
    for dy in range(0, 30, 3):
        cells = inter(strip, box(xst-1, xst+1, face+dy, face+dy+3, -3, 23))
        row.append(f"Y{face+dy:6.1f}: {max((c.bounding_box().max.Z for c in cells), default=float('nan')):5.2f}")
    print(f" X~{xst} face {face:.2f}: " + "  ".join(row))

print("\n== shell-central: Ymin per 5mm X bin ==")
x = -40
out = []
while x < 40:
    cells = inter(shell, box(x, x+5, -70, 90, -3, 23))
    if cells: out.append(f"X{x+2.5:6.1f}: {min(c.bounding_box().min.Y for c in cells):7.2f}")
    x += 5
print("  " + "  ".join(out))
print("== shell-central top profile: Zmax per 5mm Y band at X~-2..2 ==")
row = []
y = -0.37
while y < 85:
    cells = inter(shell, box(-2, 2, y, y+5, -3, 23))
    if cells: row.append(f"Y{y+2.5:5.1f}: {max(c.bounding_box().max.Z for c in cells):5.2f}")
    y += 5
print("  " + "  ".join(row))
