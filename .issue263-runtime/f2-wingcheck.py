"""F2 Wing check: section of fitlib wing solids at board mid-Z vs the true
Wing Rev.5 outlines translated by the J_WING->envelope-centre offset."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
from build123d import Box, Pos
from shapely.geometry import Polygon
from shapely.ops import unary_union

RT = '/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime'
wj = json.load(open(f'{RT}/f2-wings.json'))
bodies = dict(FF.bodies_at(17, -2.65))

def section_polys(solid, z):
    bb = solid.bounding_box()
    slab = Pos(bb.center().X, bb.center().Y, z) * Box(3000, 3000, 0.05)
    sec = solid & slab
    polys = []
    for f in sec.faces():
        pts = [(round(v.X, 2), round(v.Y, 2)) for v in f.outer_wire().vertices()]
        if len(pts) >= 3:
            polys.append(Polygon(pts))
    return unary_union([q for q in polys if q.is_valid and q.area > 0.01])

for side, wname, env in (('right', 'wing_right', (27.0, -37.5)), ('left', 'wing_left', (-27.0, -37.5))):
    sp = section_polys(bodies[wname], 5.3)
    d = wj[f'wing-rev5-17mm-{side}']
    off = (env[0] - d['jw_pos'][0], env[1] - d['jw_pos'][1])
    true = Polygon([(x + off[0], y + off[1]) for x, y in d['outline']])
    print(f'{side}: study section area {sp.area:.1f} mm2, true outline area {true.area:.1f} mm2, '
          f'symdiff {sp.symmetric_difference(true).area:.1f} mm2, study bounds '
          f'{[round(v,1) for v in sp.bounds]}, true bounds {[round(v,1) for v in true.bounds]}', flush=True)
    # restrict comparison to the tab region (near Main seam)
    from shapely.geometry import box as sbox
    region = sbox(15, 25, 40, 55) if side == 'right' else sbox(-40, 25, -15, 55)
    print(f'   tab region: study {sp.intersection(region).area:.1f} mm2, true {true.intersection(region).area:.1f} mm2, '
          f'overlap-in-region study-vs-true symdiff {sp.intersection(region).symmetric_difference(true.intersection(region)).area:.1f} mm2', flush=True)
print('done')
