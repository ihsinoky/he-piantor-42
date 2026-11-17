"""Issue #270 stage 2d, Main design: Stage 2c candidate + build fillet
at the J2 diving corner PL (d = 0.151).

The fillet is a conventional corner fillet: an arc tangent to the
FRONT line and to the WALL line at PL. The wall stub PL->W0 (W0 = wall
line x edge line) is only 0.174 mm long, which caps the radius:
tangent length Lt = R / tan(phi/2), phi = interior angle at PL
(~142 deg) -> Lt = 0.344R, so R <= ~0.50. Scan R = 1.00 .. 0.30 in
0.05 steps, skipping radii whose tangent point falls off the wall
stub; take the largest R that keeps every Stage 2c check:
pad clearance >= 1.4864-eps, copper cuts 0, min edge-to-copper
>= 0.284, pads uncovered 0, inside silhouette.
Checks copied from s2c_design3.py (same yardsticks, base = Rev.9)."""
import json, math
from pathlib import Path
import numpy as np
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

HERE = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
g = json.loads((HERE / 'geometry.json').read_text())
sites = json.loads((HERE / 'sites.json').read_text())
case = json.loads((HERE / 'case_geometry.json').read_text())
tray = json.loads((HERE / 'tray_local.json').read_text())
probe = json.loads((HERE / 'stage2c-probe.json').read_text())
M = json.loads((HERE / 'stage2c-measure-summary.json').read_text())
S2C = json.loads((HERE / 'stage2c.json').read_text())

rev7 = Polygon(g['main_rev7_outline'])
rev9 = Polygon(probe['rev9_outline_case'])
sil = unary_union([Polygon(p) for p in case['silhouette_parts']])
traypoly = {s: unary_union([Polygon(p) for p in tray[s]]) for s in tray}
DEPTH = 4.738
FRONT_HALF = 16.689 / 2
BASE_D = -2.0
BASE_HALF = FRONT_HALF + (DEPTH - BASE_D) / math.tan(math.radians(60))
RAISE = S2C['chosen_raise']


def to_case(site, t, d):
    A, u, n = site['A'], site['u'], site['n']
    return (A[0] + u[0] * t + n[0] * d, A[1] + u[1] * t + n[1] * d)


def line_int(P, v, Q, w):
    den = v[0] * w[1] - v[1] * w[0]
    t = ((Q[0] - P[0]) * w[1] - (Q[1] - P[1]) * w[0]) / den
    return (P[0] + v[0] * t, P[1] + v[1] * t)


WALLS = {}


def build_cand():
    blobs, spec = [], {}
    for ref in ('J2', 'J3'):
        s = sites[ref]
        d = M[ref]
        a, m, cen = d['a'], d['m'], d['cen']
        tc = sum(s['tab_t_range_mine']) / 2
        wf = d['pad_w_max'] + 0.8364 + RAISE
        FP = (cen[0] + m[0] * wf, cen[1] + m[1] * wf)

        def wall(side):
            p1 = to_case(s, tc + side * FRONT_HALF, DEPTH)
            p2 = to_case(s, tc + side * BASE_HALF, BASE_D)
            return p1, (p2[0] - p1[0], p2[1] - p1[1])
        PL = line_int(FP, a, *wall(-1))
        PR = line_int(FP, a, *wall(+1))
        B1 = to_case(s, tc - BASE_HALF, BASE_D)
        B2 = to_case(s, tc + BASE_HALF, BASE_D)
        blobs.append(Polygon([B1, PL, PR, B2]))
        WALLS[ref] = {(-1): wall(-1), (+1): wall(+1)}
        spec[ref] = {'PL': PL, 'PR': PR, 'B1': B1, 'B2': B2, 'tc': tc}
    return unary_union([rev7] + blobs), spec


cand, spec = build_cand()
assert abs(cand.area - S2C['candidate_checks']['area']) < 0.05, cand.area


def td(site, pt):
    dx, dy = pt[0] - site['A'][0], pt[1] - site['A'][1]
    return (dx * site['u'][0] + dy * site['u'][1], dx * site['n'][0] + dy * site['n'][1])


