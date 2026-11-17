"""Stage 2b geometry core: build Rev.9 Main / Rev.6 Wing outline polygons
(board frame) from the approved Stage 2a spec, and check the outline
deltas against ALL copper incl. zone fills and zone outline polygons."""
import json, math, sys
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union, polygonize
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
RT = "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime"
Q263 = "/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-263-implementation"
GAP = 0.55
DEPTH = 4.738
FRONT_HALF = 16.689 / 2
BASE_HALF = 22.160 / 2

def xy(v):
    return (v.x / MM, v.y / MM)

def outline_of(board):
    segs = []
    for d in board.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            if d.GetShape() == p.SHAPE_T_ARC:
                # sample arcs densely (chord err << 1 um at these radii)
                c = d.GetCenter(); r = d.GetRadius() / MM
                a0 = math.atan2(d.GetStart().y - c.y, d.GetStart().x - c.x)
                # use arc mid to fix direction
                m = d.GetArcMid(); a1 = math.atan2(m.y - c.y, m.x - c.x)
                a2 = math.atan2(d.GetEnd().y - c.y, d.GetEnd().x - c.x)
                def norm(a):
                    while a < a0 - 1e-9: a += 2 * math.pi
                    while a > a0 + 2 * math.pi: a -= 2 * math.pi
                    return a
                a1n, a2n = norm(a1), norm(a2)
                if abs((a2n - a0) - 2 * ((a1n - a0))) > 0.2 and (a2n - a0) > math.pi:
                    a2n -= 2 * math.pi
                n = max(4, int(abs(a2n - a0) / 0.05))
                pts = [(c.x / MM + r * math.cos(a0 + (a2n - a0) * i / n),
                        c.y / MM + r * math.sin(a0 + (a2n - a0) * i / n)) for i in range(n + 1)]
                for a, b in zip(pts[:-1], pts[1:]):
                    segs.append(LineString([a, b]))
            else:
                segs.append(LineString([xy(d.GetStart()), xy(d.GetEnd())]))
    polys = list(polygonize(unary_union(segs)))
    polys.sort(key=lambda q: -q.area)
    return polys[0]

def polys_of(ps):
    def ring(line):
        return [(line.CPoint(i).x / MM, line.CPoint(i).y / MM) for i in range(line.PointCount())]
    parts = []
    for i in range(ps.OutlineCount()):
        holes = [ring(ps.Hole(i, j)) for j in range(ps.HoleCount(i))]
        parts.append(Polygon(ring(ps.Outline(i)), holes))
    return unary_union([q for q in parts if q.area > 0])

def copper_items(board):
    """(name, shapely geom) for tracks, vias, pads, zone fills, zone outlines."""
    items = []
    for t in board.GetTracks():
        s, e = xy(t.GetStart()), xy(t.GetEnd())
        if isinstance(t, p.PCB_VIA):
            items.append(("via", Point(s).buffer(t.GetWidth() / MM / 2)))
        else:
            items.append(("track", LineString([s, e]).buffer(t.GetWidth() / MM / 2)))
    for f in board.GetFootprints():
        for a in f.Pads():
            for l in (p.F_Cu, p.B_Cu):
                if a.IsOnLayer(l):
                    ps = p.SHAPE_POLY_SET()
                    a.TransformShapeToPolygon(ps, l, 0, 10, p.ERROR_OUTSIDE)
                    items.append(("pad", polys_of(ps)))
    for z in board.Zones():
        fp = z.GetFilledPolysList(z.GetFirstLayer())
        # filled polys per layer: iterate all copper layers of the zone
        for l in z.GetLayerSet().Seq():
            try:
                items.append(("fill", polys_of(z.GetFilledPolysList(l))))
            except Exception:
                pass
        items.append(("zonepoly", polys_of(z.Outline())))
    return items

# ---------- Main Rev.9 outline (board frame) ----------
sites = json.loads(open(f"{RT}/sites.json").read())
g = json.loads(open(f"{RT}/geometry.json").read())

def site_frame(site):
    A = site["A"]; u = site["u"]; n = site["n"]
    return A, u, n

def td_to_case(site, t, d):
    A, u, n = site_frame(site)
    return (A[0] + t * u[0] + d * n[0], A[1] + t * u[1] + d * n[1])

def trapezoid_case(site, tc):
    pts = [td_to_case(site, tc - BASE_HALF, 0), td_to_case(site, tc + BASE_HALF, 0),
           td_to_case(site, tc + FRONT_HALF, DEPTH), td_to_case(site, tc - FRONT_HALF, DEPTH)]
    return Polygon(pts)

# stage-1 frame tab centres: J2 42.973 (front [34.628,51.317]), J3 24.993 (front [16.648,33.337])
TC = {"J2": 42.973, "J3": 24.993}
rev7_case = Polygon(g["main_rev7_outline"])
traps = [trapezoid_case(sites[s], TC[s]) for s in ("J2", "J3")]
main_new_case = unary_union([rev7_case] + traps)
main_new_board = shp_translate(main_new_case, xoff=100.0, yoff=70.0)

if __name__ == "__main__":
    print("trapezoid corners (board):")
    for s in ("J2", "J3"):
        pts = []
        for t, d in ((TC[s] - BASE_HALF, 0), (TC[s] + BASE_HALF, 0), (TC[s] + FRONT_HALF, DEPTH), (TC[s] - FRONT_HALF, DEPTH)):
            c = td_to_case(sites[s], t, d)
            pts.append((round(c[0] + 100, 4), round(c[1] + 70, 4)))
        print(s, pts)
    print("main_new area (expect 2642.6):", round(main_new_board.area, 2))
    b = p.LoadBoard(f"{Q263}/main-rev8/main.kicad_pcb")
    rev8 = outline_of(b)
    print("rev8 area:", round(rev8.area, 2))
    growth = main_new_board.difference(rev8)
    removed = rev8.difference(main_new_board)
    print("growth area:", round(growth.area, 4), "removed area:", round(removed.area, 6))
    items = copper_items(b)
    for name, region in (("growth", growth), ("removed", removed)):
        if region.area == 0:
            print(name, ": empty"); continue
        hits = {}
        for kind, geom in items:
            inter = geom.intersection(region)
            if inter.area > 1e-6:
                hits[kind] = hits.get(kind, 0) + inter.area
        print(name, "copper hits:", {k: round(v, 5) for k, v in hits.items()} or "NONE")
