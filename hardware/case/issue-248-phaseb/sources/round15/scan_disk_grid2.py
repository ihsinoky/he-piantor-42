"""Finer disk-placement scan: sub-regions that showed pockets in
scan 1 (northern bay + southern band), Z 3.9..13.3 step 0.95,
R in {7.5, 9.2}, 24 angles, clearance >= 0.55 kept.
Writes RT15/disk_grid2.json incrementally, key 'cx,cy,Z,R'."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
from exact_oracle import OracleBody

RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
BOX_LO = np.array([-2., -30., 0.]); BOX_HI = np.array([50., 40., 26.])
BODS = []
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, k, s in raw:
        if n.startswith('Wire'): continue
        bb = s.bounding_box()
        lo = np.array([bb.min.X, bb.min.Y, bb.min.Z]); hi = np.array([bb.max.X, bb.max.Y, bb.max.Z])
        if np.any(hi < BOX_LO) or np.any(lo > BOX_HI): continue
        ob = OracleBody(n, s).restrict(BOX_LO - 3, BOX_HI + 3)
        if len(ob.faces): BODS.append(ob)
CENTRES = []
for cx in range(12, 33, 2):
    for cy in range(10, 23, 2): CENTRES.append((cx, cy))
for cx in range(8, 29, 2):
    for cy in range(-12, 3, 2): CENTRES.append((cx, cy))
ZS = [round(3.9 + 0.95 * j, 2) for j in range(11)]
out = {}
try: out = json.load(open(f'{RT15}/disk_grid2.json'))
except Exception: pass
t0 = time.time()
for R in (7.5, 9.2):
    for Z in ZS:
        done = [k for k in out if k.endswith(f',{Z},{R}')]
        if len(done) >= len(CENTRES): continue
        feas = 0
        for cx, cy in CENTRES:
            key = f'{cx},{cy},{Z},{R}'
            if key in out: continue
            th = np.linspace(0, 2 * np.pi, 24, endpoint=False)
            pts = np.stack([cx + R * np.cos(th), cy + R * np.sin(th), np.full(24, Z)], axis=1)
            worst = 9.0
            for p in pts:
                for ob in BODS:
                    dlb = np.maximum(np.maximum(ob.lo - p, p - ob.hi), 0.0)
                    if float(dlb @ dlb) > 16.0: continue
                    d = ob.dist(p)[0] - 0.5
                    if d < worst: worst = d
                if worst < 0.55: break
            if worst >= 0.55:
                out[key] = round(float(worst), 3); feas += 1
        json.dump(out, open(f'{RT15}/disk_grid2.json', 'w'))
        print(f'R {R} Z {Z}: feasible {feas} ({time.time()-t0:.0f}s)', flush=True)
print('saved', len(out), flush=True)
