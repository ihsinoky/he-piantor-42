"""Issue #261 gate 3 (revised): service-motion audit, right side.
Procedure: case top opened (shell/plateau/strip bodies excluded), switch
plate + its screws removed (plate-*, plate-screw-* excluded), then:
Phase A: unplug Main-end ZIF — only the FPC tip (final straight) moves,
  swept out along -DIR vs fixed bodies.
Phase B: Wing lifted out with the FPC attached. The unplugged FPC is
  modelled in its extraction drape: installed path truncated at the
  final-straight start, free end draped into the seam channel. The drape
  shape is audited statically first, then swept rigidly with the Wing.
Left side is the mirror (same channel/corridor geometry)."""
import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-lowdeck/.issue261-runtime')
import audit_static as A
import fitlib18 as F
import repair18_lib as R
from build123d import Pos

EXCL = ('shell', 'plateau', 'strip', 'plate-', 'plate_', 'plate-screw')
fixed = [(n, s) for n, s in A.bodies if not any(k in n for k in EXCL)]
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
# Phase A: tip sweep (final-straight sheet segment only)
tip = A.sheet(A.catmull([(13.44, 30.21, 6.90), (20.92, 38.24, 6.90)]))
for t in (1.25, 2.5, 3.75, 5.0):
    moved = Pos(-DIR[0] * t, -DIR[1] * t, 0) * tip
    all_hits += audit_solids(f'A{t}', [('tip', moved)], fixed)
# Extraction drape shape: installed path to the straight start, then the
# free end drapes SE and down into the seam channel.
DRAPE = A.CTRL_R[:-1] + [(16.5, 33.5, 5.60), (19.5, 36.5, 5.35)]
drape = A.sheet(A.catmull(DRAPE))
all_hits += audit_solids('drape-static', [('drape', drape)], fixed)
# Phase B: sweep drape + Wing-ZIF with the Wing lift path
zifw = A.zifs['ZIF-wing-right']
for dx, dy, dz in [(0, 0, 2.5), (0, 0, 5.0), (-6, -8, 7.0),
                   (-12, -17, 9.0), (-19, -26, 12.0), (-26, -36, 16.0)]:
    ms = [('drape', Pos(dx, dy, dz) * drape), ('ZIF-wing-right', Pos(dx, dy, dz) * zifw)]
    all_hits += audit_solids(f'B{dx},{dy},{dz}', ms, fixed)
print('TOTAL HITS:', all_hits if all_hits else 'NONE')
print('DONE')
