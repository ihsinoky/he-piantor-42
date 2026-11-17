"""Case geometry for #270: silhouette + tray material at board slab.

Bodies: fitlibF.bodies_at(17, -2.65) (the #261/#263 audit body set).
Silhouette = union of tray-left/right sections at Z=2.0 (footprint).
Tray slab = union of tray sections at Z=5.3 (middle of board slab
4.70..5.90) -> 2D proxy for pocket-relief growth area.
Validation: (rev8-rev7) growth ∩ tray slab ~= 3.28 (L) + 3.01 (R) mm2
(REPORT volumes 3.94/3.61 mm3 over the 1.2 mm board thickness).
"""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
from build123d import Box, Pos
from shapely.geometry import Polygon
from shapely.ops import unary_union

bodies = dict(FF.bodies_at(17, -2.65))
print('bodies:', sorted(bodies.keys())[:40])


def section_poly(solid, z):
    bb = solid.bounding_box()
    sec = solid & (Pos(bb.center().X, bb.center().Y, z) * Box(3000, 3000, 0.05))
    polys = []
    for f in sec.faces():
        pts = [(round(v.X, 3), round(v.Y, 3)) for v in f.outer_wire().vertices()]
        if len(pts) >= 3:
            q = Polygon(pts)
            if q.is_valid and q.area > 0.01:
                polys.append(q)
    return unary_union(polys)


trays = [bodies['tray-left'], bodies['tray-right']]
sil = unary_union([section_poly(t, 0.0) for t in trays])
slab = unary_union([section_poly(t, 5.3) for t in trays])
print('silhouette type', sil.geom_type, 'area', round(sil.area, 1), 'bounds', [round(v, 1) for v in sil.bounds])
print('tray slab area', round(slab.area, 1))

g = json.load(open('geometry.json'))
rev7 = Polygon(g['main_rev7_outline'])
rev8 = Polygon(g['main_rev8_outline'])
growth = rev8.difference(rev7)
inter = growth.intersection(slab)
print('current growth area total', round(growth.area, 2), ' growth∩tray-slab', round(inter.area, 3),
      '(expect ~6.29 = 3.28+3.01)')
# per-side split by X sign
for name, half in (('L', Polygon([(-200, -200), (0, -200), (0, 200), (-200, 200)])),
                   ('R', Polygon([(0, -200), (200, -200), (200, 200), (0, 200)]))):
    print(f'  side {name}: {inter.intersection(half).area:.3f} mm2')

out = dict(
    silhouette=[list(c) for c in (sil.geoms[0] if sil.geom_type == 'MultiPolygon' else sil).exterior.coords]
    if sil.geom_type == 'Polygon' else None,
    silhouette_parts=[[list(c) for c in q.exterior.coords] for q in
                      (sil.geoms if sil.geom_type == 'MultiPolygon' else [sil])],
    tray_slab_parts=[[list(c) for c in q.exterior.coords] for q in
                     (slab.geoms if slab.geom_type == 'MultiPolygon' else [slab])],
)
json.dump(out, open('case_geometry.json', 'w'))
print('saved case_geometry.json')
