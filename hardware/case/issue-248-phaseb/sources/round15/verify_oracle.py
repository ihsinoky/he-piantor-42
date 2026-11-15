"""Verify OracleBody against the face-pruned DistShapeShape reference
(exact_dist.Body) on random points per body, both pitches."""
import sys, json, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
from exact_oracle import OracleBody
from exact_dist import Body as RefBody

REGION_LO = np.array([-52., -28., -2.]); REGION_HI = np.array([52., 48., 26.])
rng = np.random.default_rng(20261115)
out = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    fixed = {n: s for n, k, s in raw if not n.startswith('Wire')}
    for name, shape in fixed.items():
        lo = np.array([shape.bounding_box().min.X, shape.bounding_box().min.Y, shape.bounding_box().min.Z])
        hi = np.array([shape.bounding_box().max.X, shape.bounding_box().max.Y, shape.bounding_box().max.Z])
        if np.any(hi < REGION_LO) or np.any(lo > REGION_HI): continue
        ob = OracleBody(name, shape)
        rb = RefBody(name, shape)
        pts = lo - 3 + rng.random((60, 3)) * (hi - lo + 6)
        worst = 0.0; worstp = None; nfb = 0
        for p in pts:
            d_o, q_o = ob.dist(p)
            d_r, q_r = rb._boundary_dist(p)
            dd = abs(abs(d_o) - d_r)
            if dd > worst: worst, worstp = dd, p
        out[f'{pitch}:{name}'] = dict(kinds=ob.kinds, max_absdiff_mm=round(float(worst), 5),
                                      worst_point=[round(float(v), 2) for v in worstp])
        print(pitch, name, ob.kinds, 'maxdiff', round(float(worst), 5), flush=True)
json.dump(out, open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15/oracle_verify.json', 'w'), indent=1)
bad = {k: v for k, v in out.items() if v['max_absdiff_mm'] > 0.02}
print('bodies checked', len(out), 'bodies with maxdiff>0.02:', len(bad), flush=True)
for k, v in bad.items(): print(' BAD', k, v, flush=True)
