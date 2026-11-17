"""Issue 264 gate 3 v3: bodies from assemble_v5 (compound channel cuts),
fixed set per #261 audit_service_b (Wing-attached bodies excluded - they
move with the Wing), tip/drape as box Compounds (no fuse)."""
import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B
import build_audit264_v5 as V5
from build123d import Pos, Compound

bodies, cable_r, cable_l, zifs = V5.assemble_v5()
EXCL = ('shell', 'plateau', 'strip', 'plate-', 'plate_', 'plate-screw',
        'wing_right', 'underside-right', 'switch-envelope-R', 'POM-right')
fixed = [(n, s) for n, s in bodies if not any(k in n for k in EXCL)]
print('fixed bodies:', len(fixed), flush=True)
DIR = (0.68, 0.73)

def seg_compound(pts_list, w=9.6, t=0.32):
    pts = B.catmull(pts_list)
    return Compound(children=[s for a, b in zip(pts[:-1], pts[1:]) if (s := B.seg_box(a, b, w, t)) is not None])

def run(tag, solids):
    hits = []
    for sname, solid in solids:
        h, o = V5.audit_classified(solid, fixed)
        hits += [(tag, sname, n, v) for n, v in h + o]
    print(tag, 'hits:', hits, flush=True)
    return hits

all_hits = []
tipV = [(14.41, 30.60, 7.54), (16.35, 32.89, 7.22), (20.92, 38.24, 6.90), (22.6, 40.0, 6.90)]
tip = seg_compound(tipV)
for t in (1.25, 2.5, 3.75, 5.0):
    all_hits += run(f'A{t}', [('tip', Pos(-DIR[0] * t, -DIR[1] * t, 0) * tip)])
V = B.path_V(0.0)
drapeV = V[:13] + [(17.47, 33.89, 6.24), (20.47, 36.89, 5.99)]
drape = seg_compound(drapeV)
all_hits += run('drape-static', [('drape', drape)])
zifw = zifs['ZIF-wing-right']
for dx, dy, dz in [(0, 0, 2.5), (0, 0, 5.0), (-6, -8, 7.0),
                   (-12, -17, 9.0), (-19, -26, 12.0), (-26, -36, 16.0)]:
    ms = [('drape', Pos(dx, dy, dz) * drape), ('ZIF-wing-right', Pos(dx, dy, dz) * zifw)]
    all_hits += run(f'B{dx},{dy},{dz}', ms)
print('TOTAL HITS:', all_hits if all_hits else 'NONE')
print('DONE')
