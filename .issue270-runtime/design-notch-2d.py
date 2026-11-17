"""Issue #270 stage 2d, Wing simplified notch design (PO redirect
2026-11-18): per variant, in case frame at the fitted pose, the notch
floor is THREE straight segments parallel to the final tab's diving
wall / front / rising wall, each at perpendicular distance
0.55 + delta from the tab edge line, joined by R1.0 tangent fillets,
ends extended past the existing Wing (Rev.5) boundary. Verified by
dense sampling: min distance floor -> final Main outline >= 0.550
(delta raised in 0.01 steps if a fillet dips below), overlap 0,
removed region vs Rev.5 copper (hard hits abort), inside the D-037
silhouette. Also records the Stage 2b exact-offset notch area for
comparison. Writes notch2d.json (elements in case + board frames)."""
import json, math, sys
from pathlib import Path
import numpy as np
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
WT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline")
Q263 = WT / "hardware/kicad/qualification/issue-263-implementation"
Q270M = WT / "hardware/kicad/qualification/issue-270-main-rev9/main-rev9"
Q270W = WT / "hardware/kicad/qualification/issue-270-wing-rev6"
sys.path.insert(0, str(RT))
from geom2b import copper_items
from notchain import wing_xf_factory

D2 = json.loads((RT / "stage2d.json").read_text())
case = json.loads((RT / 'case_geometry.json').read_text())
sil = unary_union([Polygon(q) for q in case['silhouette_parts']])
GAP = 0.55
RF = 0.55  # junction fillet radius: the project's established notch-arc
# radius (Rev.6 exact-offset chain). Swept 1.0 / 0.75 / 0.55: R0.55 needs
# the least delta raise (0.01-0.05 vs 0.10-0.12) and removes the least
# Wing material, because the tangent fillet's dip toward the tab corner
# scales with R.

def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])

main_case = shp_translate(outline_kicad(p.LoadBoard(str(Q270M / "main.kicad_pcb"))), xoff=-100.0, yoff=-70.0)
CENTROID = np.array([main_case.centroid.x, main_case.centroid.y])
F = D2["fillet"]; C = D2["corners_case"]
TAB = {
    "J2": dict(dive=(tuple(F["W0_case"]), tuple(C["J2"]["PL"])),
               front=(tuple(F["Tf_case"]), tuple(C["J2"]["PR"])),
               rise=(tuple(C["J2"]["PR"]), (-29.0265, 52.5433))),
    "J3": dict(dive=((17.8562, 33.1958), tuple(C["J3"]["PR"])),
               front=(tuple(C["J3"]["PR"]), tuple(C["J3"]["PL"])),
               rise=(tuple(C["J3"]["PL"]), (28.9362, 52.3869))),
}

def offset_line(p1, p2, dist):
    a, b = np.array(p1, float), np.array(p2, float)
    d = b - a; d = d / np.linalg.norm(d)
    n = np.array([-d[1], d[0]])
    if np.dot(CENTROID - a, n) > 0:
        n = -n
    return (a + n * dist, d)

def line_x(L1, L2):
    (p1, d1), (p2, d2) = L1, L2
    den = d1[0] * d2[1] - d1[1] * d2[0]
    t = ((p2[0] - p1[0]) * d2[1] - (p2[1] - p1[1]) * d2[0]) / den
    return p1 + d1 * t

