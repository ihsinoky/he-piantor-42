"""Diagnose v2 copper cuts: which items, where (in per-site (t,d) frames)."""
import json, math
from pathlib import Path
from shapely.geometry import Polygon, Point, LineString
from shapely.ops import unary_union

HERE = Path(__file__).resolve().parent
g = json.loads((HERE / 'geometry.json').read_text())
sites = json.loads((HERE / 'sites.json').read_text())
probe = json.loads((HERE / 'stage2c-probe.json').read_text())
polys = json.loads((HERE / 'stage2c-polys.json').read_text())

rev9 = Polygon(probe['rev9_outline_case'])
cand = Polygon(polys['main_cand'])
removed = rev9.difference(cand)
print('removed area', round(removed.area, 3), 'parts:',
      [round(p.area, 2) for p in getattr(removed, 'geoms', [removed])])


def copper_geo(it):
    if it['kind'] == 'track':
        return LineString([it['a'], it['b']]).buffer(it['width'] / 2, cap_style=2)
    if it['kind'] == 'via':
        return Point(it['centre']).buffer(it['dia'] / 2)
    return Polygon(it['corners'])


def td(site, pt):
    dx, dy = pt[0] - site['A'][0], pt[1] - site['A'][1]
    return (dx * site['u'][0] + dy * site['u'][1], dx * site['n'][0] + dy * site['n'][1])


for it in g['main_copper_near_tabs']:
    geo = copper_geo(it)
    inter = geo.intersection(removed)
    if not inter.is_empty:
        c = inter.representative_point()
        near = min(sites, key=lambda r: math.dist(c.coords[0], sites[r]['origin']))
        print('CUT', it['kind'], {k: it.get(k) for k in ('ref', 'num', 'net', 'width', 'dia')},
              'inter area', round(inter.area, 4), 'at case', [round(v, 2) for v in c.coords[0]],
              '(t,d)@' + near, [round(v, 2) for v in td(sites[near], c.coords[0])])
    else:
        d = cand.exterior.distance(geo)
        if d < 0.30:
            c = geo.representative_point()
            near = min(sites, key=lambda r: math.dist(c.coords[0], sites[r]['origin']))
            print('CLOSE', round(d, 3), it['kind'], {k: it.get(k) for k in ('ref', 'num', 'net')},
                  '(t,d)@' + near, [round(v, 2) for v in td(sites[near], c.coords[0])])
