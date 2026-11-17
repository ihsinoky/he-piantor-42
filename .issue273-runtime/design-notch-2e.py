"""Issue #273 Stage 2e design: Wing Rev.6 notch with GENUINELY simple
mouth transitions. Per variant, in case frame at the fitted pose:
floor = the Stage 2d offset lines (dive/front/rise at GAP 0.55 +
delta, corner fillets R0.55 reused exactly from notch2d.json);
the dive straight is EXTENDED to intersect the Wing's existing
inner edge E1 and the rise straight to intersect the existing far
edge E2 (both lines taken from the Rev.5 board's own long Edge.Cuts
elements), with ONE tangent fillet at each intersection (largest R
in 1.00..0.30 step 0.05 leaving >= 0.15 mm of straight; if no R
fits, a sharp corner is recorded with the geometric reason).
The new outline is built by REPLACING the Rev.5 ring arc between
the two fillet tangent points with the new chain - NOT by keepout
difference - so no Rev.5 mouth geometry survives.
Checks: seam >= 0.550 vs the final Rev.9 outline (this worktree),
overlap 0, inside D-037 silhouette, removed-region copper = fills
only, added-region copper = none. Writes notch2e.json."""
import json, math, sys
from pathlib import Path
import numpy as np
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
SRT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
sys.path.insert(0, str(SRT))
from geom2b import copper_items
from notchain import wing_xf_factory

Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
Q270M = W / "hardware/kicad/qualification/issue-270-main-rev9/main-rev9"
ND = json.loads((SRT / "notch2d.json").read_text())
case = json.loads((SRT / "case_geometry.json").read_text())
SIL = unary_union([Polygon(q) for q in case["silhouette_parts"]])
GAP = 0.55
RESID = 0.15

def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM)
                    for j in range(ch.PointCount())])

MAIN = shp_translate(outline_kicad(p.LoadBoard(str(Q270M / "main.kicad_pcb"))),
                     xoff=-100.0, yoff=-70.0)

def unit(v):
    v = np.array(v, float)
    return v / np.linalg.norm(v)

def line_x(p1, d1, p2, d2):
    den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
    return np.array(p1, float) + np.array(d1, float) * t

def fillet(I, u1, u2, R):
    """Tangent arc at intersection I; u1/u2 = unit vectors AWAY from
    I along the incoming/outgoing lines. Returns dict or None."""
    u1, u2 = unit(u1), unit(u2)
    cos = float(np.clip(np.dot(u1, u2), -1, 1))
    alpha = math.acos(cos)
    if alpha < 0.05 or alpha > math.pi - 0.05:
        return None
    Lt = R / math.tan(alpha / 2)
    Ta = np.array(I, float) + u1 * Lt
    Tb = np.array(I, float) + u2 * Lt
    bis = unit(u1 + u2)
    O = np.array(I, float) + bis * (R / math.sin(alpha / 2))
    mid = O + R * unit(np.array(I, float) - O)
    return dict(Ta=tuple(Ta), Tb=tuple(Tb), O=tuple(O), mid=tuple(mid),
                Lt=Lt, alpha_deg=math.degrees(alpha))

def arc_pts(O, r, a, b):
    a0 = math.atan2(a[1] - O[1], a[0] - O[0])
    a1 = math.atan2(b[1] - O[1], b[0] - O[0])
    while a1 - a0 > math.pi: a1 -= 2 * math.pi
    while a1 - a0 < -math.pi: a1 += 2 * math.pi
    n = max(8, int(abs(a1 - a0) / 0.01))
    return [tuple(O + r * np.array([math.cos(a0 + (a1 - a0) * i / n),
                                    math.sin(a0 + (a1 - a0) * i / n)]))
            for i in range(n + 1)]

