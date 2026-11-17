"""Tray material near the Main tab zones at board Z (4.70..5.90).

Intersect tray solids with a local window box per side, tessellate,
project triangles to XY, union -> local tray-material polygon.
Validation: (rev8-rev7) growth ∩ local tray ~= 3.283 (L) / 3.008 (R) mm2.
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
trays = [bodies['tray-left'], bodies['tray-right']]

WIN = {'L': (-48, 20, -2, 72), 'R': (2, 20, 48, 72), 'C': (-20, -5, 20, 30)}  # x0,y0,x1,y1 case mm


def local_tray(x0, y0, x1, y1):
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    box = Pos(cx, cy, 5.3) * Box(x1 - x0, y1 - y0, 1.2)
    tris = []
    for t in trays:
        s = t & box
        if s is None:
            continue
        verts, idx = s.tessellate(0.05)
        P = [(v.X, v.Y) for v in verts]
        for a, b, c in idx:
            tri = Polygon([P[a], P[b], P[c]])
            if tri.is_valid and tri.area > 1e-9:
                tris.append(tri)
    return unary_union(tris)


g = json.load(open('geometry.json'))
rev7 = Polygon(g['main_rev7_outline'])
rev8 = Polygon(g['main_rev8_outline'])
growth = rev8.difference(rev7)

out = {}
for side, (x0, y0, x1, y1) in WIN.items():
    lt = local_tray(x0, y0, x1, y1)
    inter = growth.intersection(lt)
    print(f'{side}: local tray area {lt.area:.1f}, current growth∩tray {inter.area:.3f} mm2 '
          f'(expect 3.283 L / 3.008 R)')
    parts = lt.geoms if lt.geom_type == 'MultiPolygon' else [lt]
    out[side] = [[list(c) for c in q.exterior.coords] for q in parts]
json.dump(out, open('tray_local.json', 'w'))
print('saved tray_local.json')
