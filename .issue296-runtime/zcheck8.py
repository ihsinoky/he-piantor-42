import build123d as bd, json
G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
byname = {e["name"]: i for i, e in enumerate(idx)}
def load(name): return bd.import_brep(f"{G17}/{byname[name]}.brep")
def mv(s, dx): return s.moved(bd.Location((dx, 0, 0)))
CZ = 2.65
def inter(a,b):
    try: return a.intersect(b)
    except Exception: return None
def vol(r):
    if r is None: return 0.0
    return sum(s.volume for s in r.solids() if s.volume > 0.001)
wing = mv(load("wing_right"), 9.5)
def pose(slide=0.0, tip=0.0, pivot="rim"):
    yN = -59.62 + slide; yS = -9.12 + slide
    zc = 7.40 + CZ
    c = bd.Solid.make_cylinder(7.25, 50.5).moved(bd.Location((0,0,0),(90,0,0)))
    bb = c.bounding_box()
    cx = (bb.min.X+bb.max.X)/2; cy = (bb.min.Y+bb.max.Y)/2; cz = (bb.min.Z+bb.max.Z)/2
    c = c.moved(bd.Location((15-cx, (yN+yS)/2 - cy, zc - cz)))
    if tip:
        pz = (0.15 + CZ) if pivot == "rim" else zc
        c = c.moved(bd.Location((0, -yS, -pz)))
        c = c.moved(bd.Location((0,0,0),(-tip,0,0)))
        c = c.moved(bd.Location((0, yS, pz)))
    return c
for pivot in ("rim", "centre"):
    for tip in (10, 15, 20, 25, 35):
        env = pose(2.0, 0)
        env = env.fuse(pose(2.0, tip, pivot))
        v = vol(inter(env, wing))
        print("pivot %-6s tip %2d deg: env vs wing board vol %.3f" % (pivot, tip, v))
