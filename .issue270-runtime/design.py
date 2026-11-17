"""Issue #270 stage 1: candidate construction + 2D checks.

All (t,d) work uses the analyze_tabs.py edge frames (A at the Rev.7
segment start; tab ranges = tab_t_range_mine in the same frames).
 A filleted tabs: current tab quad (same t-range/depth) with front
   corners rounded R2.0 and base (re-entrant) fillets R2.0.
 B continuous edge: each tab's front line extended toward the apex,
   joined by one fillet arc R12 tangent to both front lines, centred
   on the board axis; south ends keep a semicircle blend (as A seed).
 C symmetric trapezoid tabs: identical spec both sites (depth 4.738,
   front length 16.689, wall run 1.0), centred on each current tab.
Checks: pad bbox-corner clearance (floor 0.70; current as-built
0.8197), silk containment, Wing seam >= 0.50, silhouette containment,
tray relief delta, copper cut/clearance in the tab windows.
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

rev7 = Polygon(g['main_rev7_outline'])
rev8 = Polygon(g['main_rev8_outline'])
wings = {s: Polygon(g['wings'][s]['outline']) for s in ('left', 'right')}
sil = unary_union([Polygon(p) for p in case['silhouette_parts']])
traypoly = {s: unary_union([Polygon(p) for p in tray[s]]) for s in tray}
CUR_TRAY = {'L': 3.284, 'R': 3.004}


def to_case(site, t, d):
    A, u, n = site['A'], site['u'], site['n']
    return (A[0] + u[0] * t + n[0] * d, A[1] + u[1] * t + n[1] * d)


def blob_poly(site, td_pts):
    return Polygon([to_case(site, t, d) for t, d in td_pts])


def arc_td(tc, dc, r, a0, a1, n=10):
    return [(tc + r * math.cos(math.radians(a0 + (a1 - a0) * i / n)),
             dc + r * math.sin(math.radians(a0 + (a1 - a0) * i / n))) for i in range(n + 1)]


# ---------------- candidate A ----------------
def cand_A(Rb=2.0, Rf=2.0):
    blobs = []
    for ref in ('J2', 'J3'):
        s = sites[ref]
        t0, t1 = s['tab_t_range_mine']
        D = s['depth']
        pts = [(t0 - Rb, -2.0)]
        pts += arc_td(t0 - Rb, Rb, Rb, 270, 360)      # base fillet (re-entrant)
        pts += [(t0, D - Rf)]
        pts += arc_td(t0 + Rf, D - Rf, Rf, 180, 90)   # front corner round
        pts += [(t1 - Rf, D)]
        pts += arc_td(t1 - Rf, D - Rf, Rf, 90, 0)     # front corner round
        pts += [(t1, Rb)]
        pts += arc_td(t1 + Rb, Rb, Rb, 180, 270)      # base fillet
        pts += [(t1 + Rb, -2.0)]
        blobs.append(blob_poly(s, pts))
    return unary_union([rev7] + blobs)


# ---------------- candidate C ----------------
def cand_C(wall_run=1.0):
    D = 4.738
    L = 16.689
    blobs = []
    for ref in ('J2', 'J3'):
        s = sites[ref]
        tc = sum(s['tab_t_range_mine']) / 2
        pts = [(tc - L / 2 - wall_run, -2.0), (tc - L / 2, D), (tc + L / 2, D),
               (tc + L / 2 + wall_run, -2.0)]
        blobs.append(blob_poly(s, pts))
    return unary_union([rev7] + blobs)


# ---------------- candidate B ----------------
def cand_B(Ra=12.0):
    sW, sE = sites['J2'], sites['J3']
    DW, DE = sW['depth'], sE['depth']
    nW, nE = sW['n'], sE['n']
    y = sW['A'][1] + ((DW - Ra) - (0 - sW['A'][0]) * nW[0]) / nW[1]
    O = (0.0, y)
    TW = (O[0] + Ra * nW[0], O[1] + Ra * nW[1])
    TE = (O[0] + Ra * nE[0], O[1] + Ra * nE[1])

    def t_of(site, pt):
        A, u = site['A'], site['u']
        return (pt[0] - A[0]) * u[0] + (pt[1] - A[1]) * u[1]

    tW = t_of(sW, TW)
    tE = t_of(sE, TE)
    blobs = []
    # west: south end = larger t (tab range max); semicircle there, front to tW
    t1 = sW['tab_t_range_mine'][1]
    r = DW / 2.0
    pts = [(t1, -2.0), (t1, 0.0)]
    pts += arc_td(t1, r, r, -90, 90, 24)
    pts += [(tW, DW), (tW, -2.0)]
    blobs.append(blob_poly(sW, pts))
    # east: south end = smaller t (tab range min); semicircle there, front to tE
    t0 = sE['tab_t_range_mine'][0]
    rE = DE / 2.0
    pts = [(t0, -2.0), (t0, 0.0)]
    pts += arc_td(t0, rE, rE, 270, 90, 24)
    pts += [(tE, DE), (tE, -2.0)]
    blobs.append(blob_poly(sE, pts))
    a0 = math.degrees(math.atan2(TW[1] - O[1], TW[0] - O[0]))
    a1 = math.degrees(math.atan2(TE[1] - O[1], TE[0] - O[0]))
    if a1 < a0:
        a1 += 360
    arc = arc_td(O[0], O[1], Ra, a0, a1, 48)
    pie = Polygon([O] + arc)
    return unary_union([rev7, pie] + blobs), arc


# ---------------- checks ----------------
def check(name, poly):
    if poly.geom_type == 'MultiPolygon':
        poly = max(poly.geoms, key=lambda q: q.area)
    r = dict(name=name, area=round(poly.area, 2), d_area_vs_rev8=round(poly.area - rev8.area, 2))
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
    r['seam_L'] = round(poly.distance(wings['left']), 4)
    r['seam_R'] = round(poly.distance(wings['right']), 4)
    r['inside_silhouette'] = bool(sil.covers(poly))
    growth = poly.difference(rev7)
    for side in ('L', 'R'):
        half = Polygon([(-200, -200), (0, -200), (0, 200), (-200, 200)]) if side == 'L' else \
               Polygon([(0, -200), (200, -200), (200, 200), (0, 200)])
        a = growth.intersection(traypoly[side]).intersection(half).area
        r[f'tray_{side}_mm2'] = round(a, 3)
        r[f'tray_{side}_delta_mm3'] = round((a - CUR_TRAY[side]) * 1.2, 2)
    all_tray = unary_union([traypoly[s] for s in traypoly])
    tot = growth.intersection(all_tray).area
    r['tray_total_mm2'] = round(tot, 3)
    r['tray_total_delta_mm3'] = round((tot - 6.288) * 1.2, 2)
    czone = Polygon([(-20, -5), (20, -5), (20, 20), (-20, 20)])
    r['tray_centre_mm2'] = round(growth.intersection(traypoly['C']).intersection(czone).area, 3)
    removed = rev8.difference(poly)
    r['removed_area'] = round(removed.area, 2)
    cuts, minclr = [], 1e9
    for it in g['main_copper_near_tabs']:
        if it['kind'] == 'track':
            geo = LineString([it['a'], it['b']]).buffer(it['width'] / 2, cap_style=2)
        elif it['kind'] == 'via':
            geo = Point(it['centre']).buffer(it['dia'] / 2)
        else:
            geo = Polygon(it['corners'])
        if geo.intersects(removed):
            cuts.append(it)
        else:
            minclr = min(minclr, poly.exterior.distance(geo))
    r['copper_cuts'] = len(cuts)
    kinds = {}
    for it in cuts:
        kinds[it['kind']] = kinds.get(it['kind'], 0) + 1
    r['copper_cut_kinds'] = kinds
    r['copper_min_clearance_kept'] = round(minclr, 3)
    return r, poly


results, polys = {}, {}
for nm, poly in (('current', rev8), ('A', cand_A()), ('C', cand_C())):
    results[nm], polys[nm] = check(nm, poly)
bpoly, barc = cand_B()
results['B'], polys['B'] = check('B', bpoly)
results['B']['north_excursion_mm'] = round(5.73 - min(y for _, y in barc), 2)

for nm in ('current', 'A', 'B', 'C'):
    print(nm, json.dumps(results[nm]))
json.dump(dict(results=results,
               polys={k: [list(c) for c in v.exterior.coords] for k, v in polys.items()},
               barc=barc), open(HERE / 'candidates.json', 'w'))
print('saved candidates.json')
