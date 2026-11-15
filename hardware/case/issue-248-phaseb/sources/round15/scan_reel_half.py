"""Half-ladder reel centre scan: 7 Z levels (4.6 + 1.12i, i=0..6),
R in {7.0, 9.2}, 24 angles; worst exact body distance per centre."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
from exact_oracle import OracleBody

BOX_LO = np.array([-30., -24., 2.]); BOX_HI = np.array([48., 46., 24.])
OBS = []
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, k, s in raw:
        if n.startswith('Wire'): continue
        lo = np.array([s.bounding_box().min.X, s.bounding_box().min.Y, s.bounding_box().min.Z])
        hi = np.array([s.bounding_box().max.X, s.bounding_box().max.Y, s.bounding_box().max.Z])
        if np.any(hi < BOX_LO) or np.any(lo > BOX_HI): continue
        ob = OracleBody(n, s).restrict(BOX_LO - 3, BOX_HI + 3)
        if len(ob.faces): OBS.append((pitch, n, ob))
print('bodies:', len(OBS), flush=True)
LO = np.array([ob.lo for _, _, ob in OBS]); HI = np.array([ob.hi for _, _, ob in OBS])

def worst_for(C):
    worst = 9.0; arg = None
    angs = np.linspace(0, 2 * np.pi, 24, endpoint=False)
    for i in range(7):
        z = 4.6 + 1.12 * i
        for R in (7.0, 9.2):
            pts = np.column_stack([C[0] + R * np.cos(angs), C[1] + R * np.sin(angs),
                                   np.full(len(angs), z)])
            for p in pts:
                dlb = np.maximum(np.maximum(LO - p, p - HI), 0.0)
                d2 = np.sum(dlb * dlb, axis=1)
                for k in np.where(d2 < 4.0)[0]:
                    d, q = OBS[k][2].dist(p)
                    if d < worst: worst = float(d); arg = (i + 1, R, np.round(p, 1), OBS[k][0], OBS[k][1])
    return worst, arg

res = {}
for cx in (8.0, 12.0, 16.0, 20.0, 24.0):
    for cy in (-2.0, 2.0, 6.0, 10.0, 14.0):
        w, arg = worst_for((cx, cy))
        res[(cx, cy)] = (round(w, 3), str(arg))
        print('C', (cx, cy), 'worst', round(w, 3), arg, flush=True)
print('TOP:', sorted(res.items(), key=lambda kv: -kv[1][0])[:6], flush=True)
