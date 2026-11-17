"""Issue #270 stage 2c, design v3: v2 + front line raised (parallel shift
outward) until Main copper cuts = 0 and min edge-to-copper clearance
>= 0.284 (the Rev.9 value). The diving side of the tilted front crosses
the ZIF fanout field (tracks reach d ~ 3.5 in the tab), so the line must
sit higher than the pad-only position of v2. Scan wf per project (both
sites share one rule: smallest common raise that clears both sites).
"""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
g = json.loads((HERE / 'geometry.json').read_text())
sites = json.loads((HERE / 'sites.json').read_text())
case = json.loads((HERE / 'case_geometry.json').read_text())
tray = json.loads((HERE / 'tray_local.json').read_text())
w2a = json.loads((HERE / 'wing2a.json').read_text())
probe = json.loads((HERE / 'stage2c-probe.json').read_text())
M = json.loads((HERE / 'stage2c-measure-summary.json').read_text())

rev7 = Polygon(g['main_rev7_outline'])
rev9 = Polygon(probe['rev9_outline_case'])
sil = unary_union([Polygon(p) for p in case['silhouette_parts']])
traypoly = {s: unary_union([Polygon(p) for p in tray[s]]) for s in tray}
GAP = 0.55
DEPTH = 4.738
FRONT_HALF = 16.689 / 2
BASE_D = -2.0
BASE_HALF = FRONT_HALF + (DEPTH - BASE_D) / math.tan(math.radians(60))
MIN_CLR = 0.284  # Rev.9 min edge-to-copper clearance


def to_case(site, t, d):
    A, u, n = site['A'], site['u'], site['n']
    return (A[0] + u[0] * t + n[0] * d, A[1] + u[1] * t + n[1] * d)


def line_int(P, v, Q, w):
    den = v[0] * w[1] - v[1] * w[0]
    t = ((Q[0] - P[0]) * w[1] - (Q[1] - P[1]) * w[0]) / den
    return (P[0] + v[0] * t, P[1] + v[1] * t)


def build(raise_):
    blobs, spec = [], {}
    for ref in ('J2', 'J3'):
        s = sites[ref]
        d = M[ref]
        a, m, cen = d['a'], d['m'], d['cen']
        tc = sum(s['tab_t_range_mine']) / 2
        wf = d['pad_w_max'] + 0.8364 + raise_
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

        def td(pt):
            dx, dy = pt[0] - s['A'][0], pt[1] - s['A'][1]
            return (dx * s['u'][0] + dy * s['u'][1], dx * s['n'][0] + dy * s['n'][1])

        def sw(pt):
            return ((pt[0] - cen[0]) * a[0] + (pt[1] - cen[1]) * a[1],
                    (pt[0] - cen[0]) * m[0] + (pt[1] - cen[1]) * m[1])
        spec[ref] = {'front_w': round(wf, 4), 'raise': raise_,
                     'front_seg_len': round(math.dist(PL, PR), 3),
                     'front_s_range': [round(min(sw(PL)[0], sw(PR)[0]), 3),
                                       round(max(sw(PL)[0], sw(PR)[0]), 3)],
                     'front_d_range': [round(min(td(PL)[1], td(PR)[1]), 3),
                                       round(max(td(PL)[1], td(PR)[1]), 3)],
                     'front_t_range': [round(min(td(PL)[0], td(PR)[0]), 3),
                                       round(max(td(PL)[0], td(PR)[0]), 3)],
                     'corners_case': {'PL': [round(v, 3) for v in PL],
                                      'PR': [round(v, 3) for v in PR]}}
    return unary_union([rev7] + blobs), spec


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
    r['added_vs_rev9'] = round(poly.difference(base).area, 3)
    r['removed_vs_rev9'] = round(removed.area, 3)
    return r


