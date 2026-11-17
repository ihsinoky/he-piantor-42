"""Issue 264 gate 3 v2: service motions, right side. Fixed set per #261's
FINAL service audit (audit_service_b.py): Wing-attached bodies (wing_right,
underside-right, switch-envelope-R, POM-right) excluded - they move with
the Wing. Tip/drape audited as per-box lists (no fuse). Phase A: unplug
sweep of the final segment. Phase B: drape + Wing ZIF swept with the lift."""
import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B
import build_audit264_v2 as V2
import fitlib18 as F
import repair18_lib as R
from build123d import Pos

bodies, zifs = V2.assemble_v2()
EXCL = ('shell', 'plateau', 'strip', 'plate-', 'plate_', 'plate-screw',
        'wing_right', 'underside-right', 'switch-envelope-R', 'POM-right')
fixed = [(n, s) for n, s in bodies if not any(k in n for k in EXCL)]
print('fixed bodies:', len(fixed), flush=True)
DIR = (0.68, 0.73)

def audit_boxes_moved(tag, boxes, dx, dy, dz, body_list):
    moved = [Pos(dx, dy, dz) * s for s in boxes] if (dx, dy, dz) != (0, 0, 0) else boxes
    hits = V2.audit_boxes(moved, body_list)
    print(tag, 'hits:', hits, flush=True)
    return hits

def seg_boxes(pts_list, w=9.6, t=0.32):
    pts = B.catmull(pts_list)
    return [s for a, b in zip(pts[:-1], pts[1:]) if (s := B.seg_box(a, b, w, t)) is not None]

all_hits = []
tipV = [(14.41, 30.60, 7.54), (16.35, 32.89, 7.22), (20.92, 38.24, 6.90), (22.6, 40.0, 6.90)]
tip_boxes = seg_boxes(tipV)
for t in (1.25, 2.5, 3.75, 5.0):
    all_hits += audit_boxes_moved(f'A{t}', tip_boxes, -DIR[0] * t, -DIR[1] * t, 0, fixed)
V = B.path_V(0.0)
drapeV = V[:13] + [(17.47, 33.89, 6.24), (20.47, 36.89, 5.99)]
drape_boxes = seg_boxes(drapeV)
all_hits += audit_boxes_moved('drape-static', drape_boxes, 0, 0, 0, fixed)
zifw = zifs['ZIF-wing-right']
for dx, dy, dz in [(0, 0, 2.5), (0, 0, 5.0), (-6, -8, 7.0),
                   (-12, -17, 9.0), (-19, -26, 12.0), (-26, -36, 16.0)]:
    hits = audit_boxes_moved(f'B{dx},{dy},{dz}', drape_boxes, dx, dy, dz, fixed)
    hz = V2.audit_boxes([Pos(dx, dy, dz) * zifw], fixed)
    print(f'B{dx},{dy},{dz} ZIF hits:', hz, flush=True)
    all_hits += hits + hz
print('TOTAL HITS:', all_hits if all_hits else 'NONE')
print('DONE')
