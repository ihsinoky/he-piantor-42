#!/usr/bin/env python3
"""Issue #273 stage 2e - Wing Rev.6 notch redesign (v4).

Chain (travel order): [dive mouth fillet] dive straight - corner
arc - front straight - corner fillet R0.55 - rise straight -
[rise mouth fillet]. The three straights are the Stage 2d design
lines at the 2d offsets (parallel to the adopted Rev.9 tab's front
/ walls; 0.56mm from the tab features they face).

Corner geometry (the subtle part): at the dive->front corner the
two lines meet at a shallow 38deg board wedge pointing at the Main.
The 2d chain's R0.55 arc there is the VOID-side fillet: its tangent
point on the dive line lies PAST the lines' intersection, so a
board built from it would fold back on itself in a thin sliver
(cusp) - in 2d it never reached the board (the keepout difference
kept Rev.5's E1 there), which is also why the 2d figure's mouth
looked unfixed. The 2e corner arc is the BOARD-side tangent arc
(centre on the board side of both lines): its dive-line tangent
point lies WEST of the intersection, no fold. Its radius shares
the short dive run (A to the tangent point) with the dive mouth
fillet: R_c is scanned 0.40 -> 0.15 and the largest R_c that still
leaves room for a mouth fillet R_d >= 0.30 (and >= 0.15mm residual
straight) wins. The front->rise corner keeps the 2d R0.55 fillet
(its tangent points straddle the intersection correctly - no fold).

Mouth transitions: the dive/rise straights are EXTENDED to
intersect the Wing's own long edge line (points A / K2 on the
Rev.5 edge SEGMENTS); ONE tangent fillet at each intersection
where the run allows (largest R in 1.00..0.30 leaving >= 0.15mm
residual straight), else a sharp corner at the intersection
(reported with the max feasible R). No tangent-arc chains.

New outline by RING-ARC REPLACEMENT on the Rev.5 outline (the 2d
defect was a keepout difference that kept Rev.5's faceted mouth
arcs). Checks: seam vs final Rev.9 Main outline >= 0.55, overlap
0, inside the D-037 silhouette (case_geometry.json tray
sections), removed-region copper = fills/zone outlines only,
added-region copper = none. Output: notch2e.json.
"""
import json, math, sys
from pathlib import Path
import numpy as np
import pcbnew as p
from shapely.geometry import LineString, Point, Polygon
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
RT = W / ".issue273-runtime"
SRT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
sys.path.insert(0, str(SRT))
from geom2b import copper_items
from notchain import wing_xf_factory

Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
Q270M = W / "hardware/kicad/qualification/issue-270-main-rev9"
GAP = 0.55
RESID = 0.15
ND = json.loads((SRT / "notch2d.json").read_text())
CASE = json.loads((SRT / "case_geometry.json").read_text())
SIL = unary_union([Polygon(q) for q in CASE["silhouette_parts"]])
VARIANTS = [("17mm-left", "left"), ("17mm-right", "right"),
            ("16mm-left", "left"), ("16mm-right", "right")]


def unit(v):
    v = np.asarray(v, float)
    return v / np.linalg.norm(v)


def line_x(p1, d1, p2, d2):
    A = np.column_stack([d1, -d2])
    t = np.linalg.solve(A, np.asarray(p2, float) - np.asarray(p1, float))
    return np.asarray(p1, float) + d1 * t[0]


def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM)
                    for j in range(ch.PointCount())])


mb = p.LoadBoard(str(Q270M / "main-rev9/main.kicad_pcb"))
MAIN = shp_translate(outline_kicad(mb), xoff=-100.0, yoff=-70.0)


def fillet(I, u1, u2, R):
    """Tangent fillet at corner I; u1/u2 = unit vectors pointing
    AWAY from I along the two lines (travel-in reverse / travel-out)."""
    alpha = math.acos(float(np.clip(np.dot(u1, u2), -1, 1)))
    Lt = R / math.tan(alpha / 2)
    bis = unit(np.array(u1) + np.array(u2))
    O = np.asarray(I, float) + bis * (R / math.sin(alpha / 2))
    Ta = np.asarray(I, float) + u1 * Lt
    Tb = np.asarray(I, float) + u2 * Lt
    mid = O + R * unit((Ta - O) + (Tb - O))
    return {"Ta": tuple(Ta), "Tb": tuple(Tb), "O": tuple(O),
            "mid": tuple(mid), "Lt": Lt, "alpha_deg": math.degrees(alpha)}


