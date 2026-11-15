"""Placement solver v4: min-conflicts local search over both scans.
State: one candidate per (side, strand) from the full candidate
lists (no cost cap). Move: pick a conflicted job, assign the
candidate minimising (conflicts, cost) with random tie-breaks;
random restarts. Success = 0 conflicts over all 28.
Writes RT15/reel_place.json on success."""
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
for k, v in json.load(open(f'{RT15}/disk_grid2.json')).items():
    cx, cy, Z, R = k.split(',')
    candR.append((float(cx), float(cy), float(Z), float(R), float(v)))
seen = set(); tmp = []
for c in candR:
    key = (round(c[0]), round(c[1]), round(c[2], 2), c[3])
    if key not in seen: seen.add(key); tmp.append(c)
candR = tmp
CAND = {'right': np.array(candR), 'left': np.array([(-c[0], c[1], c[2], c[3], c[4]) for c in candR])}
U, W = reel3.U, reel3.W
def cost(side, i, c):
    sgn = 1 if side == 'right' else -1
    org = dz15.rise_top(i) * [sgn, 1, 1]
    P = dz.stations(B, A, i)[2] * [sgn, 1, 1]
    E = np.array([c[0] + sgn * c[3] * U[0], c[1] + c[3] * U[1], c[2]])
    X = np.array([c[0] + sgn * c[3] * W[0], c[1] + c[3] * W[1], c[2]])
    return float(np.linalg.norm(E - org) + np.linalg.norm(P - X)) - 2.0 * c[4]
JOBS = [(s, i) for s in ('right', 'left') for i in range(14)]
COST = {}
for j in JOBS:
    COST[j] = np.array([cost(j[0], j[1], c) for c in CAND[j[0]]])
    CAND[j[0]] = CAND[j[0]]  # shared per side
def conflicts_for(j, cidx, assign):
    c = CAND[j[0]][cidx]; n = 0
    for j2, c2idx in assign.items():
        if j2 == j: continue
        c2 = CAND[j2[0]][c2idx]
        if abs(c[2] - c2[2]) < 1.05 and np.hypot(c[0] - c2[0], c[1] - c2[1]) < c[3] + c2[3] + 1.0: n += 1
    return n
rng = np.random.default_rng(20261115)
t0 = time.time(); best = (99, None)
for restart in range(200):
    assign = {j: int(np.argmin(COST[j] + rng.normal(0, 3, len(COST[j])))) for j in JOBS}
    for step in range(400):
        bad = [j for j in JOBS if conflicts_for(j, assign[j], assign) > 0]
        if not bad:
            print('SOLVED restart', restart, 'step', step, f'{time.time()-t0:.0f}s', flush=True)
            out = {'right': {}, 'left': {}}
            for (side, i), ci in assign.items():
                c = CAND[side][ci]
                out[side][str(i)] = {'C': [float(c[0]), float(c[1])], 'Z': float(c[2]),
                                     'R': float(c[3]), 'clearance': float(c[4])}
                print(side, i + 1, 'C', (c[0], c[1]), 'Z', c[2], 'R', c[3], 'clr', c[4], flush=True)
            json.dump(out, open(f'{RT15}/reel_place.json', 'w'), indent=1)
            sys.exit(0)
        tot = sum(conflicts_for(j, assign[j], assign) for j in bad)
        if tot < best[0]: best = (tot, dict(assign))
        j = bad[rng.integers(len(bad))]
        arr = CAND[j[0]]
        dz_ = np.abs(arr[:, 2] - 0)  # placeholder
        scores = []
        others = [(CAND[j2[0]][ci]) for j2, ci in assign.items() if j2 != j]
        oc = np.array([[o[0], o[1], o[2], o[3]] for o in others])
        dzv = np.abs(arr[:, 2][:, None] - oc[:, 2][None, :]) < 1.05
        dist = np.hypot(arr[:, 0][:, None] - oc[:, 0][None, :], arr[:, 1][:, None] - oc[:, 1][None, :])
        conf = ((dzv) & (dist < (arr[:, 3][:, None] + oc[:, 3][None, :] + 1.0))).sum(axis=1)
        score = conf * 1000.0 + COST[j] + rng.normal(0, 0.5, len(arr))
        assign[j] = int(np.argmin(score))
    print('restart', restart, 'best total conflicts', best[0], f'{time.time()-t0:.0f}s', flush=True)
    if time.time() - t0 > 1500: break
print('NOT solved; best total conflict count', best[0], flush=True)
