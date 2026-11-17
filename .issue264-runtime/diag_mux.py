import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B
import fitlib18 as F
import repair18_lib as R
bodies, cable_r, cable_l, zifs = B.assemble()
for n, s in bodies:
    if 'U_MUX_C' in n and 'right' in n:
        bb = s.bounding_box()
        print(n, 'bbox', [round(v,2) for v in (bb.min.X,bb.min.Y,bb.min.Z,bb.max.X,bb.max.Y,bb.max.Z)])
        v = R.vol_pair(cable_r, s, F.bounds(cable_r), F.bounds(s), repair=True)
        print('vol', v)
        # locate: common bbox via section-free approach - intersect bounding boxes per cable sub-box not available;
        # print cable bbox
cb = cable_r.bounding_box()
print('cable bbox', [round(v,2) for v in (cb.min.X,cb.min.Y,cb.min.Z,cb.max.X,cb.max.Y,cb.max.Z)])
