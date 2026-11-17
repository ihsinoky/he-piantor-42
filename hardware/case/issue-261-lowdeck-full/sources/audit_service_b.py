"""Issue #261 gate 3, Phase B (peel model): the Wing lifts; the FPC peels
out of the formed channel progressively — Wing-side stations lift with
the Wing, the Main-side drape stays until the sheet is clear, then the
whole assembly translates out NW. Wing-attached bodies (Wing PCB, its
underside set, switch envelopes, POM spacers, Wing ZIF) move with the
Wing and are excluded from the fixed set."""
import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-lowdeck/.issue261-runtime')
import audit_static as A
import fitlib18 as F
import repair18_lib as R
from build123d import Pos

EXCL = ('shell', 'plateau', 'strip', 'plate-', 'plate_', 'plate-screw',
        'wing_right', 'underside-right', 'switch-envelope-R', 'POM-right')
fixed = [(n, s) for n, s in A.bodies if not any(k in n for k in EXCL)]
print('fixed bodies:', len(fixed), flush=True)

def audit_solids(tag, solids):
    hits = []
    for sname, solid in solids:
        bb = solid.bounding_box()
        for n, bs in fixed:
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

DRAPE = A.CTRL_R[:-1] + [(16.5, 33.5, 6.60), (19.5, 36.5, 6.55)]
all_hits = []
drape = A.sheet(A.catmull(DRAPE))
all_hits += audit_solids('drape-static', [('drape', drape)])
zifw = A.zifs['ZIF-wing-right']
# Peel poses: lift control points 0..8 (through the climb top) by dz,
# point 9 by dz/2, rest unchanged; ZIF moves with the Wing.
for dz in (2.5, 5.0):
    ctrl = [(x, y, z + (dz if i <= 8 else dz / 2 if i == 9 else 0.0))
            for i, (x, y, z) in enumerate(DRAPE)]
    s = A.sheet(A.catmull(ctrl))
    all_hits += audit_solids(f'peel{dz}', [('drape', s),
                                           ('ZIF-wing-right', Pos(0, 0, dz) * zifw)])
# Clear poses: whole assembly translated out.
for dx, dy, dz in [(-6, -8, 7.0), (-12, -17, 9.0), (-19, -26, 12.0), (-26, -36, 16.0)]:
    ms = [('drape', Pos(dx, dy, dz) * drape), ('ZIF-wing-right', Pos(dx, dy, dz) * zifw)]
    all_hits += audit_solids(f'out{dx},{dy},{dz}', ms)
print('TOTAL HITS:', all_hits if all_hits else 'NONE')
print('DONE')
