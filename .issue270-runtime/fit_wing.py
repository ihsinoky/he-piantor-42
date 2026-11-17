"""Find the correct Wing fitted placement: anchor J_WING envelope centre
at (+-27,-37.5) case, try rotation angles; the right one reproduces the
REPORT seam 0.5215 (L) / 0.5221 (R) and keeps the wing inside the case
footprint (+-145.5 x +-73)."""
import json, math
import pcbnew as p
from shapely.geometry import Polygon

MM = 1e6
ROOT = '/home/hatch/workspace/projects/he-piantor-mainoutline'
Q = ROOT + '/hardware/kicad/qualification/issue-263-implementation'


def outline(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return [(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())]


def rot(pt, deg):
    th = math.radians(deg); c, s = math.cos(th), math.sin(th)
    return (pt[0] * c - pt[1] * s, pt[0] * s + pt[1] * c)


g = json.load(open('geometry.json'))
main = Polygon(g['main_rev8_outline'])

for side, sgn in (('left', -1), ('right', 1)):
    b = p.LoadBoard(f'{Q}/wing-rev5-17mm-{side}/main.kicad_pcb')
    oly = outline(b)
    f = [x for x in b.GetFootprints() if x.GetReference() == 'J_WING'][0]
    pads = {a.GetNumber(): (a.GetPosition().x / MM, a.GetPosition().y / MM) for a in f.Pads()}
    row = [pads[str(k)] for k in range(1, 15)]
    rc = (sum(q[0] for q in row) / 14, sum(q[1] for q in row) / 14)
    mps = [pads[k] for k in pads if k == 'MP']
    mc = (sum(q[0] for q in mps) / len(mps), sum(q[1] for q in mps) / len(mps))
    dv = (mc[0] - rc[0], mc[1] - rc[1]); L = math.hypot(*dv)
    env = (rc[0] + 2.40 * dv[0] / L, rc[1] + 2.40 * dv[1] / L)  # board-frame envelope centre
    target = (sgn * 27.0, -37.5)
    print(f'--- {side}: board envelope centre {env}')
    for deg in (30.5, -30.5, 29.5, -29.5, 30.0, -30.0):
        placed = []
        for pt in oly:
            q = rot((pt[0] - env[0], pt[1] - env[1]), deg)
            placed.append((q[0] + target[0], q[1] + target[1]))
        wp = Polygon(placed)
        print(f'  rot {deg:+.1f}: seam {wp.distance(main):.4f}  bbox '
              f'{[round(v,1) for v in wp.bounds]}  inter {wp.intersection(main).area:.3f}')
