"""Placement solver v2: 28 independent disk placements (14 per side)
from RT15/disk_grid.json. Right centres from the grid (Cx 10..30);
left centres are the grid mirrored (Cx -30..-10). Constraint over
all 28: |dZ| >= 1.05 or centre distance >= 19.4. Cost: fan travel
proxy (rise->entry + exit->P of that side) - 2*clearance.
Greedy, fewest-options first. Writes RT15/reel_place.json."""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
import design_r14 as dz
import design_r15 as dz15
import reel3

RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
D = json.load(open('/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/routes-round9.json'))
B, A = D['before'], D['after']
grid = json.load(open(f'{RT15}/disk_grid.json'))
candR = []
for k, v in grid.items():
    cx, cy, Z = k.split(',')
    if v >= 0.55: candR.append((float(cx), float(cy), float(Z), float(v)))
cand = {'right': candR, 'left': [(-cx, cy, Z, v) for cx, cy, Z, v in candR]}
print('feasible per side:', len(candR), flush=True)
U, W = reel3.U, reel3.W

def side_pts(side, i):
    sgn = 1 if side == 'right' else -1
    org = dz15.rise_top(i) * [sgn, 1, 1]
    P = dz.stations(B, A, i)[2] * [sgn, 1, 1]
    return org, P

def cost(side, i, c):
    cx, cy, Z, cl = c
    org, P = side_pts(side, i)
    E = np.array([cx + 9.2 * U[0], cy + 9.2 * U[1], Z])
    X = np.array([cx + 9.2 * W[0], cy + 9.2 * W[1], Z])
    if side == 'left':  # entry/exit mirror: U/W swap x sign
        E = np.array([cx - 9.2 * U[0], cy + 9.2 * U[1], Z])
        X = np.array([cx - 9.2 * W[0], cy + 9.2 * W[1], Z])
    return float(np.linalg.norm(E - org) + np.linalg.norm(P - X)) - 2.0 * cl

jobs = [(side, i) for side in ('right', 'left') for i in range(14)]
feas = {(s, i): sorted(cand[s], key=lambda c: cost(s, i, c)) for s, i in jobs}
order = sorted(jobs, key=lambda j: len(feas[j]))
chosen = {}; used = []
for side, i in order:
    for c in feas[(side, i)]:
        ok = True
        for (cx2, cy2, Z2) in used:
            if abs(c[2] - Z2) < 1.05 and np.hypot(c[0] - cx2, c[1] - cy2) < 19.4:
                ok = False; break
        if ok:
            chosen[(side, i)] = c; used.append((c[0], c[1], c[2])); break
    else:
        print('NO placement:', side, i + 1, flush=True)
out = {'right': {}, 'left': {}}
for (side, i), c in chosen.items():
    out[side][str(i)] = {'C': [c[0], c[1]], 'Z': c[2], 'clearance': c[3]}
    print(side, i + 1, 'C', (c[0], c[1]), 'Z', c[2], 'clr', c[3], 'cost', round(cost(side, i, c), 1), flush=True)
json.dump(out, open(f'{RT15}/reel_place.json', 'w'), indent=1)
print('placed', len(chosen), 'of 28', flush=True)
