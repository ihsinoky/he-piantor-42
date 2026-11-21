import build123d as bd, json, math
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
byname = {e["name"]: i for i, e in enumerate(idx)}
def load(name): return bd.import_brep(f"{G17}/{byname[name]}.brep")
def mv(s, dx, dz=0): return s.moved(bd.Location((dx, 0, dz)))
CZ = 2.65
def inter(a,b):
    try: return a.intersect(b)
    except Exception: return None
def vol(r):
    if r is None: return 0.0
    return sum(s.volume for s in r.solids() if s.volume > 0.001)

wing = mv(load("wing_right"), 9.5)
mux  = mv(load("underside-right-U_MUX_C"), 9.5)
jw   = mv(load("underside-right-J_WING"), 9.5)
tabset = wing.fuse(mux).fuse(jw)

# Simpler: build swept envelope from discrete poses: rest, slid south 2.0, tipped 15/25/35 deg about south-end contact
def pose(slide=0.0, tip=0.0):
    # cell as a box-free cylinder: create along Y from yN to yS
    yN = -59.62 + slide; yS = -9.12 + slide
    zc = 7.40 + CZ
    c = bd.Solid.make_cylinder(7.25, 50.5).moved(bd.Location((0,0,0),(90,0,0)))
    bb = c.bounding_box()
    cx = (bb.min.X+bb.max.X)/2; cy = (bb.min.Y+bb.max.Y)/2; cz = (bb.min.Z+bb.max.Z)/2
    c = c.moved(bd.Location((15-cx, (yN+yS)/2 - cy, zc - cz)))
    if tip:
        # pivot: X-parallel axis at south end (y=yS), z = power board top +0.15 case
        piv = bd.Location((0, yS, 0.15 + CZ))
        c = c.moved(piv.inverse() if hasattr(piv,'inverse') else bd.Location((0,-yS,-(0.15+CZ))))
        c = c.moved(bd.Location((0,0,0),(-tip,0,0)))
        c = c.moved(bd.Location((0, yS, 0.15 + CZ)))
    return c

env = None
for slide, tip in [(0,0),(2.0,0),(2.0,15),(2.0,25),(2.0,35)]:
    p = pose(slide, tip)
    env = p if env is None else env.fuse(p)
bb = env.bounding_box()
print("cell swept envelope bbox: X[%.2f,%.2f] Y[%.2f,%.2f] Zcase[%.2f,%.2f]" % (bb.min.X, bb.max.X, bb.min.Y, bb.max.Y, bb.min.Z-CZ, bb.max.Z-CZ))
print("cell envelope vs tabset vol:", round(vol(inter(env, tabset)), 3))

def fbox(x0,x1,y0,y1,z0,z1):
    return bd.Solid.make_box(x1-x0, y1-y0, z1-z0).moved(bd.Location((x0,y0,z0+CZ)))
# finger zone east of east cell: X 22.25..32.25, Y cell length, Z 7.40..16.65 (centreline grip)
fz = fbox(22.25, 32.25, -59.62, -9.12, 7.40, 16.65)
print("finger(centreline) vs tabset vol:", round(vol(inter(fz, tabset)), 3))
print("finger(centreline) vs wing board vol:", round(vol(inter(fz, wing)), 3))
# strict variant: Z down to 3.00
fz2 = fbox(22.25, 32.25, -59.62, -9.12, 3.00, 16.65)
print("finger(strict Z>=3.0) vs tabset vol:", round(vol(inter(fz2, tabset)), 3))
r = inter(fz2, wing)
if r:
    for s in r.solids():
        if s.volume > 0.01:
            b2 = s.bounding_box()
            print("  strict vs board: vol %.2f X[%.2f,%.2f] Y[%.2f,%.2f] Zcase[%.2f,%.2f]" % (s.volume, b2.min.X, b2.max.X, b2.min.Y, b2.max.Y, b2.min.Z-CZ, b2.max.Z-CZ))
r = inter(fz2, mux)
print("finger(strict) vs MUX body vol:", round(vol(r),3))
r = inter(fz2, jw)
print("finger(strict) vs J_WING env vol:", round(vol(r),3))

r = inter(env, tabset)
print("--- cell envelope vs tabset intersection solids ---")
if r:
    for s in r.solids():
        if s.volume > 0.01:
            b3 = s.bounding_box()
            print("vol %.3f X[%.2f,%.2f] Y[%.2f,%.2f] Zcase[%.2f,%.2f]" % (s.volume, b3.min.X, b3.max.X, b3.min.Y, b3.max.Y, b3.min.Z-CZ, b3.max.Z-CZ))
for nm, body in [("wing", wing), ("mux", mux), ("jwing", jw)]:
    print("env vs", nm, round(vol(inter(env, body)), 3))