# --- J2 diving corner = PL (d = 0.151); wall on the PL side is wall(-1) ---
s2 = sites['J2']
for name in ('PL', 'PR'):
    print(f"J2 {name}: td={tuple(round(v,3) for v in td(s2, spec['J2'][name]))} case={tuple(round(v,3) for v in spec['J2'][name])}")
PL = np.array(spec['J2']['PL'], float)
PR = np.array(spec['J2']['PR'], float)
wp1, wv = WALLS['J2'][-1]
wv = np.array(wv, float); wv = wv / np.linalg.norm(wv)   # wall dir (down-outward)
W0 = np.array(line_int(tuple(PL), tuple(wv), s2['A'], s2['u']))  # wall x edge line
stub = float(np.linalg.norm(PL - W0))
u_wall = (W0 - PL) / stub                                # PL -> W0 (along wall)
u_front = (PR - PL) / np.linalg.norm(PR - PL)            # PL -> PR (along front)
phi = math.degrees(math.acos(float(np.clip(np.dot(u_wall, u_front), -1, 1))))
print(f"W0={tuple(round(v,3) for v in W0)} stub={stub:.4f} mm, interior angle phi={phi:.1f} deg, "
      f"Lt per R = {1/math.tan(math.radians(phi)/2):.4f}")


