"""F2 Wing placement fit: rotate the true Wing outline about the J_WING anchor
(envelope centre in case frame) to best match the fitlib study section; then
measure the Main tab overlap against the TRUE placed Wing outline."""
import sys, json, math
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import numpy as np
import fitlibF as FF
from build123d import Box, Pos, Polygon as BPoly, extrude as b_extrude
from shapely.geometry import Polygon
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

# Main tab polygons in case frame (translation -100,-70 verified exact)
def to_case(pts):
    return [(x - 100.0, y - 70.0) for x, y in pts]
tabs_poly = Polygon(to_case(bj['outline_rev8'])).difference(Polygon(to_case(bj['outline_rev7'])))

for side, wname, env in (('right', 'wing_right', (27.0, -37.5)), ('left', 'wing_left', (-27.0, -37.5))):
    sp = section_poly(bodies[wname], 5.3)
    d = wj[f'wing-rev5-17mm-{side}']
    jx, jy = d['jw_pos']
    base = Polygon([(x - jx, y - jy) for x, y in d['outline']])  # J_WING at origin
    best = None
    for deg10 in range(-900, 901, 5):
        deg = deg10 / 10.0
        cand = shp_translate(shp_rotate(base, deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
        sd = sp.symmetric_difference(cand).area
        if best is None or sd < best[1]:
            best = (deg, sd, cand)
    deg, sd, cand = best
    print(f'{side}: best rotation {deg} deg, symdiff {sd:.1f} mm2 (study area {sp.area:.0f})', flush=True)
    ov = tabs_poly.intersection(cand)
    print(f'   TRUE wing vs Main tabs: overlap area {ov.area:.2f} mm2 (= {ov.area * 1.2:.1f} mm3 in band)', flush=True)
    if ov.area > 0.001:
        print('   overlap bounds:', [round(v, 2) for v in ov.bounds], flush=True)
print('done')
