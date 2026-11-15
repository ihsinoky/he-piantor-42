"""Placement solver for per-strand reel disks (R=9.2) from
RT15/disk_grid.json: choose one (centre, Z) per design strand such
that all chosen Z are >= 1.05 apart OR centres >= 19.4 apart (same-Z
plan separation), clearance >= 0.55, centre X >= 10 (mirror pair
separation), minimising total fan travel proxy (distance from the
strand's rise top to the entry point + exit point to P).
Greedy: strands with fewest feasible placements first.
Writes RT15/reel_place.json."""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
import design_r14 as dz
import design_r15 as dz15

RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
D = json.load(open('/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/routes-round9.json'))
B, A = D['before'], D['after']
grid = json.load(open(f'{RT15}/disk_grid.json'))
cand = []
for k, v in grid.items():
    cx, cy, Z = k.split(',')
    if v >= 0.55:
        cand.append((float(cx), float(cy), float(Z), float(v)))
print('feasible placements:', len(cand), flush=True)
U = np.array([np.cos(np.radians(-45.)), np.sin(np.radians(-45.))])
W = np.array([np.cos(np.radians(45.)), np.sin(np.radians(45.))])

def cost(i, c):
    cx, cy, Z, cl = c
    org = dz15.rise_top(i)
    P = dz.stations(B, A, i)[2]
    E = np.array([cx + 9.2 * U[0], cy + 9.2 * U[1], Z])
    X = np.array([cx + 9.2 * W[0], cy + 9.2 * W[1], Z])
    return float(np.linalg.norm(E - org) + np.linalg.norm(P - X)) - 2.0 * cl

feas = {i: sorted(cand, key=lambda c: cost(i, c)) for i in range(14)}
order = sorted(range(14), key=lambda i: len([c for c in feas[i] if c[3] >= 0.55]))
chosen = {}
used = []
for i in order:
    for c in feas[i]:
        ok = True
        for (cx2, cy2, Z2) in used:
            if abs(c[2] - Z2) < 1.05 and np.hypot(c[0] - cx2, c[1] - cy2) < 19.4:
                ok = False; break
        if ok:
            chosen[i] = c; used.append((c[0], c[1], c[2])); break
    else:
        print('strand', i + 1, 'NO placement', flush=True)
for i in range(14):
    if i in chosen:
        c = chosen[i]
        print('strand', i + 1, 'C', (c[0], c[1]), 'Z', c[2], 'clearance', c[3], 'cost', round(cost(i, c), 1), flush=True)
json.dump({str(i + 1): {'C': [chosen[i][0], chosen[i][1]], 'Z': chosen[i][2],
                        'clearance': chosen[i][3]} for i in chosen},
          open(f'{RT15}/reel_place.json', 'w'), indent=1)
print('placed', len(chosen), 'of 14', flush=True)