def fillet(R):
    Lt = R / math.tan(math.radians(phi) / 2)
    if Lt > stub:
        return None, dict(R=R, Lt=round(Lt, 4), feasible=False)
    Tf = PL + u_front * Lt
    Tw = PL + u_wall * Lt
    bis = u_front + u_wall; bis = bis / np.linalg.norm(bis)
    O = PL + bis * (R / math.sin(math.radians(phi) / 2))
    a0 = math.atan2(Tf[1] - O[1], Tf[0] - O[0])
    a1 = math.atan2(Tw[1] - O[1], Tw[0] - O[0])
    while a1 - a0 > math.pi: a1 -= 2 * math.pi
    while a1 - a0 < -math.pi: a1 += 2 * math.pi
    n = max(8, int(abs(a1 - a0) / 0.02))
    arc = [tuple(O + R * np.array([math.cos(a0 + (a1 - a0) * i / n),
                                   math.sin(a0 + (a1 - a0) * i / n)])) for i in range(n + 1)]
    pocket = Polygon([tuple(Tf), tuple(PL), tuple(Tw)] + arc[::-1][1:-1])
    return cand.difference(pocket), dict(
        R=R, Lt=round(float(Lt), 4), feasible=True, stub_residual=round(stub - Lt, 4),
        Tf=tuple(Tf), Tw=tuple(Tw), O=tuple(O), W0=tuple(W0),
        arc_mid=arc[len(arc) // 2], pocket_area=round(pocket.intersection(cand).area, 4))


def copper_geo(it):
    if it['kind'] == 'track':
        return LineString([it['a'], it['b']]).buffer(it['width'] / 2, cap_style=2)
    if it['kind'] == 'via':
        return Point(it['centre']).buffer(it['dia'] / 2)
    return Polygon(it['corners'])


def main_checks(poly, base):
    r = {}
    worst, worst_id, uncovered = 1e9, None, 0
    for ref, lst in g['main_zif_pads'].items():
        for pd in lst:
            for c in pd['bbox']:
                pt = Point(c)
                if not poly.covers(pt):
                    uncovered += 1
                dd = poly.exterior.distance(pt)
                if dd < worst:
                    worst, worst_id = dd, f"{ref}.{pd['num']}"
    r['pad_clearance'] = round(worst, 4); r['pad_worst'] = worst_id; r['pad_uncovered'] = uncovered
    sw_, sun = 1e9, 0
    for ref in ('J2', 'J3'):
        s = sites[ref]
        for t, dd in s['silk_td']:
            pt = Point(to_case(s, t, dd))
            if not poly.covers(pt):
                sun += 1
            sw_ = min(sw_, poly.exterior.distance(pt))
    r['silk_min_dist'] = round(sw_, 3); r['silk_uncovered'] = sun
    r['inside_silhouette'] = bool(sil.covers(poly))
    for side, half in (('L', Polygon([(-200, -200), (0, -200), (0, 200), (-200, 200)])),
                       ('R', Polygon([(0, -200), (200, -200), (200, 200), (0, 200)]))):
        a_c = poly.difference(rev7).intersection(traypoly[side]).intersection(half).area
        a_b = base.difference(rev7).intersection(traypoly[side]).intersection(half).area
        r[f'tray_{side}_delta_vs_rev9_mm3'] = round((a_c - a_b) * 1.2, 2)
    removed = base.difference(poly)
    cuts, minclr = 0, 1e9
    for it in g['main_copper_near_tabs']:
        geo = copper_geo(it)
        if geo.intersects(removed):
            cuts += 1
        minclr = min(minclr, poly.exterior.distance(geo))
    r['copper_cuts_vs_rev9'] = cuts
    r['copper_min_clearance'] = round(minclr, 3)
    r['area'] = round(poly.area, 2)
    return r


base_chk = S2C['candidate_checks']
print("2c candidate checks:", {k: base_chk[k] for k in ('pad_clearance', 'copper_cuts_vs_rev9', 'copper_min_clearance')})
chosen = None
for i in range(20, 5, -1):
    R = round(i * 0.05, 2)
    poly, finfo = fillet(R)
    if poly is None:
        print("R", R, "Lt", finfo['Lt'], "> stub", round(stub, 4), "- infeasible")
        continue
    chk = main_checks(poly, rev9)
    ok = (chk['copper_cuts_vs_rev9'] == 0 and chk['copper_min_clearance'] >= 0.284
          and chk['pad_uncovered'] == 0 and chk['inside_silhouette']
          and chk['pad_clearance'] >= base_chk['pad_clearance'] - 0.001)
    print("R", R, "Lt", finfo['Lt'], "pocket", finfo['pocket_area'], "cuts", chk['copper_cuts_vs_rev9'],
          "minclr", chk['copper_min_clearance'], "padclr", chk['pad_clearance'], "area", chk['area'],
          "OK" if ok else "")
    if ok:
        chosen = (poly, finfo, chk)
        break
assert chosen, "no feasible fillet radius passes"
poly, finfo, chk = chosen
print("CHOSEN fillet R =", finfo['R'], " stub residual =", finfo['stub_residual'], "mm")

B = lambda pt: [round(pt[0] + 100, 4), round(pt[1] + 70, 4)]
out = dict(stage="2d-main-design", fillet=dict(
    site="J2", corner="PL (diving, d=0.151)",
    type="arc tangent to front line and wall line at PL; radius capped by the 0.174 mm wall stub",
    R=finfo['R'], Lt=finfo['Lt'], stub_mm=round(stub, 4), stub_residual_mm=finfo['stub_residual'],
    interior_angle_deg=round(phi, 2), pocket_area_mm2=finfo['pocket_area'],
    Tf_case=[round(v, 4) for v in finfo['Tf']], Tw_case=[round(v, 4) for v in finfo['Tw']],
    O_case=[round(v, 4) for v in finfo['O']], W0_case=[round(v, 4) for v in finfo['W0']],
    arc_mid_case=[round(v, 4) for v in finfo['arc_mid']],
    Tf_board=B(finfo['Tf']), Tw_board=B(finfo['Tw']), O_board=B(finfo['O']),
    W0_board=B(finfo['W0']), arc_mid_board=B(finfo['arc_mid'])),
    corners_case={ref: {k: [round(v, 4) for v in spec[ref][k]] for k in ('PL', 'PR')} for ref in ('J2', 'J3')},
    checks=chk, checks_2c_candidate=base_chk)
json.dump(out, open(HERE / 'stage2d.json', 'w'), indent=1)
json.dump({'main_final': [list(c) for c in poly.exterior.coords]},
          open(HERE / 'stage2d-polys.json', 'w'), indent=1)
print("saved stage2d.json + stage2d-polys.json")
print("final checks:", json.dumps(chk))
