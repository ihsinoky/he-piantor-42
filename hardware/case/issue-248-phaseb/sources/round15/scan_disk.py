"""Decisive scan: does ANY horizontal disk of R=9.2 (the radius the
+30.2 mm slack equation mandates for a 270 deg wrap) at a usable Z
(5.2/6.3 below the Wing slab 7.35-8.55; 9.6/10.7/11.8 above it) fit
the bay free volume? Centres X -14..30, Y -10..18 step 2, 32 angles,
both pitches. Reports the global best centreline clearance."""
import sys, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
from exact_oracle import OracleBody

BOX_LO = np.array([-44., -24., 2.]); BOX_HI = np.array([48., 46., 24.])
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
angs = np.linspace(0, 2 * np.pi, 32, endpoint=False)
best = (-9, None)
for Z in (5.2, 6.3, 9.6, 10.7, 11.8):
    for cx in np.arange(-14., 30.01, 2.0):
        for cy in np.arange(-10., 18.01, 2.0):
            worst = 9.0; arg = None
            pts = np.column_stack([cx + 9.2 * np.cos(angs), cy + 9.2 * np.sin(angs), np.full(32, Z)])
            for p in pts:
                dlb = np.maximum(np.maximum(LO - p, p - HI), 0.0)
                d2 = np.sum(dlb * dlb, axis=1)
                for k in np.where(d2 < 4.0)[0]:
                    d, q = OBS[k][2].dist(p)
                    if d < worst: worst = float(d); arg = (OBS[k][0], OBS[k][1], np.round(p, 1))
            if worst > best[0]: best = (worst, (cx, cy, Z, arg))
    print('Z', Z, 'global best so far', round(best[0], 3), best[1], flush=True)
print('FINAL BEST', round(best[0], 3), best[1], flush=True)
json.dump({'best_clearance': best[0], 'centre': [best[1][0], best[1][1]], 'Z': best[1][2],
           'binding': str(best[1][3])},
          open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15/disk_scan.json', 'w'), indent=1)