def nrm_toward(d, ref, p0):
    n = np.array([-d[1], d[0]])
    return n if np.dot(n, np.asarray(ref) - np.asarray(p0)) > 0 else -n


def corner_fillet_sides(Lp, Ld_, Mp, Md, R, refA, refB):
    """Fillet of radius R tangent to lines (Lp,Ld_) and (Mp,Md);
    centre on refA's side of the first line, refB's side of the
    second. Returns O, Ta (on first line), Tb (on second), mid."""
    na = nrm_toward(Ld_, refA, Lp)
    nb = nrm_toward(Md, refB, Mp)
    O = line_x(np.asarray(Lp) + na * R, Ld_, np.asarray(Mp) + nb * R, Md)
    Ta = np.asarray(Lp) + Ld_ * float(np.dot(O - np.asarray(Lp), Ld_))
    Tb = np.asarray(Mp) + Md * float(np.dot(O - np.asarray(Mp), Md))
    mid = O + R * unit((Ta - O) + (Tb - O))
    return {"O": tuple(O), "Ta": tuple(Ta), "Tb": tuple(Tb), "mid": tuple(mid)}


def pick_fillet(I, u1, u2, run):
    for R in [1.00, 0.95, 0.90, 0.85, 0.80, 0.75, 0.70, 0.65, 0.60,
              0.55, 0.50, 0.45, 0.40, 0.35, 0.30]:
        F = fillet(I, u1, u2, R)
        if run - F["Lt"] >= RESID:
            return R, F
    return None, None


def arc_pts(O, R, a, b, step_deg=3.0):
    O = np.asarray(O, float)
    a0 = math.atan2(*(np.asarray(a) - O)[::-1])
    a1 = math.atan2(*(np.asarray(b) - O)[::-1])
    sw_ccw = (a1 - a0) % (2 * math.pi)
    sw_cw = -((a0 - a1) % (2 * math.pi))
    sw = sw_ccw if abs(sw_ccw) < abs(sw_cw) else sw_cw
    n = max(4, int(abs(math.degrees(sw)) / step_deg))
    return [tuple(O + R * np.array([math.cos(a0 + sw * i / n),
                                    math.sin(a0 + sw * i / n)]))
            for i in range(n + 1)]


