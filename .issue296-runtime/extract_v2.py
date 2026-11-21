"""Extract real geometry for the v2 figures -> geom_v2.json.
Run with the cad-venv python (build123d).
Sources: geometry17 BREP body set (issue-232-final 17mm assembly).
Frame: asm frame (X east, Y south). g17 Z -> case Z: subtract 2.65.
Stage B poses: tray/plate/strip halves shift +-9.5 in X (delta=9.5).
"""
import build123d as bd
import json, math

G17 = "/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/phaseb/geometry17"
idx = json.load(open(G17 + "/index.json"))
pos = {e["name"]: i for i, e in enumerate(idx)}
ZC = 2.65  # g17 Z - 2.65 = case Z

def load(name):
    return bd.import_brep(f"{G17}/{pos[name]}.brep")

def shifted(solid, dx):
    return solid.moved(bd.Location((dx, 0, 0))) if dx else solid

def edge_polylines(solid, step=1.5):
    """Project all edges of a solid onto XY as sampled polylines."""
    out = []
    for e in solid.edges():
        try:
            L = e.length
            n = max(2, min(200, int(L / step) + 1))
            pts = []
            for i in range(n + 1):
                p = e.position_at(i / n)
                pts.append([round(p.X, 3), round(p.Y, 3)])
            out.append(pts)
        except Exception:
            pass
    return out

def face_wire_pts(face):
    """Outer wire of a planar face as (points, [inner wires points])."""
    def wire_pts(w):
        pts = []
        for e in w.edges():
            n = max(2, int(e.length / 1.0) + 1)
            for i in range(n):
                p = e.position_at(i / n)
                pts.append([round(p.X, 3), round(p.Y, 3), round(p.Z, 3)])
        return pts
    outer = wire_pts(face.outer_wire())
    inners = [wire_pts(w) for w in face.inner_wires()]
    return outer, inners

def top_outline(solid):
    """Outer wire of the largest horizontal face at the solid's top."""
    best = None
    for f in solid.faces():
        n = f.normal_at()
        if abs(n.Z) > 0.99 and f.center().Z > 3:
            if best is None or f.area > best.area:
                best = f
    outer, inners = face_wire_pts(best)
    holes = []
    for w in inners:
        xs = [p[0] for p in w]; ys = [p[1] for p in w]
        cx, cy = sum(xs) / len(xs), sum(ys) / len(ys)
        r = max(max(xs) - min(xs), max(ys) - min(ys)) / 2
        if r < 4:
            holes.append([round(cx, 2), round(cy, 2), round(r, 2)])
    return [[p[0], p[1]] for p in outer], holes

def section_polys(solid, axis, at, half=0.25):
    """Intersect solid with a thin slab centred on the cut plane; return
    the faces lying on the lower slab plane as polygons in (u, caseZ)."""
    if axis == "Y":  # cut plane Y=at, profile coords (X, Z)
        slab = bd.Solid.make_box(500, 2 * half, 80, bd.Plane(origin=(-250, at - half, -5)))
        pick = lambda p: [p[0], p[2] - ZC]
        tol_ok = lambda f: abs(f.center().Y - (at - half)) < 0.05
    else:  # cut plane X=at, profile coords (Y, Z)
        slab = bd.Solid.make_box(2 * half, 500, 80, bd.Plane(origin=(at - half, -250, -5)))
        pick = lambda p: [p[1], p[2] - ZC]
        tol_ok = lambda f: abs(f.center().X - (at - half)) < 0.05
    inter = solid.intersect(slab)
    polys = []
    if not inter:
        return polys
    for f in inter.faces():
        if tol_ok(f) and f.area > 0.05:
            outer, inners = face_wire_pts(f)
            polys.append({"outer": [pick(p) for p in outer],
                          "inners": [[pick(p) for p in w] for w in inners]})
    return polys

out = {}

# --- case projected edges (top view) ---
case_edges = {}
for name, dx in [("tray-left", -9.5), ("tray-right", 9.5),
                 ("shell-central", 0), ("strip-left", -9.5), ("strip-right", 9.5)]:
    case_edges[name] = edge_polylines(shifted(load(name), dx))
out["case_edges"] = case_edges

# --- plate outlines (top face) + notch applied later in render ---
plates = {}
for name, dx in [("plate-left", -9.5), ("plate-right", 9.5)]:
    o, holes = top_outline(load(name))
    plates[name] = {"outer": [[round(x + dx, 3), y] for x, y in o],
                    "holes": [[round(x + dx, 2), y, r] for x, y, r in holes]}
out["plates"] = plates

# --- Fly outline at relocated position (centre 0,-50.14 -> 38,-50.14) ---
fly = load("Fly-official-00-instance-0")
o, _ = top_outline(fly)
out["fly_outer"] = [[round(x + 38, 3), y] for x, y in o]

# --- sections ---
secA = {}  # E-W at Y=-34.37
for name, dx in [("tray-left", -9.5), ("tray-right", 9.5), ("shell-central", 0)]:
    secA[name] = section_polys(shifted(load(name), dx), "Y", -34.37)
out["secA"] = secA
secB = {}  # N-S at X=0
for name, dx in [("tray-left", -9.5), ("tray-right", 9.5), ("shell-central", 0)]:
    secB[name] = section_polys(shifted(load(name), dx), "X", 0.0)
out["secB"] = secB

json.dump(out, open(".issue296-runtime/geom_v2.json", "w"))
print("written", {k: (len(v) if isinstance(v, (list, dict)) else v) for k, v in out.items()})