def build_chain(site, delta):
    """Returns (elements, samples) in case frame. Elements:
    ('line', a, b) / ('arc', centre, r, a, b, mid)."""
    Ld = offset_line(*TAB[site]["dive"], GAP + delta)
    Lf = offset_line(*TAB[site]["front"], GAP + delta)
    Lr = offset_line(*TAB[site]["rise"], GAP + delta)
    I1 = line_x(Ld, Lf)
    I2 = line_x(Lf, Lr)
    # travel directions: dive -> I1 -> I2 -> rise mouth
    def toward(L, frm, to):
        p, d = L
        return d * (1 if np.dot(d, np.array(to) - np.array(frm)) >= 0 else -1)
    d_dive = toward(Ld, Ld[0], I1)
    d_front = toward(Lf, I1, I2)
    rise_far = np.array(TAB[site]["rise"][1]) + (np.array(Lr[0]) - np.array(TAB[site]["rise"][0]))
    d_rise = toward(Lr, I2, rise_far)
    els, joints = [], []
    for I, din, dout in ((I1, d_dive, d_front), (I2, d_front, d_rise)):
        u1, u2 = -din, dout                       # away from I along each segment
        alpha = math.acos(float(np.clip(np.dot(u1, u2), -1, 1)))
        Lt = RF / math.tan(alpha / 2)
        Ta = I + u1 * Lt
        Tb = I + u2 * Lt
        bis = u1 + u2; bis = bis / np.linalg.norm(bis)
        O = I + bis * (RF / math.sin(alpha / 2))
        joints.append(dict(I=I, Ta=Ta, Tb=Tb, O=O, Lt=Lt, alpha=alpha))
    j1, j2 = joints
    end_dive = tuple(j1["Ta"] - d_dive * 40.0)
    end_rise = tuple(j2["Tb"] + d_rise * 40.0)
    def arc_pts(j):
        O, Ta, Tb = j["O"], j["Ta"], j["Tb"]
        a0 = math.atan2(Ta[1] - O[1], Ta[0] - O[0])
        a1 = math.atan2(Tb[1] - O[1], Tb[0] - O[0])
        while a1 - a0 > math.pi: a1 -= 2 * math.pi
        while a1 - a0 < -math.pi: a1 += 2 * math.pi
        n = max(8, int(abs(a1 - a0) / 0.01))
        return [tuple(O + RF * np.array([math.cos(a0 + (a1 - a0) * i / n),
                                         math.sin(a0 + (a1 - a0) * i / n)])) for i in range(n + 1)]
    a1p, a2p = arc_pts(j1), arc_pts(j2)
    mid1 = a1p[len(a1p) // 2]; mid2 = a2p[len(a2p) // 2]
    els = [("line", end_dive, tuple(j1["Ta"])),
           ("arc", tuple(j1["O"]), RF, tuple(j1["Ta"]), tuple(j1["Tb"]), mid1),
           ("line", tuple(j1["Tb"]), tuple(j2["Ta"])),
           ("arc", tuple(j2["O"]), RF, tuple(j2["Ta"]), tuple(j2["Tb"]), mid2),
           ("line", tuple(j2["Tb"]), end_rise)]
    pts = [end_dive, tuple(j1["Ta"])] + a1p[1:] + [tuple(j2["Ta"])] + a2p[1:] + [end_rise]
    return els, LineString(pts), (j1, j2)

def sample_chain(ls, step=0.02):
    n = max(2, int(ls.length / step))
    return [ls.interpolate(i / n, normalized=True) for i in range(n + 1)]

results = {}
for variant in ("17mm-left", "17mm-right", "16mm-left", "16mm-right"):
    pitch, side = variant.split("-")
    site = "J2" if side == "left" else "J3"
    src = Q263 / f"wing-rev5-{variant}"
    b5 = p.LoadBoard(str(src / "main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    def to_case(poly_board):
        q = shp_translate(poly_board, xoff=-jw[0], yoff=-jw[1])
        deg = 30.5 if side == "left" else -30.5
        q = shp_rotate(q, deg, origin=(0, 0))
        env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
        return shp_translate(q, xoff=env[0], yoff=env[1])
    wing_old_case = to_case(outline_kicad(b5))
    # Stage 2b notch area for comparison
    b6 = p.LoadBoard(str(Q270W / f"wing-rev6-{variant}" / "main.kicad_pcb"))
    wing_2b_case = to_case(outline_kicad(b6))
    removed_2b = wing_old_case.difference(wing_2b_case)
    # design loop on delta
    chosen = None
    for di in range(0, 21):
        delta = round(di * 0.01, 2)
        els, chain, joints = build_chain(site, delta)
        # keepout: chain + deep closure toward Main centroid
        mid = np.array(chain.interpolate(0.5, normalized=True).coords[0])
        inward = CENTROID - mid; inward = inward / np.linalg.norm(inward)
        e0 = np.array(els[0][1]); e1 = np.array(els[-1][2])
        keepout = Polygon([tuple(e0), *[tuple(c) for c in chain.coords[1:]],
                           tuple(e1 + inward * 50), tuple(e0 + inward * 50)])
        wing_new = wing_old_case.difference(keepout)
        if wing_new.geom_type == "MultiPolygon":
            wing_new = max(wing_new.geoms, key=lambda q: q.area)
        overlap = main_case.intersection(wing_new).area
        seam_poly = main_case.distance(wing_new)
        # diagnostic: floor min over the near-Wing portion of the chain
        near = wing_old_case.buffer(1.0)
        dists = [(main_case.distance(pt), (pt.x, pt.y)) for pt in sample_chain(chain)
                 if near.covers(pt)]
        dmin, dmin_pt = min(dists)
        if seam_poly >= GAP - 1e-9 and overlap == 0.0:
            chosen = (delta, els, chain, joints, dmin, dmin_pt, wing_new, seam_poly)
            break
        print(f"  {variant} delta {delta}: poly seam {seam_poly:.4f} floor min {dmin:.4f} overlap {overlap:.4f} - raise")
    assert chosen, f"{variant}: no delta in [0, 0.20] clears the seam"
    delta, els, chain, joints, dmin, dmin_pt, wing_new, seam_poly = chosen
    removed = wing_old_case.difference(wing_new)
    # copper check in board frame: exact inverse of to_case as an
    # affine transform (point-by-point inversion broke on a sliver
    # part with a TopologyException)
    deg = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    removed_board = shp_translate(
        shp_rotate(shp_translate(removed, xoff=-env[0], yoff=-env[1]), -deg, origin=(0, 0)),
        xoff=jw[0], yoff=jw[1])
    if not removed_board.is_valid:
        removed_board = removed_board.buffer(0)
    hits = {}
    for kind, geom in copper_items(b5):
        inter = geom.intersection(removed_board)
        if inter.area > 1e-6:
            hits[kind] = hits.get(kind, 0) + inter.area
    hard = {k: v for k, v in hits.items() if k not in ("fill", "zonepoly")}
    print(f"{variant}: delta {delta}, seam sample-min {dmin:.4f} at {tuple(round(v,2) for v in dmin_pt)}, "
          f"poly-dist {seam_poly:.4f}, overlap {main_case.intersection(wing_new).area:.4f}, "
          f"removed {removed.area:.2f} mm2 (2b: {removed_2b.area:.2f}), copper hits "
          f"{ {k: round(v,4) for k, v in hits.items()} or 'NONE' }, silhouette {sil.covers(wing_new)}")
    assert not hard, f"{variant}: removed region hits routed copper {hard}"
    assert sil.covers(wing_new)
    def el_board(el):
        if el[0] == "line":
            return ("line", inv(el[1]), inv(el[2]))
        return ("arc", inv(el[1]), el[2], inv(el[3]), inv(el[4]), inv(el[5]))
    results[variant] = dict(
        site=site, delta=delta, rf=RF,
        seam_sample_min=round(float(dmin), 4), seam_min_at_case=[round(v, 3) for v in dmin_pt],
        seam_poly_dist=round(float(seam_poly), 4),
        overlap_mm2=round(float(main_case.intersection(wing_new).area), 5),
        removed_area_mm2=round(float(removed.area), 3),
        removed_area_2b_mm2=round(float(removed_2b.area), 3),
        copper_hits={k: round(v, 5) for k, v in hits.items()},
        inside_silhouette=bool(sil.covers(wing_new)),
        joints=[dict(Lt=round(float(j["Lt"]), 3), alpha_deg=round(math.degrees(j["alpha"]), 1)) for j in joints],
        elements_case=[list(e) if e[0] == "line" else [e[0], list(e[1]), e[2], list(e[3]), list(e[4]), list(e[5])] for e in els],
        elements_board=[list(e) if e[0] == "line" else [e[0], list(e[1]), e[2], list(e[3]), list(e[4]), list(e[5])] for e in map(el_board, els)],
        wing_new_case=[list(c) for c in wing_new.exterior.coords])
json.dump(results, open(RT / "notch2d.json", "w"), indent=1)
print("saved notch2d.json")