out = {}
for variant, side in VARIANTS:
    els_nd = ND[variant]["elements_case"]
    Ld_p = np.array(els_nd[0][1]); Ld_d = unit(np.array(els_nd[0][2]) - Ld_p)
    Lf_p = np.array(els_nd[2][1]); Lf_d = unit(np.array(els_nd[2][2]) - Lf_p)
    Lr_p = np.array(els_nd[4][1]); Lr_d = unit(np.array(els_nd[4][2]) - Lr_p)
    O1_ref = np.array(els_nd[1][1]); O2_ref = np.array(els_nd[3][1])
    I1 = line_x(Ld_p, Ld_d, Lf_p, Lf_d)
    I2 = line_x(Lf_p, Lf_d, Lr_p, Lr_d)
    # validate: the stored 2d arcs are reproduced by corner_fillet_sides
    # with both refs = the stored centre (void-side fillets)
    for C, el in ((corner_fillet_sides(Ld_p, Ld_d, Lf_p, Lf_d, 0.55, O1_ref, O1_ref), els_nd[1]),
                  (corner_fillet_sides(Lf_p, Lf_d, Lr_p, Lr_d, 0.55, O2_ref, O2_ref), els_nd[3])):
        assert np.linalg.norm(np.array(C["O"]) - np.array(el[1])) < 0.01
        assert np.linalg.norm(np.array(C["Ta"]) - np.array(el[3])) < 0.01
        assert np.linalg.norm(np.array(C["Tb"]) - np.array(el[4])) < 0.01
    # corner 2 keeps the stored (void-side, correctly straddling) fillet
    C2 = corner_fillet_sides(Lf_p, Lf_d, Lr_p, Lr_d, 0.55, O2_ref, O2_ref)
    T2a, T2b = np.array(C2["Ta"]), np.array(C2["Tb"])
    # corner 1: the board-side centre is on O1_ref's side of the dive
    # line and on ONE of the two sides of the front line; try both
    # front sides and keep the centre whose tangent points straddle
    # I1 without folding (T1a on the approach side, T1b on the
    # departure side). (Left: front side opposite O1_ref. Right:
    # to be seen - the J3 corner is not a mirror of J2.)
    n_front_toward_O1 = nrm_toward(Lf_d, O1_ref, Lf_p)
    front_travel = Lf_d if np.dot(Lf_d, T2a - I1) > 0 else -Lf_d

    def corner1(R_c):
        cands = []
        for refB in (I1 - n_front_toward_O1 * 2.0, I1 + n_front_toward_O1 * 2.0):
            C = corner_fillet_sides(Ld_p, Ld_d, Lf_p, Lf_d, R_c, O1_ref, refB)
            Ta, Tb = np.array(C["Ta"]), np.array(C["Tb"])
            if np.dot(Ta - I1, unit(I1 - A_pt)) < 0 and \
                    np.dot(Tb - I1, front_travel) > 0:
                cands.append(C)
        assert len(cands) == 1, f"{variant}: corner1 candidates {len(cands)}"
        return cands[0]

    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    ang = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)

    def to_case(poly):
        q = shp_translate(poly, xoff=-jw[0], yoff=-jw[1])
        q = shp_rotate(q, ang, origin=(0, 0))
        return shp_translate(q, xoff=env[0], yoff=env[1])

    def pt_case(pt):
        q = to_case(Point(pt))
        return (q.x, q.y)

    wing_old = to_case(outline_kicad(b5))
    chain_union = unary_union([LineString([els_nd[0][1], els_nd[0][2]]),
                               LineString([els_nd[2][1], els_nd[2][2]]),
                               LineString([els_nd[4][1], els_nd[4][2]])])
    flanks = []
    for d in b5.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts or str(d.GetShape()) not in ("0", "SEGMENT"):
            continue
        s = pt_case((d.GetStart().x / MM, d.GetStart().y / MM))
        e = pt_case((d.GetEnd().x / MM, d.GetEnd().y / MM))
        ls = LineString([s, e])
        if math.dist(s, e) >= 15.0 and ls.distance(chain_union) < 6.0 \
                and max(Point(s).distance(chain_union),
                        Point(e).distance(chain_union)) > 10.0:
            flanks.append((np.array(s), np.array(e)))
    assert len(flanks) == 2, f"{variant}: {len(flanks)} flank candidates"
    cand = []
    for s, e in flanks:
        d = unit(e - s)
        x = line_x(Ld_p, Ld_d, s, d)
        cand.append((LineString([s, e]).distance(Point(x)),
                     float(np.linalg.norm(x - I1)), (s, e)))
    cand.sort(key=lambda c: (round(c[0], 6), c[1]))
    assert cand[0][0] < 0.01, f"{variant}: dive flank segdist {cand[0][0]:.3f}"
    (E1s, E1e) = cand[0][2]
    (E2s, E2e) = cand[1][2]
    E1_d = unit(E1e - E1s)
    E2_d = unit(E2e - E2s)
    A_pt = line_x(Ld_p, Ld_d, E1s, E1_d)
    far1 = E1s if np.linalg.norm(A_pt - E1s) > np.linalg.norm(A_pt - E1e) else E1e
    hE1 = unit(A_pt - far1)
    K2_pt = line_x(Lr_p, Lr_d, E2s, E2_d)
    assert LineString([E2s, E2e]).distance(Point(K2_pt)) < 0.01
    far2 = E2s if np.linalg.norm(K2_pt - E2s) > np.linalg.norm(K2_pt - E2e) else E2e
    hE2 = unit(far2 - K2_pt)
    dDive = unit(I1 - A_pt)
    hRise = unit(K2_pt - T2b)
    run_rise = float(np.linalg.norm(K2_pt - T2b))
    R_r, F_r = pick_fillet(K2_pt, -hRise, hE2, run_rise)
    sharp = {}
    if F_r is None:
        F = fillet(K2_pt, -hRise, hE2, 0.30)
        sharp["rise_Rmax"] = (run_rise - RESID) / (F["Lt"] / 0.30)

    def build_chain(R_c):
        C1 = corner1(R_c)
        T1a, T1b = np.array(C1["Ta"]), np.array(C1["Tb"])
        run_dive = float(np.dot(T1a - A_pt, dDive))
        R_d, F_d = pick_fillet(A_pt, -hE1, dDive, run_dive)
        lsharp = {}
        if F_d is None:
            F = fillet(A_pt, -hE1, dDive, 0.30)
            lsharp["dive_Rmax"] = (run_dive - RESID) / (F["Lt"] / 0.30)
        els, pts = [], []
        if F_d is not None:
            els.append(("arc", F_d["O"], R_d, F_d["Ta"], F_d["Tb"], F_d["mid"]))
            pts += arc_pts(F_d["O"], R_d, F_d["Ta"], F_d["Tb"])
            els.append(("line", F_d["Tb"], tuple(T1a)))
            pts.append(tuple(T1a))
            start_pt = F_d["Ta"]
        else:
            els.append(("line", tuple(A_pt), tuple(T1a)))
            pts += [tuple(A_pt), tuple(T1a)]
            start_pt = tuple(A_pt)
        els.append(("arc", C1["O"], R_c, tuple(T1a), tuple(T1b), C1["mid"]))
        pts += arc_pts(C1["O"], R_c, tuple(T1a), tuple(T1b))[1:]
        fi = len(els)
        els.append(("line", tuple(T1b), tuple(T2a)))
        pts.append(tuple(T2a))
        els.append(("arc", C2["O"], 0.55, tuple(T2a), tuple(T2b), C2["mid"]))
        pts += arc_pts(C2["O"], 0.55, tuple(T2a), tuple(T2b))[1:]
        if F_r is not None:
            els.append(("line", tuple(T2b), F_r["Ta"]))
            pts.append(F_r["Ta"])
            els.append(("arc", F_r["O"], R_r, F_r["Ta"], F_r["Tb"], F_r["mid"]))
            pts += arc_pts(F_r["O"], R_r, F_r["Ta"], F_r["Tb"])[1:]
            end_pt = F_r["Tb"]
        else:
            els.append(("line", tuple(T2b), tuple(K2_pt)))
            pts.append(tuple(K2_pt))
            end_pt = tuple(K2_pt)
        return {"els": els, "pts": pts, "front_index": fi, "start": start_pt,
                "end": end_pt, "R_c": R_c, "R_d": R_d, "run_dive": run_dive,
                "T1a": tuple(T1a), "sharp": lsharp}

    scan = []
    chosen = None
    for R_c in [0.40, 0.375, 0.35, 0.325, 0.30, 0.275, 0.25, 0.225,
                0.20, 0.175, 0.15]:
        ch = build_chain(R_c)
        s_chain = MAIN.distance(LineString(ch["pts"]))
        scan.append((R_c, ch["R_d"], s_chain))
        if chosen is None and ch["R_d"] is not None and ch["R_d"] >= 0.30:
            chosen = ch
    if chosen is None:
        chosen = build_chain(0.15)
    ch = chosen
    els, chain_pts = ch["els"], ch["pts"]
    print(f"{variant}: R_c={ch['R_c']} R_d={ch['R_d']} R_r={R_r} scan "
          + " ".join(f"{r}:Rd{rd}/s{s:.3f}" for r, rd, s in scan))

    # ring-arc replacement on the Rev.5 outline
    ring = [tuple(c) for c in wing_old.exterior.coords]
    n = len(ring) - 1

    def seg_proj(pt):
        pt = np.array(pt)
        best = (1e9, -1, 0.0, None)
        for i in range(n):
            a, b = np.array(ring[i]), np.array(ring[i + 1])
            ab = b - a
            t = float(np.clip(np.dot(pt - a, ab) / np.dot(ab, ab), 0, 1))
            q = a + ab * t
            d = float(np.linalg.norm(pt - q))
            if d < best[0]:
                best = (d, i, t, tuple(q))
        return best

    dA, dB = seg_proj(ch["start"]), seg_proj(ch["end"])
    assert dA[0] < 1e-3 and dB[0] < 1e-3, \
        f"{variant}: tangent pts off ring {dA[0]:.4f} {dB[0]:.4f}"
    tab_pt = Point(np.mean([np.array(els_nd[2][1]), np.array(els_nd[2][2])], axis=0))

    def build_arc(forward):
        pts = [ch["start"]]
        i = (dA[1] + 1) % n if forward else dA[1]
        target = (dB[1] + 1) % n if forward else dB[1]
        while i != target:
            pts.append(ring[i])
            i = (i + 1) % n if forward else (i - 1) % n
        pts.append(ch["end"])
        return pts

    arcs = [build_arc(True), build_arc(False)]
    scores = [LineString(a).distance(tab_pt) if len(a) > 2 else 99 for a in arcs]
    notch_arc = arcs[0] if scores[0] < scores[1] else arcs[1]
    long_arc = arcs[1] if scores[0] < scores[1] else arcs[0]
    assert min(scores) < 5.0 < max(scores), f"{variant}: arc split {scores}"
    new_ring = long_arc + chain_pts[::-1][1:]
    wing_new = Polygon(new_ring)
    assert wing_new.is_valid, f"{variant}: invalid new polygon"
    removed = wing_old.difference(wing_new)
    added = wing_new.difference(wing_old)
    seam = MAIN.distance(wing_new)
    ovl = MAIN.intersection(wing_new).area
    sil_ok = SIL.covers(wing_new)
    assert seam >= GAP - 1e-9 and ovl == 0.0 and sil_ok, \
        f"{variant}: seam {seam:.4f} ovl {ovl} sil {sil_ok}"
    rem_kinds, add_kinds = {}, {}
    for kind, poly in copper_items(b5):
        cp = to_case(poly)
        ra = cp.intersection(removed).area if not removed.is_empty else 0.0
        aa = cp.intersection(added).area if not added.is_empty else 0.0
        if ra > 1e-6:
            rem_kinds[kind] = rem_kinds.get(kind, 0.0) + ra
        if aa > 1e-6:
            add_kinds[kind] = add_kinds.get(kind, 0.0) + aa
    bad_rem = {k: v for k, v in rem_kinds.items() if k not in ("fill", "zonepoly")}
    assert not bad_rem, f"{variant}: removed copper {bad_rem}"
    assert not add_kinds, f"{variant}: added-region copper {add_kinds}"

    def els_json(els):
        r = []
        for e in els:
            if e[0] == "line":
                r.append(["line", [float(v) for v in e[1]], [float(v) for v in e[2]]])
            else:
                r.append(["arc", [float(v) for v in e[1]], float(e[2]),
                          [float(v) for v in e[3]], [float(v) for v in e[4]],
                          [float(v) for v in e[5]]])
        return r

    def to_board(pt):
        q = shp_translate(Point(pt), xoff=-env[0], yoff=-env[1])
        q = shp_rotate(q, -ang, origin=(0, 0))
        q = shp_translate(q, xoff=jw[0], yoff=jw[1])
        return (q.x, q.y)

    eb = []
    for e in els:
        if e[0] == "line":
            eb.append(["line", list(to_board(e[1])), list(to_board(e[2]))])
        else:
            eb.append(["arc", list(to_board(e[1])), e[2], list(to_board(e[3])),
                       list(to_board(e[4])), list(to_board(e[5]))])
    out[variant] = {
        "elements_case": els_json(els),
        "elements_board": eb,
        "front_index": ch["front_index"],
        "wing_new_case": [[float(x), float(y)] for x, y in new_ring],
        "diag": {
            "A": [float(v) for v in A_pt], "K2": [float(v) for v in K2_pt],
            "R_dive_mouth": ch["R_d"], "R_corner_dive": ch["R_c"],
            "R_corner_rise": 0.55, "R_rise_mouth": R_r,
            "sharp": {**sharp, **ch["sharp"]}, "run_dive": ch["run_dive"], "run_rise": run_rise,
            "corner_scan": [[r, rd, round(s, 4)] for r, rd, s in scan],
            "seam": seam, "overlap": ovl, "silhouette": bool(sil_ok),
            "removed_area": removed.area, "added_area": added.area,
            "removed_copper": rem_kinds, "added_copper": add_kinds,
            "n_elements": len(els),
        },
    }
    print(f"   seam {seam:.4f} ovl {ovl:.5f} sil {sil_ok} removed "
          f"{removed.area:.3f} added {added.area:.3f} sharp {sharp} els {len(els)}")

(RT / "notch2e.json").write_text(json.dumps(out, indent=1))
print("wrote notch2e.json")
