"""F2 detail: locate the grown tray intersections; tab vs Wing contact volumes."""
import sys, json
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import numpy as np
import fitlibF as FF
from build123d import Pos, Polygon as BPoly, extrude as b_extrude

RT = '/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime'
bj = json.load(open(f'{RT}/f2-board.json'))
bodies = dict(FF.bodies_at(17, -2.65))
main = bodies['main']; bb = main.bounding_box()
refs = ('H1', 'H2', 'H3')
case_anchor = {}
for ref in refs:
    w = bodies[f'washer-main-{ref}'].bounding_box()
    case_anchor[ref] = ((w.min.X + w.max.X) / 2, (w.min.Y + w.max.Y) / 2)
P = np.array([bj['anchors_rev7'][r] for r in refs]); Q = np.array([case_anchor[r] for r in refs])
pc, qc = P.mean(0), Q.mean(0)
U, S, Vt = np.linalg.svd((P - pc).T @ (Q - qc))
R = Vt.T @ U.T; t = qc - R @ pc

def board_solid(pts):
    A = np.array(pts, dtype=float) @ R.T + t
    face = BPoly(*[tuple(p) for p in A[:-1]])
    return Pos(0, 0, bb.min.Z) * b_extrude(face, amount=bb.max.Z - bb.min.Z)

old = board_solid(bj['outline_rev7']); ext = board_solid(bj['outline_rev8']); tabs = ext - old
print('main bb Z:', bb.min.Z, bb.max.Z)
for nm, s in (('old', old), ('ext', ext)):
    b2 = s.bounding_box(); print(nm, 'Z', round(b2.min.Z,2), round(b2.max.Z,2), 'vol', round(s.volume,1))
for name in ('tray-left', 'tray-right', 'wing_left', 'wing_right'):
    s = bodies[name]
    inter_new = ext & s; inter_old = old & s
    tv = (tabs & s).volume
    if inter_new.volume > 0 and inter_old.volume > 0:
        grown = inter_new - inter_old
    elif inter_new.volume > 0:
        grown = inter_new
    else:
        grown = inter_new
    gbb = grown.bounding_box() if grown.volume > 0 else None
    print(f'{name}: tab-overlap {tv:.3f} mm3; grown {grown.volume:.3f} mm3',
          ('bbox X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f' % (gbb.min.X, gbb.max.X, gbb.min.Y, gbb.max.Y, gbb.min.Z, gbb.max.Z)) if gbb else '')
# tab extents in case frame
tb = tabs.bounding_box()
print('tabs bbox: X %.2f..%.2f Y %.2f..%.2f Z %.2f..%.2f' % (tb.min.X, tb.max.X, tb.min.Y, tb.max.Y, tb.min.Z, tb.max.Z))
# tray outer bounds (silhouette reference)
for name in ('tray-left', 'tray-right'):
    sb = bodies[name].bounding_box()
    print(f'{name} bounds: X {sb.min.X:.2f}..{sb.max.X:.2f} Y {sb.min.Y:.2f}..{sb.max.Y:.2f} Z {sb.min.Z:.2f}..{sb.max.Z:.2f}')