results = {}
for variant in ("17mm-left", "17mm-right", "16mm-left", "16mm-right"):
    pitch, side = variant.split("-")
    site = "J2" if side == "left" else "J3"
    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    deg = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    def to_case(poly):
        q = shp_translate(poly, xoff=-jw[0], yoff=-jw[1])
        q = shp_rotate(q, deg, origin=(0, 0))
        return shp_translate(q, xoff=env[0], yoff=env[1])
    def pt_case(pt):
        q = shp_translate(Point(pt), xoff=-jw[0], yoff=-jw[1])
        q = shp_rotate(q, deg, origin=(0, 0))
        q = shp_translate(q, xoff=env[0], yoff=env[1])
        return (q.x, q.y)
    wing_old = to_case(outline_kicad(b5))
    nd = ND[variant]
    els_nd = nd["elements_case"]
    # floor lines/arcs from the 2d design (exact reuse)
    Ld_p, Ld_d = np.array(els_nd[0][1], float), unit(np.array(els_nd[0][2], float) - np.array(els_nd[0][1], float))
    A1 = els_nd[1]; Lf_a, Lf_b = np.array(els_nd[2][1], float), np.array(els_nd[2][2], float)
    Lf_d = unit(Lf_b - Lf_a)
    A2 = els_nd[3]
    Lr_p, Lr_d = np.array(els_nd[4][1], float), unit(np.array(els_nd[4][2], float) - np.array(els_nd[4][1], float))
    T1a, T1b = np.array(A1[3], float), np.array(A1[4], float)
    T2a, T2b = np.array(A2[3], float), np.array(A2[4], float)
    I1 = line_x(Ld_p, Ld_d, Lf_a, Lf_d)
    I2 = line_x(Lf_a, Lf_d, Lr_p, Lr_d)
    chain_union = unary_union([LineString([els_nd[0][1], els_nd[0][2]]),
                               LineString([Lf_a, Lf_b]),
                               LineString([els_nd[4][1], els_nd[4][2]])])
    # flank edges: Rev.5 long line elements near the design chain
    flanks = []
    for d in b5.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts or str(d.GetShape()) not in ("0", "SEGMENT"):
            continue
        s = pt_case((d.GetStart().x / MM, d.GetStart().y / MM))
        e = pt_case((d.GetEnd().x / MM, d.GetEnd().y / MM))
        if math.dist(s, e) >= 15.0 and LineString([s, e]).distance(chain_union) < 6.0 \
                and max(Point(s).distance(chain_union), Point(e).distance(chain_union)) > 10.0:
            flanks.append((np.array(s), np.array(e)))
    assert len(flanks) == 2, f"{variant}: {len(flanks)} flank candidates"
    # assign dive/rise flanks: the dive flank is the one whose
    # SEGMENT contains the dive-line intersection A (the two flanks
    # can be collinear - both on the Wing's one long edge line - so
    # line-intersection proximity alone ties; segment containment
    # is the discriminator)
    cand = []
    for s, e in flanks:
        d = unit(e - s)
        x = line_x(Ld_p, Ld_d, s, d)
        segdist = LineString([s, e]).distance(Point(x))
        cand.append((segdist, float(np.linalg.norm(x - I1)), (s, e), x))
    cand.sort(key=lambda c: (round(c[0], 6), c[1]))
    assert cand[0][0] < 0.01 and cand[0][1] < 6.0, \
        f"{variant}: dive flank segdist {cand[0][0]:.3f} distI1 {cand[0][1]:.2f}"
    (E1s, E1e), A_pt = cand[0][2], cand[0][3]
    (E2s, E2e) = cand[1][2]
    # headings from the FAR endpoint of each flank segment: hE1 points
    # toward the notch (toward A), hE2 away from the notch (from K2)
    far1 = E1s if np.linalg.norm(A_pt - E1s) > np.linalg.norm(A_pt - E1e) else E1e
    hE1 = unit(A_pt - far1)
    K2_pt = line_x(Lr_p, Lr_d, E2s, unit(E2e - E2s))
    far2 = E2s if np.linalg.norm(K2_pt - E2s) > np.linalg.norm(K2_pt - E2e) else E2e
    hE2 = unit(far2 - K2_pt)
    assert LineString([E2s, E2e]).distance(Point(K2_pt)) < 0.01, f"{variant}: K2 off E2 segment"
    hRise = unit(K2_pt - T2b)
    dDive = unit(I1 - A_pt)
    run_dive = float(np.linalg.norm(T1a - A_pt))
    run_rise = float(np.linalg.norm(K2_pt - T2b))
    def pick(I, u1, u2, run):
        for ri in range(20, 5, -1):
            R = ri * 0.05
            f = fillet(I, u1, u2, R)
            if f and run - f["Lt"] >= RESID:
                return R, f
        return None, None
    R_d, F_d = pick(A_pt, -hE1, dDive, run_dive)
    R_r, F_r = pick(K2_pt, -hRise, hE2, run_rise)
    mode_dive = "fillet" if F_d else "sharp"
    if not F_d:
        f0 = fillet(A_pt, -hE1, dDive, 1.0)
        Rmax_dive = run_dive * math.tan(math.radians(f0["alpha_deg"]) / 2) if f0 else 0.0
    else:
        Rmax_dive = None
    assert F_r, f"{variant}: rise mouth fillet infeasible (run {run_rise:.3f})"
    # ---- assemble elements (dive -> rise) ----
    els = []
    chain_pts = []
    if F_d:
        els.append(("arc", F_d["O"], R_d, F_d["Ta"], F_d["Tb"], F_d["mid"]))
        els.append(("line", F_d["Tb"], tuple(T1a)))
        chain_pts += arc_pts(F_d["O"], R_d, F_d["Ta"], F_d["Tb"])
        chain_pts.append(tuple(T1a))
        start_pt = F_d["Ta"]
    else:
        els.append(("line", tuple(A_pt), tuple(T1a)))
        chain_pts += [tuple(A_pt), tuple(T1a)]
        start_pt = tuple(A_pt)
    els.append(("arc", tuple(A1[1]), A1[2], tuple(T1a), tuple(T1b), tuple(A1[5])))
    chain_pts += arc_pts(tuple(A1[1]), A1[2], tuple(T1a), tuple(T1b))[1:]
    els.append(("line", tuple(T1b), tuple(T2a)))
    chain_pts.append(tuple(T2a))
    els.append(("arc", tuple(A2[1]), A2[2], tuple(T2a), tuple(T2b), tuple(A2[5])))
    chain_pts += arc_pts(tuple(A2[1]), A2[2], tuple(T2a), tuple(T2b))[1:]
    els.append(("line", tuple(T2b), F_r["Ta"]))
    chain_pts.append(F_r["Ta"])
    els.append(("arc", F_r["O"], R_r, F_r["Ta"], F_r["Tb"], F_r["mid"]))
    chain_pts += arc_pts(F_r["O"], R_r, F_r["Ta"], F_r["Tb"])[1:]
    end_pt = F_r["Tb"]
    front_idx = 3 if F_d else 2
    # ---- replace the ring arc ----
    ring = [tuple(c) for c in wing_old.exterior.coords[:-1]]
    def seg_proj(pt):
        best = None
        for i in range(len(ring)):
            a, b = ring[i], ring[(i + 1) % len(ring)]
            ab = np.array(b) - np.array(a)
            t = float(np.clip(np.dot(np.array(pt) - np.array(a), ab) / np.dot(ab, ab), 0, 1))
            q = np.array(a) + ab * t
            dd = float(np.linalg.norm(np.array(pt) - q))
            if best is None or dd < best[0]:
                best = (dd, i, t, tuple(q))
        return best
    print("DBG", variant, "A", A_pt, "K2", K2_pt, "hE1", hE1, "hE2", hE2, "Rd", R_d, "Rr", R_r)
    print("DBG Fd", F_d)
    print("DBG Fr", F_r)
    print("DBG start", start_pt, "end", end_pt)
    dA = seg_proj(start_pt); dB = seg_proj(end_pt)
    assert dA[0] < 1e-3 and dB[0] < 1e-3, f"{variant}: tangent pts off ring {dA[0]:.4f} {dB[0]:.4f}"
    tab_pt = Point(tuple((Lf_a + Lf_b) / 2))
    def arc_walk(i0, t0, i1, t1, forward):
        pts = []
        n = len(ring)
        if forward:
            pts.append(tuple(np.array(ring[i0]) + (np.array(ring[(i0 + 1) % n]) - np.array(ring[i0])) * t0))
            i = (i0 + 1) % n
            while i != (i1 + 1) % n:
                pts.append(ring[i]); i = (i + 1) % n
            pts.append(tuple(np.array(ring[i1]) + (np.array(ring[(i1 + 1) % n]) - np.array(ring[i1])) * t1))
        else:
            pts.append(tuple(np.array(ring[(i0 + 1) % n]) + (np.array(ring[i0]) - np.array(ring[(i0 + 1) % n])) * (1 - t0)))
            i = i0
            while i != i1:
                pts.append(ring[i]); i = (i - 1) % n
            pts.append(tuple(np.array(ring[i1]) + (np.array(ring[(i1 + 1) % n]) - np.array(ring[i1])) * t1))
        return pts
    # candidate arcs from start_pt to end_pt, both directions
    def build_arc(fwd):
        # walk ring from start (seg dA) to end (seg dB)
        n = len(ring)
        pts = [start_pt]
        if fwd:
            i = (dA[1] + 1) % n
            while i != (dB[1] + 1) % n:
                pts.append(ring[i]); i = (i + 1) % n
        else:
            i = dA[1]
            while i != dB[1]:
                pts.append(ring[i]); i = (i - 1) % n
        pts.append(end_pt)
        return pts
    arcs = [build_arc(True), build_arc(False)]
    def arc_score(a):
        return LineString(a).distance(tab_pt) if len(a) > 2 else 99
    scores = [arc_score(a) for a in arcs]
    notch_arc = arcs[0] if scores[0] < scores[1] else arcs[1]
    long_arc = arcs[1] if scores[0] < scores[1] else arcs[0]
    assert min(scores) < 5.0 < max(scores), f"{variant}: arc split ambiguous {scores}"
    new_ring = long_arc + chain_pts[::-1][1:]
    wing_new = Polygon(new_ring)
    assert wing_new.is_valid, f"{variant}: invalid new polygon"
    assert wing_new.geom_type == "Polygon"
    # ---- checks ----
    seam = MAIN.distance(wing_new)
    ovl = MAIN.intersection(wing_new).area
    sil_ok = SIL.covers(wing_new)
    removed = wing_old.difference(wing_new)
    added = wing_new.difference(wing_old)
    def to_board_poly(poly):
        q = shp_translate(poly, xoff=-env[0], yoff=-env[1])
        q = shp_rotate(q, -deg, origin=(0, 0))
        return shp_translate(q, xoff=jw[0], yoff=jw[1])
    hits_r, hits_a = {}, {}
    for kind, geom in copper_items(b5):
        for poly, acc in ((removed, hits_r), (added, hits_a)):
            if poly.area <= 0:
                continue
            inter = geom.intersection(to_board_poly(poly))
            if inter.area > 1e-6:
                acc[kind] = acc.get(kind, 0) + inter.area
    hard_r = {k: v for k, v in hits_r.items() if k not in ("fill", "zonepoly")}
    hard_a = {k: v for k, v in hits_a.items() if k not in ("fill", "zonepoly")}
    print(f"{variant}: A={tuple(round(v,3) for v in A_pt)} K2={tuple(round(v,3) for v in K2_pt)} "
          f"dive {mode_dive} R={R_d} (run {run_dive:.3f}) rise R={R_r} (run {run_rise:.3f})")
    print(f"   seam {seam:.4f} ovl {ovl:.5f} sil {sil_ok} removed {removed.area:.3f} added {added.area:.3f} "
          f"area {wing_old.area:.1f}->{wing_new.area:.1f}")
    print(f"   copper removed { {k: round(v,4) for k,v in hits_r.items()} or 'NONE' } "
          f"added { {k: round(v,4) for k,v in hits_a.items()} or 'NONE' }")
    from shapely.ops import nearest_points
    np1, np2 = nearest_points(MAIN, wing_new)
    print("DBG seam at main", (round(np1.x,3), round(np1.y,3)), "wing", (round(np2.x,3), round(np2.y,3)))
    print("DBG added parts:", [(round(g.area,2), tuple(round(v,2) for v in g.bounds)) for g in (list(added.geoms) if added.geom_type == "MultiPolygon" else [added])])
    assert seam >= GAP - 1e-9 and ovl == 0.0 and sil_ok
    assert not hard_r, f"{variant}: removed hits routed copper {hard_r}"
    assert not hard_a, f"{variant}: added covers routed copper {hard_a}"
    def el_board(el):
        if el[0] == "line":
            return ("line", inv(el[1]), inv(el[2]))
        return ("arc", inv(el[1]), el[2], inv(el[3]), inv(el[4]), inv(el[5]))
    results[variant] = dict(
        site=site, delta=nd["delta"], front_index=front_idx,
        A=[round(v, 4) for v in A_pt], K2=[round(v, 4) for v in K2_pt],
        I1=[round(v, 4) for v in I1], I2=[round(v, 4) for v in I2],
        mode_dive=mode_dive, R_dive=R_d, R_rise=R_r,
        Rmax_dive=round(Rmax_dive, 3) if Rmax_dive else None,
        run_dive=round(run_dive, 4), run_rise=round(run_rise, 4),
        Lt_dive=round(F_d["Lt"], 4) if F_d else None,
        Lt_rise=round(F_r["Lt"], 4),
        seam_min=round(float(seam), 4), overlap_mm2=round(float(ovl), 5),
        removed_area_mm2=round(float(removed.area), 3),
        added_area_mm2=round(float(added.area), 3),
        removed_area_2d_mm2=nd["removed_area_mm2"],
        copper_removed={k: round(v, 5) for k, v in hits_r.items()},
        copper_added={k: round(v, 5) for k, v in hits_a.items()},
        inside_silhouette=bool(sil_ok),
        E1=[[round(v, 4) for v in E1s], [round(v, 4) for v in E1e]],
        E2=[[round(v, 4) for v in E2s], [round(v, 4) for v in E2e]],
        elements_case=[list(e) if e[0] == "line" else [e[0], list(e[1]), e[2], list(e[3]), list(e[4]), list(e[5])] for e in els],
        elements_board=[list(e) if e[0] == "line" else [e[0], list(e[1]), e[2], list(e[3]), list(e[4]), list(e[5])] for e in map(el_board, els)],
        wing_new_case=[list(c) for c in wing_new.exterior.coords])
json.dump(results, open(W / ".issue273-runtime/notch2e.json", "w"), indent=1)
print("saved notch2e.json")
