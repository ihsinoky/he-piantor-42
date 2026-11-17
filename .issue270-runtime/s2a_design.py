"""Issue #270 stage 2a: 60-degree trapezoid tabs + matched Wing notches.

Angle definition: the tab side wall makes 60 deg with the board's
slanted edge line (tab front edge is parallel to that edge); tab
interior angle at the base = 60 deg, at the front corners = 120 deg.
Wall run per side r = D / tan(60).

Main: rev7 + trapezoid blobs, identical spec both sites
(D = 4.738, front length Lf scanned, centred on each site's current
tab centre). Wing: wing_new = wing_old - buffer(main_new, g),
g = 0.55, so the notch floor is the exact 0.55 offset of the new tab
front + walls (parallel faces, uniform gap, R0.55 corner arcs).
Checks per stage2a plan; control = stage-1 harness numbers.
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

rev7 = Polygon(g['main_rev7_outline'])
rev8 = Polygon(g['main_rev8_outline'])
sil = unary_union([Polygon(p) for p in case['silhouette_parts']])
traypoly = {s: unary_union([Polygon(p) for p in tray[s]]) for s in tray}
CUR_TRAY = {'L': 3.284, 'R': 3.004}
GAP = 0.55
DEPTH = 4.738


def to_case(site, t, d):
    A, u, n = site['A'], site['u'], site['n']
    return (A[0] + u[0] * t + n[0] * d, A[1] + u[1] * t + n[1] * d)


def make_main(Lf):
    r = DEPTH / math.tan(math.radians(60.0))
    blobs = []
    for ref in ('J2', 'J3'):
        s = sites[ref]
        tc = sum(s['tab_t_range_mine']) / 2
        pts = [(tc - Lf / 2 - r, -2.0), (tc - Lf / 2, DEPTH),
               (tc + Lf / 2, DEPTH), (tc + Lf / 2 + r, -2.0)]
        blobs.append(Polygon([to_case(s, t, d) for t, d in pts]))
    return unary_union([rev7] + blobs), r


def copper_geo(it):
    if it['kind'] == 'track':
        return LineString([it['a'], it['b']]).buffer(it['width'] / 2, cap_style=2)
    if it['kind'] == 'via':
        return Point(it['centre']).buffer(it['dia'] / 2)
    return Polygon(it['corners'])


def main_checks(poly):
    r = {}
    worst, worst_id, uncovered = 1e9, None, 0
    for ref, lst in g['main_zif_pads'].items():
        for pd in lst:
            for c in pd['bbox']:
                pt = Point(c)
                if not poly.covers(pt):
                    uncovered += 1
                d = poly.exterior.distance(pt)
                if d < worst:
                    worst, worst_id = d, f"{ref}.{pd['num']}"
    r['pad_clearance'] = round(worst, 4); r['pad_worst'] = worst_id; r['pad_uncovered'] = uncovered
    sw, sun = 1e9, 0
    for ref in ('J2', 'J3'):
        s = sites[ref]
        for t, d in s['silk_td']:
            pt = Point(to_case(s, t, d))
            if not poly.covers(pt):
                sun += 1
            sw = min(sw, poly.exterior.distance(pt))
    r['silk_min_dist'] = round(sw, 3); r['silk_uncovered'] = sun
    r['inside_silhouette'] = bool(sil.covers(poly))
    growth = poly.difference(rev7)
    for side in ('L', 'R'):
        half = Polygon([(-200, -200), (0, -200), (0, 200), (-200, 200)]) if side == 'L' else \
               Polygon([(0, -200), (200, -200), (200, 200), (0, 200)])
        a = growth.intersection(traypoly[side]).intersection(half).area
        r[f'tray_{side}_mm2'] = round(a, 3)
        r[f'tray_{side}_delta_mm3'] = round((a - CUR_TRAY[side]) * 1.2, 2)
    r['removed_vs_rev8'] = round(rev8.difference(poly).area, 4)
    r['area'] = round(poly.area, 2)
    cuts, minclr = 0, 1e9
    removed = rev8.difference(poly)
    for it in g['main_copper_near_tabs']:
        geo = copper_geo(it)
        if geo.intersects(removed):
            cuts += 1
        minclr = min(minclr, poly.exterior.distance(geo))
    r['copper_cuts'] = cuts
    r['copper_min_clearance'] = round(minclr, 3)
    return r


def wing_checks(main_poly, variant):
    w_old = Polygon(w2a[variant]['outline'])
    w_new = w_old.difference(main_poly.buffer(GAP, resolution=64))
    if w_new.geom_type == 'MultiPolygon':
        w_new = max(w_new.geoms, key=lambda q: q.area)
    removed = w_old.difference(w_new)
    r = dict(variant=variant)
    r['seam'] = round(main_poly.distance(w_new), 4)
    r['overlap'] = round(main_poly.intersection(w_new).area, 4)
    r['removed_area'] = round(removed.area, 3)
    r['removed_bbox'] = [round(v, 1) for v in removed.bounds] if not removed.is_empty else None
    r['inside_silhouette'] = bool(sil.covers(w_new))
    # gap uniformity: sample the new boundary within 1.2mm of Main
    from shapely.ops import unary_union as uu
    floor = w_new.exterior.intersection(main_poly.buffer(1.2, resolution=64))
    ds = []
    if not floor.is_empty:
        geoms = [floor] if floor.geom_type == 'LineString' else list(getattr(floor, 'geoms', []))
        for ln in geoms:
            if ln.geom_type not in ('LineString', 'LinearRing'):
                continue
            n = max(2, int(ln.length / 0.25))
            for i in range(n + 1):
                pt = ln.interpolate(i / n, normalized=True)
                ds.append(main_poly.distance(pt))
    if ds:
        r['gap_min'] = round(min(ds), 4); r['gap_max'] = round(max(ds), 4)
        r['gap_samples'] = len(ds)
    # copper: hard classes pad/track/via; courtyard reported apart
    hard_hit, cy_hit, mind = [], [], 1e9
    for it in w2a[variant]['copper']:
        geo = copper_geo(it)
        if it['kind'] == 'courtyard':
            if geo.intersects(removed):
                cy_hit.append(it['ref'])
            continue
        if geo.intersects(removed):
            hard_hit.append((it['kind'], it.get('ref'), it.get('num'), it.get('net')))
        else:
            mind = min(mind, removed.distance(geo))
    r['copper_hits'] = hard_hit
    r['courtyard_hits'] = sorted(set(cy_hit))
    r['copper_min_dist_to_removed'] = round(mind, 3) if mind < 1e9 else None
    return r, w_new


results = {}
polys = {}
for Lf in (15.689, 16.689):
    mp, run = make_main(Lf)
    key = f'Lf{Lf}'
    results[key] = dict(wall_run=round(run, 4), main=main_checks(mp))
    results[key]['wings'] = {}
    for variant in ('17mm-left', '17mm-right', '16mm-left', '16mm-right'):
        wr, w_new = wing_checks(mp, variant)
        results[key]['wings'][variant] = wr
        if Lf == 16.689:
            polys[variant] = [list(c) for c in w_new.exterior.coords]
    if Lf == 16.689:
        polys['main'] = [list(c) for c in mp.exterior.coords]
    print(key, json.dumps(results[key]['main']))
    for v, wr in results[key]['wings'].items():
        print('  ', v, json.dumps(wr))

json.dump(dict(results=results, polys=polys, gap=GAP, depth=DEPTH),
          open(HERE / 'stage2a.json', 'w'))
print('saved stage2a.json')
