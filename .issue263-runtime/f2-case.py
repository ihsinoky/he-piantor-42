"""F2 step B: board->case transform from H1/H2/H3 washers; extended Main solid
vs all case bodies (intersection comparison against the Rev.7 'main' baseline)
+ tab clearance distances. Case bodies: #261 audit set (fitlibF.bodies_at)."""
import sys, json, math
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import numpy as np
import fitlibF as FF
from build123d import Box, Pos, Face, Polygon as BPoly, Solid, extrude as b_extrude
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

RT = '/home/hatch/workspace/projects/he-piantor-boards/.issue263-runtime'
bj = json.load(open(f'{RT}/f2-board.json'))
bodies = dict(FF.bodies_at(17, -2.65))
main = bodies['main']
bb = main.bounding_box()
print('main solid Z range:', round(bb.min.Z, 2), round(bb.max.Z, 2), 'XY bounds:',
      (round(bb.min.X, 1), round(bb.max.X, 1)), (round(bb.min.Y, 1), round(bb.max.Y, 1)), flush=True)

# case-frame anchors from washer bounds centres
case_anchor = {}
for ref in ('H1', 'H2', 'H3'):
    w = bodies[f'washer-main-{ref}'].bounding_box()
    case_anchor[ref] = ((w.min.X + w.max.X) / 2, (w.min.Y + w.max.Y) / 2)
print('case anchors:', {k: (round(v[0], 2), round(v[1], 2)) for k, v in case_anchor.items()}, flush=True)

# Kabsch fit board->case (allow reflection)
refs = ('H1', 'H2', 'H3')
P = np.array([bj['anchors_rev7'][r] for r in refs])
Q = np.array([case_anchor[r] for r in refs])
pc, qc = P.mean(0), Q.mean(0)
H = (P - pc).T @ (Q - qc)
U, S, Vt = np.linalg.svd(H)
R = Vt.T @ U.T
t = qc - R @ pc
resid = np.linalg.norm((P @ R.T + t) - Q, axis=1)
print('transform R det:', round(float(np.linalg.det(R)), 3), 'residuals mm:', [round(float(r), 4) for r in resid], flush=True)

def to_case(pts):
    A = np.array(pts, dtype=float)
    return (A @ R.T + t).tolist()

# validate: transformed Rev.7 outline vs 'main' section polygon
zmid = (bb.min.Z + bb.max.Z) / 2
slab = Pos(bb.center().X, bb.center().Y, zmid) * Box(2000, 2000, 0.05)
sec = main & slab
sec_verts = {(round(v.X, 2), round(v.Y, 2)) for v in sec.vertices()}
o7 = to_case(bj['outline_rev7'])
def pt_poly_dist(p, poly):
    best = 1e9
    for a, b in zip(poly, poly[1:] + poly[:1]):
        ax, ay = a; bx, by = b; px, py = p
        dx, dy = bx - ax, by - ay; L2 = dx * dx + dy * dy
        u = 0 if L2 == 0 else max(0, min(1, ((px - ax) * dx + (py - ay) * dy) / L2))
        best = min(best, math.hypot(px - (ax + u * dx), py - (ay + u * dy)))
    return best
dev = max(pt_poly_dist(list(v), o7) for v in sec_verts)
print('Rev.7 outline vs case main section: max vertex deviation mm:', round(dev, 3), flush=True)

# board solids in case frame: extrude transformed outlines over main's Z range
def board_solid(outline_pts):
    o = to_case(outline_pts)
    face = BPoly(*[tuple(p) for p in o[:-1]])
    s = b_extrude(face, amount=bb.max.Z - bb.min.Z)
    return Pos(0, 0, bb.min.Z - s.bounding_box().min.Z) * s
old = board_solid(bj['outline_rev7'])
ext = board_solid(bj['outline_rev8'])
# tab solids: extended board minus old board
tabs = ext - old
print('tab solids volume mm3:', round(tabs.volume, 2), flush=True)
# does the extended board stay inside the case design's Main region solid?
excess = ext - main
print('extended board outside case-main region: mm3 =', round(excess.volume, 3), flush=True)

EXCLUDE = ('Main-study-', 'washer-main-', 'screw-main-', 'EZmate-Main', 'Main-GH-')
def excluded(n):
    return n == 'main' or any(n.startswith(x) for x in EXCLUDE)

report = {'transform_residuals_mm': [round(float(r), 4) for r in resid],
          'rev7_section_deviation_mm': round(dev, 3),
          'extended_outside_case_main_region_mm3': round(excess.volume, 3),
          'tab_volume_mm3': round(tabs.volume, 2), 'hits': []}
for n, s in bodies.items():
    if excluded(n):
        continue
    try:
        v_old = (old & s).volume
    except Exception:
        v_old = 0.0
    try:
        v_new = (ext & s).volume
    except Exception:
        v_new = 0.0
    if v_new > max(0.01, v_old + 0.01):
        report['hits'].append({'body': n, 'old_mm3': round(v_old, 3), 'new_mm3': round(v_new, 3)})
print('NEW/GROWN intersections:', json.dumps(report['hits']), flush=True)

# tab clearance: min distance from tab solids to every non-excluded body within 8mm bbox
tres = []
tb = tabs.bounding_box()
for n, s in bodies.items():
    if excluded(n):
        continue
    sb = s.bounding_box()
    if sb.min.X > tb.max.X + 8 or sb.max.X < tb.min.X - 8 or sb.min.Y > tb.max.Y + 8 or sb.max.Y < tb.min.Y - 8:
        continue
    d = BRepExtrema_DistShapeShape(tabs.wrapped, s.wrapped)
    tres.append((n, round(float(d.Value()), 3)))
tres.sort(key=lambda x: x[1])
report['tab_nearest_bodies'] = tres[:10]
print('tab nearest bodies:', tres[:10], flush=True)
json.dump(report, open(f'{RT}/f2-result.json', 'w'), indent=1)
print('F2 DONE')