chosen = None
for i in range(0, 81):
    raise_ = round(i * 0.05, 2)
    cand_i, spec_i = build(raise_)
    chk = main_checks(cand_i, rev9)
    ok = (chk['copper_cuts_vs_rev9'] == 0 and chk['copper_min_clearance'] >= MIN_CLR
          and chk['pad_uncovered'] == 0 and chk['inside_silhouette'])
    print('raise', raise_, 'cuts', chk['copper_cuts_vs_rev9'], 'minclr', chk['copper_min_clearance'],
          'padclr', chk['pad_clearance'], 'sil', chk['inside_silhouette'], 'OK' if ok else '')
    if ok:
        chosen = (cand_i, spec_i, chk, raise_)
        break

assert chosen, 'no raise in scan range clears the copper'
cand, cand_spec, cand_chk, raise_ = chosen
print('CHOSEN raise', raise_)


def derive_wing(main_poly, variant):
    w_old = Polygon(w2a[variant]['outline'])
    w_new = w_old.difference(main_poly.buffer(GAP, resolution=64))
    if w_new.geom_type == 'MultiPolygon':
        w_new = max(w_new.geoms, key=lambda q: q.area)
    return w_new


def wing_check(main_poly, w_base, variant):
    w_new = w_base.difference(main_poly.buffer(GAP, resolution=64))
    if w_new.geom_type == 'MultiPolygon':
        w_new = max(w_new.geoms, key=lambda q: q.area)
    removed_extra = w_base.difference(w_new)
    r = dict(variant=variant)
    r['seam'] = round(main_poly.distance(w_new), 4)
    r['overlap'] = round(main_poly.intersection(w_new).area, 4)
    r['removed_extra_area'] = round(removed_extra.area, 3)
    floor = w_new.exterior.intersection(main_poly.buffer(1.2, resolution=64))
    ds = []
    geoms = [floor] if floor.geom_type == 'LineString' else list(getattr(floor, 'geoms', []))
    for ln in geoms:
        if ln.geom_type not in ('LineString', 'LinearRing'):
            continue
        nn = max(2, int(ln.length / 0.25))
        for i in range(nn + 1):
            ds.append(main_poly.distance(ln.interpolate(i / nn, normalized=True)))
    if ds:
        r['gap_min'] = round(min(ds), 4); r['gap_max'] = round(max(ds), 4)
    hard_hit, mind = [], 1e9
    for it in w2a[variant]['copper']:
        if it['kind'] == 'courtyard':
            continue
        geo = copper_geo(it)
        if geo.intersects(removed_extra):
            hard_hit.append((it['kind'], it.get('ref'), it.get('num'), it.get('net')))
        else:
            mind = min(mind, removed_extra.distance(geo))
    r['copper_hits_extra'] = hard_hit
    r['copper_min_dist_to_removed_extra'] = round(mind, 3) if mind < 1e9 else None
    r['inside_silhouette'] = bool(sil.covers(w_new))
    return r, w_new


res = dict(measure=M, cand_spec=cand_spec, design='v3 minimal-change + raised front line',
           chosen_raise=raise_)
res['candidate_checks'] = cand_chk
print('CANDIDATE v3 main:', json.dumps(cand_chk))

polys = {'main_rev9': [list(c) for c in rev9.exterior.coords],
         'main_cand': [list(c) for c in cand.exterior.coords], 'wings': {}}
res['wings'] = {}
for variant in ('17mm-left', '17mm-right', '16mm-left', '16mm-right'):
    w6 = derive_wing(rev9, variant)
    wr, w_cand = wing_check(cand, w6, variant)
    res['wings'][variant] = wr
    polys['wings'][variant] = dict(rev6=[list(c) for c in w6.exterior.coords],
                                   cand=[list(c) for c in w_cand.exterior.coords])
    print(' ', variant, json.dumps(wr))

json.dump(res, open(HERE / 'stage2c.json', 'w'), indent=1)
json.dump(polys, open(HERE / 'stage2c-polys.json', 'w'), indent=1)
print('saved stage2c.json + stage2c-polys.json (v3)')
