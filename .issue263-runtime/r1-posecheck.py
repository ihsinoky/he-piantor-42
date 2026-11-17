"""R1 pose validation for 16mm variants: fitlib wing section vs true outline
transformed by the J_WING->envelope mapping (same method as F2 wingcheck)."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-42/.issue194-runtime/geometry/lib/python3.12/site-packages')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
from build123d import Box, Pos
from shapely.geometry import Polygon, box as sbox
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
from shapely.ops import unary_union

RT = '/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime'
wj = json.load(open(f'{RT}/r1-wings.json'))

def section_polys(solid, z):
    bb = solid.bounding_box()
    sec = solid & (Pos(bb.center().X, bb.center().Y, z) * Box(3000, 3000, 0.05))
    polys = []
    for f in sec.faces():
        pts = [(round(v.X, 2), round(v.Y, 2)) for v in f.outer_wire().vertices()]
        if len(pts) >= 3:
            polys.append(Polygon(pts))
    return unary_union([q for q in polys if q.is_valid and q.area > 0.01])

for pitch in (16, 17):
    bodies = dict(FF.bodies_at(pitch, -2.65))
    for side, wname, env, deg in (('right', 'wing_right', (27.0, -37.5), -30.5),
                                  ('left', 'wing_left', (-27.0, -37.5), 30.5)):
        sp = section_polys(bodies[wname], 5.3)
        d = wj[f'wing-rev5-{pitch}mm-{side}']
        jx, jy = d['jw_pos']
        base = Polygon([(x - jx, y - jy) for x, y in d['outline']])
        true = shp_translate(shp_rotate(base, deg, origin=(0, 0)), xoff=env[0], yoff=env[1])
        region = sbox(15, 25, 40, 55) if side == 'right' else sbox(-40, 25, -15, 55)
        sd_full = sp.symmetric_difference(true).area / true.area * 100
        sd_reg = sp.intersection(region).symmetric_difference(true.intersection(region)).area
        print(f'{pitch}mm {side}: full symdiff {sd_full:.1f}% of outline; tab-region symdiff '
              f'{sd_reg:.2f} mm2 (study {sp.intersection(region).area:.1f} vs true '
              f'{true.intersection(region).area:.1f})', flush=True)
print('done')
