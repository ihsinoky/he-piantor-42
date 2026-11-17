"""F2 seam quantification: Rev.7 slanted edge -> true Wing outline gap profile
in the tab zones; max tab depth that keeps >=0.50 mm case-class clearance."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
from build123d import Box, Pos
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

RT = '/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime'
wj = json.load(open(f'{RT}/f2-wings.json'))
bj = json.load(open(f'{RT}/f2-board.json'))
bodies = dict(FF.bodies_at(17, -2.65))

def section_poly(solid, z):
    bb = solid.bounding_box()
    sec = solid & (Pos(bb.center().X, bb.center().Y, z) * Box(3000, 3000, 0.05))
    polys = []
    for f in sec.faces():
        pts = [(round(v.X, 2), round(v.Y, 2)) for v in f.outer_wire().vertices()]
        if len(pts) >= 3:
            q = Polygon(pts)
            if q.is_valid and q.area > 0.01:
                polys.append(q)
    return unary_union(polys)

def to_case(pts):
    return [(x - 100.0, y - 70.0) for x, y in pts]

old_poly = Polygon(to_case(bj['outline_rev7']))
new_poly = Polygon(to_case(bj['outline_rev8']))
for side, wname, env, deg in (('right', 'wing_right', (27.0, -37.5), -30.5), ('left', 'wing_left', (-27.0, -37.5), 30.5)):
    d = wj[f'wing-rev5-17mm-{side}']
    jx, jy = d['jw_pos']
    base = Polygon([(x - jx, y - jy) for x, y in d['outline']])
    wing = shp_translate(shp_rotate(base, deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
    # seam gap: distance from old board polygon to wing polygon
    gap = old_poly.distance(wing)
    # tab excursion profile: sample points along the new outline's tab edge,
    # distance to wing outline
    tab = new_poly.difference(old_poly)
    # points on tab boundary farthest into the seam: sample tab polygon boundary
    samples = []
    bnd = tab.boundary
    n = 200
    for i in range(n + 1):
        p = bnd.interpolate(i / n, normalized=True)
        samples.append((p, p.distance(wing)))
    inside = [(p, dist) for p, dist in samples if wing.contains(p)]
    maxbite = 0.0
    # bite depth: for points of the wing boundary inside the tab, distance to old edge
    wb = wing.boundary
    for i in range(n + 1):
        p = wb.interpolate(i / n, normalized=True)
        if tab.contains(p):
            maxbite = max(maxbite, p.distance(old_poly))
    print(f'{side}: seam gap old<->wing = {gap:.3f} mm; tab points inside wing: {len(inside)}/{n}; '
          f'max bite depth into wing outline = {maxbite:.2f} mm', flush=True)
print('done')
