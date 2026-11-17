"""Issue 264 gate 3: service motions, right side (left = mirror).
Case top opened + switch plate removed (EXCL as #261). Phase A: unplug
Main end - only the final segment (from F_V7 fold) moves, swept along
-DIR. NOTE: the real fold flexes open as the tail slides; the rigid sweep
is the conservative bound. Phase B: Wing lift with cable attached; the
part past F_V7 replaced by a drape (#261 offsets); stack legs modelled
at their installed z (rigid) - conservative."""
import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B
import fitlib18 as F
import repair18_lib as R
from build123d import Pos

bodies, cable_r, cable_l, zifs = B.assemble()
EXCL = ('shell', 'plateau', 'strip', 'plate-', 'plate_', 'plate-screw')
fixed = [(n, s) for n, s in bodies if not any(k in n for k in EXCL)]
print('fixed bodies:', len(fixed), flush=True)
DIR = (0.68, 0.73)

def audit_solids(tag, solids, body_list):
    hits = []
    for sname, solid in solids:
        bb = solid.bounding_box()
        for n, bs in body_list:
            b2 = bs.bounding_box()
            if (bb.max.X < b2.min.X - 1 or bb.min.X > b2.max.X + 1 or
                bb.max.Y < b2.min.Y - 1 or bb.min.Y > b2.max.Y + 1 or
                bb.max.Z < b2.min.Z - 1 or bb.min.Z > b2.max.Z + 1):
                continue
            v = R.vol_pair(solid, bs, F.bounds(solid), F.bounds(bs), repair=True)
            if v > F.HIT:
                hits.append((tag, sname, n, round(float(v), 4)))
    print(tag, 'hits:', hits, flush=True)
    return hits

all_hits = []
# Phase A: tip = final segment sheet (V7 -> T1) at installed z profile
tipV = [(14.41, 30.60, 7.54), (16.35, 32.89, 7.22), (20.92, 38.24, 6.90), (22.6, 40.0, 6.90)]
tip = B.sheet_from_pts(B.catmull(tipV), 9.6, 0.32)
for t in (1.25, 2.5, 3.75, 5.0):
    moved = Pos(-DIR[0] * t, -DIR[1] * t, 0) * tip
    all_hits += audit_solids(f'A{t}', [('tip', moved)], fixed)
# Phase B: drape = installed path to V7 (stack legs at installed z), then drape
V = B.path_V(0.0)
drapeV = V[:13] + [(17.47, 33.89, 6.24), (20.47, 36.89, 5.99)]
drape = B.sheet_from_pts(B.catmull(drapeV), 9.6, 0.32)
all_hits += audit_solids('drape-static', [('drape', drape)], fixed)
zifw = zifs['ZIF-wing-right']
for dx, dy, dz in [(0, 0, 2.5), (0, 0, 5.0), (-6, -8, 7.0),
                   (-12, -17, 9.0), (-19, -26, 12.0), (-26, -36, 16.0)]:
    ms = [('drape', Pos(dx, dy, dz) * drape), ('ZIF-wing-right', Pos(dx, dy, dz) * zifw)]
    all_hits += audit_solids(f'B{dx},{dy},{dz}', ms, fixed)
print('TOTAL HITS:', all_hits if all_hits else 'NONE')
print('DONE')
