"""Placement solver v3: backtracking assignment of 28 disks from
both placement scans (coarse grid1 R=9.2; fine grid2 R in {7.5,9.2}).
Conflict: |dZ| < 1.05 and centre distance < R1+R2+1.0.
Cost: fan travel proxy (side-aware) - 2*clearance. Writes
RT15/reel_place.json {side: {i: {C, Z, R, clearance}}}."""
import json, sys, time
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
candR = []
for k, v in json.load(open(f'{RT15}/disk_grid.json')).items():
    cx, cy, Z = k.split(',')
    if v >= 0.55: candR.append((float(cx), float(cy), float(Z), 9.2, float(v)))
try:
    for k, v in json.load(open(f'{RT15}/disk_grid2.json')).items():
        cx, cy, Z, R = k.split(',')
        candR.append((float(cx), float(cy), float(Z), float(R), float(v)))
except FileNotFoundError:
    pass
seen = set(); cand1 = []
for c in candR:
    key = (round(c[0]), round(c[1]), round(c[2], 2), c[3])
    if key not in seen: seen.add(key); cand1.append(c)
candR = cand1
cand = {'right': candR, 'left': [(-c[0], c[1], c[2], c[3], c[4]) for c in candR]}
print('candidates per side:', len(candR), flush=True)
U, W = reel3.U, reel3.W

def side_pts(side, i):
    sgn = 1 if side == 'right' else -1
    return dz15.rise_top(i) * [sgn, 1, 1], dz.stations(B, A, i)[2] * [sgn, 1, 1]

def cost(side, i, c):
    cx, cy, Z, R, cl = c
    org, P = side_pts(side, i)
    sgn = 1 if side == 'right' else -1
    E = np.array([cx + sgn * R * U[0], cy + R * U[1], Z])
    X = np.array([cx + sgn * R * W[0], cy + R * W[1], Z])
    return float(np.linalg.norm(E - org) + np.linalg.norm(P - X)) - 2.0 * cl

jobs = [(s, i) for s in ('right', 'left') for i in range(14)]
feas = {}
for j in jobs:
    lst = sorted(cand[j[0]], key=lambda c: cost(j[0], j[1], c))
    feas[j] = lst[:45] + lst[45:: max(1, len(lst) // 25)][:25]
print('candidates per job (capped):', {j: len(feas[j]) for j in jobs[:2]}, flush=True)

def conflict(c1, c2):
    return abs(c1[2] - c2[2]) < 1.05 and np.hypot(c1[0] - c2[0], c1[1] - c2[1]) < c1[3] + c2[3] + 1.0

placed = {}
nodes = [0]
t0 = time.time()
sys.setrecursionlimit(10000)
def dfs():
    nodes[0] += 1
    if nodes[0] > 3000000 or time.time() - t0 > 900: return False
    if len(placed) == len(jobs): return True
    best = None; bestopts = None
    for j in jobs:
        if j in placed: continue
        opts = [c for c in feas[j] if all(not conflict(c, pc) for pc in placed.values())]
        if bestopts is None or len(opts) < len(bestopts):
            best, bestopts = j, opts
            if len(opts) <= 1: break
    if not bestopts: return False
    for c in bestopts:
        placed[best] = c
        if dfs(): return True
        del placed[best]
    return False
ok = dfs()
print('dfs ok:', ok, 'nodes', nodes[0], f'{time.time()-t0:.0f}s', 'placed', len(placed), flush=True)
out = {'right': {}, 'left': {}}
for (side, i), c in placed.items():
    out[side][str(i)] = {'C': [c[0], c[1]], 'Z': c[2], 'R': c[3], 'clearance': c[4]}
    print(side, i + 1, 'C', (c[0], c[1]), 'Z', c[2], 'R', c[3], 'clr', c[4], 'cost', round(cost(side, i, c), 1), flush=True)
json.dump(out, open(f'{RT15}/reel_place.json', 'w'), indent=1)
