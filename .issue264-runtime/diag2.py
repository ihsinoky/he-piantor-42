import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B
import fitlib18 as F
import repair18_lib as R
import numpy as np

bodies, cable_r, cable_l, zifs = B.assemble()
targets = {n: s for n, s in bodies if n in ('underside-right-U_MUX_C', 'Main-study-C23', 'underside-left-U_MUX_C')}
for n, s in targets.items():
    bb = s.bounding_box()
    print(n, 'bbox', [round(v, 2) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)], flush=True)
# per-segment test, right cable vs U_MUX_C right
V = B.path_V(0.0)
pts = B.catmull(V)
mux = targets['underside-right-U_MUX_C']
for i, (a, b) in enumerate(zip(pts[:-1], pts[1:])):
    s = B.seg_box(a, b, 9.6, 0.32)
    if s is None: continue
    bb = s.bounding_box(); b2 = mux.bounding_box()
    if (bb.max.X < b2.min.X - 1 or bb.min.X > b2.max.X + 1 or bb.max.Y < b2.min.Y - 1 or
        bb.min.Y > b2.max.Y + 1 or bb.max.Z < b2.min.Z - 1 or bb.min.Z > b2.max.Z + 1):
        continue
    v = R.vol_pair(s, mux, F.bounds(s), F.bounds(mux), repair=True)
    if v > F.HIT:
        print('segment', i, 'mid', [round(float(x), 1) for x in (np.array(a) + np.array(b)) / 2], 'vol', round(float(v), 4), flush=True)
print('DONE')
