"""Wing Rev.6 notch chain geometry (case frame), shared by build/verify.

The new notch floor is the exact 0.55 mm offset of the IMPLEMENTED
Rev.9 Main outline around the tab: entry line (offset of the Main
slanted edge) -> R0.55 arc (base corner) -> wall line -> R0.55 arc
(front corner) -> front line -> R0.55 arc -> wall line -> R0.55 arc
-> entry line, clipped where it crosses the current Wing outline
(S1/S2). Elements are built analytically from the Rev.9 board's own
tab vertices; correctness is verified against the shapely buffer
construction in the build script.
"""
import math
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union, polygonize
from shapely.affinity import rotate as shp_rotate

MM = 1e6
GAP = 0.55

def wing_xf_factory(board, side):
    jf = [x for x in board.GetFootprints() if x.GetReference() == "J_WING"][0]
    jx, jy = jf.GetPosition().x / MM, jf.GetPosition().y / MM
    deg, env = (30.5, (-27.0, -37.5)) if side == "left" else (-30.5, (27.0, -37.5))
    def fwd(pt):
        q = shp_rotate(Point(pt[0] - jx, pt[1] - jy), deg, origin=(0, 0))
        return (q.x + env[0], q.y + env[1])
    def inv(pt):
        q = shp_rotate(Point(pt[0] - env[0], pt[1] - env[1]), -deg, origin=(0, 0))
        return (q.x + jx, q.y + jy)
    return fwd, inv, (jx, jy)

def offset_line(p1, p2, away_from):
    """Line through p1,p2 shifted so its distance to `away_from` grows by GAP:
    returns (a, b) points on the offset line (same direction)."""
    import numpy as np
    p1, p2, c = np.array(p1, float), np.array(p2, float), np.array(away_from, float)
    d = p2 - p1; d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    if np.dot(c - p1, n) > 0:
        n = -n  # n now points away from the interior point
    return (tuple(p1 + n * GAP), tuple(p2 + n * GAP))

def foot(c, line):
    import numpy as np
    a, b = np.array(line[0], float), np.array(line[1], float)
    c = np.array(c, float)
    d = b - a; d = d / np.linalg.norm(d)
    return tuple(a + d * np.dot(c - a, d))

def build_chain(tab, interior_pt):
    """tab: dict with case-frame corners base1, front1, front2, base2 in
    traversal order around the tab (base1..base2 along the Main edge).
    Returns ordered elements: ('line', a, b) / ('arc', centre, r, a, b, mid).
    Entry lines are extended 20 mm past the base corners."""
    import numpy as np
    b1, f1, f2, b2 = tab["base1"], tab["front1"], tab["front2"], tab["base2"]
    edge = (b1, b2)
    e_off = offset_line(b1, b2, interior_pt)
    w1_off = offset_line(b1, f1, interior_pt)
    fr_off = offset_line(f1, f2, interior_pt)
    w2_off = offset_line(f2, b2, interior_pt)
    def ext(line, at, dist):
        a, b = np.array(line[0], float), np.array(line[1], float)
        d = b - a; d = d / np.linalg.norm(d)
        return tuple(np.array(at, float) + d * dist)
    # tangent points: foot of each corner on the two adjacent offset lines
    t_b1_e = foot(b1, e_off); t_b1_w = foot(b1, w1_off)
    t_f1_w = foot(f1, w1_off); t_f1_f = foot(f1, fr_off)
    t_f2_f = foot(f2, fr_off); t_f2_w = foot(f2, w2_off)
    t_b2_w = foot(b2, w2_off); t_b2_e = foot(b2, e_off)
    def arc(c, a, b):
        ca, cb = np.array(a, float) - np.array(c, float), np.array(b, float) - np.array(c, float)
        aa, ab = math.atan2(ca[1], ca[0]), math.atan2(cb[1], cb[0])
        # choose the sweep that stays outside the tab (away from interior)
        while ab - aa > math.pi: ab -= 2 * math.pi
        while ab - aa < -math.pi: ab += 2 * math.pi
        mid_ang = (aa + ab) / 2
        mid = (c[0] + GAP * math.cos(mid_ang), c[1] + GAP * math.sin(mid_ang))
        if Point(mid).distance(Point(interior_pt)) < Point(a).distance(Point(interior_pt)):
            mid_ang += math.pi
            mid = (c[0] + GAP * math.cos(mid_ang), c[1] + GAP * math.sin(mid_ang))
        return ("arc", c, GAP, a, b, mid)
    s1 = ext(e_off, t_b1_e, -20.0)
    s2 = ext(e_off, t_b2_e, 20.0)
    return [("line", s1, t_b1_e), arc(b1, t_b1_e, t_b1_w), ("line", t_b1_w, t_f1_w),
            arc(f1, t_f1_w, t_f1_f), ("line", t_f1_f, t_f2_f), arc(f2, t_f2_f, t_f2_w),
            ("line", t_f2_w, t_b2_w), arc(b2, t_b2_w, t_b2_e), ("line", t_b2_e, s2)]

def chain_linestring(elements, arc_steps=24):
    pts = []
    for el in elements:
        if el[0] == "line":
            seg = [el[1], el[2]]
        else:
            _, c, r, a, b, _ = el
            aa = math.atan2(a[1] - c[1], a[0] - c[0])
            ab = math.atan2(b[1] - c[1], b[0] - c[0])
            while ab - aa > math.pi: ab -= 2 * math.pi
            while ab - aa < -math.pi: ab += 2 * math.pi
            # match the mid-side chosen in build_chain: sample and keep as-is;
            # the mid check there guarantees the short outside sweep
            seg = [(c[0] + r * math.cos(aa + (ab - aa) * i / arc_steps),
                    c[1] + r * math.sin(aa + (ab - aa) * i / arc_steps)) for i in range(arc_steps + 1)]
        if pts and seg[0] == pts[-1]:
            seg = seg[1:]
        pts.extend(seg)
    return LineString(pts)
