"""Issue #270 stage 2c: connector-aligned tab candidate - design + checks.

Frames: harness case frame. Per-site (t,d) frames from sites.json
(t along Rev.7 slanted edge, d outward normal). Connector axis from
stage2c-measure.json (PCA over signal-pad centres, Rev.9 board).
Candidate per site: trapezoid blob in the connector frame (s along
connector axis, w along its outward normal):
  front edge parallel to connector axis at w = w_padmax + TARGET_CLR,
  front s-range = pad-corner s-range widened to cover courtyard + margin,
  walls at 60 deg interior from the front corners back past the edge line.
Candidate Main = rev7 + blobs (same construction as stage 2a).
Checks reuse the stage-2a yardsticks (adapted main_checks / wing_checks).
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
meas = json.loads((HERE / 'stage2c-measure.json').read_text())
probe = json.loads((HERE / 'stage2c-probe.json').read_text())

rev7 = Polygon(g['main_rev7_outline'])
rev9 = Polygon(probe['rev9_outline_case'])
sil = unary_union([Polygon(p) for p in case['silhouette_parts']])
traypoly = {s: unary_union([Polygon(p) for p in tray[s]]) for s in tray}
GAP = 0.55
TARGET_CLR = 0.8364  # Rev.9 pad-corner clearance to preserve


def to_case(site, t, d):
    A, u, n = site['A'], site['u'], site['n']
    return (A[0] + u[0] * t + n[0] * d, A[1] + u[1] * t + n[1] * d)


def ang(v):
    return math.degrees(math.atan2(v[1], v[0]))


def line_ang(v):
    a = ang(v) % 180.0
    return a


# ---------- measurements ----------
M = {}
for ref in ('J2', 'J3'):
    s = sites[ref]
    u, n = s['u'], s['n']
    a = meas[ref]['pad_axis'][:]
    if a[0] * u[0] + a[1] * u[1] < 0:
        a = [-a[0], -a[1]]
    m = (-a[1], a[0])
    if m[0] * n[0] + m[1] * n[1] < 0:
        m = (-m[0], -m[1])
    edge_la = line_ang(u)
    axis_la = line_ang(a)
    skew = abs(axis_la - edge_la)
    skew = min(skew, 180 - skew)
    # courtyard corners (case frame)
    cy = [tuple(q) for q in probe[ref]['courtyard'][0][1]]
    # pad corners from geometry.json (case frame)
    padcorners = [tuple(c) for pd in g['main_zif_pads'][ref] for c in pd['bbox']]
    cen = meas[ref]['sig_centroid']

    def sw(pt):
        return ((pt[0] - cen[0]) * a[0] + (pt[1] - cen[1]) * a[1],
                (pt[0] - cen[0]) * m[0] + (pt[1] - cen[1]) * m[1])

    pc_sw = [sw(c) for c in padcorners]
    cy_sw = [sw(c) for c in cy]
    M[ref] = dict(u=u, n=n, a=a, m=m, cen=cen, cy=cy,
                  edge_line_ang=round(edge_la, 3), axis_line_ang=round(axis_la, 3),
                  skew_deg=round(skew, 3), yaw=meas[ref]['yaw'],
                  pad_w_max=round(max(w for _, w in pc_sw), 4),
                  pad_s_range=[round(min(x for x, _ in pc_sw), 3),
                               round(max(x for x, _ in pc_sw), 3)],
                  cy_w_range=[round(min(w for _, w in cy_sw), 3),
                              round(max(w for _, w in cy_sw), 3)],
                  cy_s_range=[round(min(x for x, _ in cy_sw), 3),
                              round(max(x for x, _ in cy_sw), 3)])
    print(ref, 'edge line', M[ref]['edge_line_ang'], 'axis line', M[ref]['axis_line_ang'],
          'SKEW', M[ref]['skew_deg'], 'pad w_max', M[ref]['pad_w_max'],
          'pad s', M[ref]['pad_s_range'], 'cy s', M[ref]['cy_s_range'], 'cy w', M[ref]['cy_w_range'])

# current Rev.9 tab front angle: longest outline segment with max mean d
for ref in ('J2', 'J3'):
    s = sites[ref]
    A = s['A']
    def td(pt):
        dx, dy = pt[0] - A[0], pt[1] - A[1]
        return (dx * s['u'][0] + dy * s['u'][1], dx * s['n'][0] + dy * s['n'][1])
    coords = list(rev9.exterior.coords)
    best = None
    for p1, p2 in zip(coords, coords[1:]):
        L = math.dist(p1, p2)
        if L < 8:
            continue
        dm = (td(p1)[1] + td(p2)[1]) / 2
        if best is None or dm > best[0]:
            best = (dm, L, line_ang((p2[0] - p1[0], p2[1] - p1[1])))
    M[ref]['rev9_front'] = dict(mean_d=round(best[0], 3), len=round(best[1], 3),
                                line_ang=round(best[2], 3))
    print(ref, 'Rev.9 front seg: mean d', best[0], 'len', best[1], 'line ang', best[2],
          'vs edge line', M[ref]['edge_line_ang'])

json.dump(M, open(HERE / 'stage2c-measure-summary.json', 'w'), indent=1)
print('saved stage2c-measure-summary.json')

# ---------- candidate construction ----------
HF = 16.689 / 2  # front half-length, same as Rev.9 front length
WALL_LEN = 12.0


def copper_geo(it):
    if it['kind'] == 'track':
        return LineString([it['a'], it['b']]).buffer(it['width'] / 2, cap_style=2)
    if it['kind'] == 'via':
        return Point(it['centre']).buffer(it['dia'] / 2)
    return Polygon(it['corners'])


cand_blobs = []
cand_spec = {}
for ref in ('J2', 'J3'):
    d = M[ref]
    a, m, cen = d['a'], d['m'], d['cen']
    wf = d['pad_w_max'] + TARGET_CLR
    F1 = (-HF, wf)
    F2 = (HF, wf)
    B2 = (HF + WALL_LEN * math.sin(math.radians(60)), wf - WALL_LEN * math.cos(math.radians(60)))
    B1 = (-HF - WALL_LEN * math.sin(math.radians(60)), wf - WALL_LEN * math.cos(math.radians(60)))

    def cs(sv, wv):
        return (cen[0] + a[0] * sv + m[0] * wv, cen[1] + a[1] * sv + m[1] * wv)

    blob = Polygon([cs(*F1), cs(*F2), cs(*B2), cs(*B1)])
    cand_blobs.append(blob)
    # front segment d-range in the site (t,d) frame
    site = sites[ref]
    A = site['A']
    def td(pt):
        dx, dy = pt[0] - A[0], pt[1] - A[1]
        return (dx * site['u'][0] + dy * site['u'][1], dx * site['n'][0] + dy * site['n'][1])
    f1c, f2c = cs(*F1), cs(*F2)
    cand_spec[ref] = dict(w_front=round(wf, 4), front_len=16.689,
                          front_d_range=[round(min(td(f1c)[1], td(f2c)[1]), 3),
                                         round(max(td(f1c)[1], td(f2c)[1]), 3)],
                          front_t_range=[round(min(td(f1c)[0], td(f2c)[0]), 3),
                                         round(max(td(f1c)[0], td(f2c)[0]), 3)],
                          wall_interior_deg=120)
    print(ref, 'candidate front w', round(wf, 3), 'front d range', cand_spec[ref]['front_d_range'])

cand = unary_union([rev7] + cand_blobs)


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
    sw, sun = 1e9, 0
    for ref in ('J2', 'J3'):
        s = sites[ref]
        for t, dd in s['silk_td']:
            pt = Point(to_case(s, t, dd))
            if not poly.covers(pt):
                sun += 1
            sw = min(sw, poly.exterior.distance(pt))
    r['silk_min_dist'] = round(sw, 3); r['silk_uncovered'] = sun
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


def derive_wing(main_poly, variant):
    w_old = Polygon(w2a[variant]['outline'])
    w_new = w_old.difference(main_poly.buffer(GAP, resolution=64))
    if w_new.geom_type == 'MultiPolygon':
        w_new = max(w_new.geoms, key=lambda q: q.area)
    return w_old, w_new


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


res = dict(measure=M, cand_spec=cand_spec)
res['rev9_baseline_checks'] = main_checks(rev9, rev9)
res['candidate_checks'] = main_checks(cand, rev9)
print('REV9 baseline:', json.dumps(res['rev9_baseline_checks']))
print('CANDIDATE main:', json.dumps(res['candidate_checks']))

polys = {'main_rev9': [list(c) for c in rev9.exterior.coords],
         'main_cand': [list(c) for c in cand.exterior.coords], 'wings': {}}
res['wings'] = {}
for variant in ('17mm-left', '17mm-right', '16mm-left', '16mm-right'):
    _, w6 = derive_wing(rev9, variant)
    wr, w_cand = wing_check(cand, w6, variant)
    res['wings'][variant] = wr
    polys['wings'][variant] = dict(rev6=[list(c) for c in w6.exterior.coords],
                                   cand=[list(c) for c in w_cand.exterior.coords])
    print(' ', variant, json.dumps(wr))

json.dump(res, open(HERE / 'stage2c.json', 'w'), indent=1)
json.dump(polys, open(HERE / 'stage2c-polys.json', 'w'), indent=1)
print('saved stage2c.json + stage2c-polys.json')
