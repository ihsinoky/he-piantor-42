"""Round 18 gate-3 (unplug-first) qualification on the stored build.
Part A: per-strand extraction feasibility under exact length
conservation (plug/dress translate -Y by s; host bulge flattens to
feed the span growth). Part B: shell removal sweep (+Z) vs stored
wires + switch envelopes. Part C: right-Wing lift-out (+Z) vs wires
at extraction state + trays + Main. 17mm (16mm is the mirror twin;
extraction arithmetic is pitch-independent)."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
import repair18_lib as R
from build123d import Location, Vector

RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime'
T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

stored = json.load(open(f'{RT}/round18/stored.json'))
M = stored['M']

def unit(v):
    v = np.array(v, float); return v / np.linalg.norm(v)

def perp_h(t, direction):
    n = np.array([t[1], -t[0], 0.]); n = n / np.linalg.norm(n)
    if direction == 'W' and n[0] > 0: n = -n
    if direction == 'E' and n[0] < 0: n = -n
    return n

def state_points(i, direction, dh, dc, s):
    pts = F.points_of(M, i, 'right')
    B0, B1, COR, RISE = [np.array(p, float) for p in pts[:4]]
    rest = pts[4:]
    B0 = B0 + np.array([0., -s, 0.]); B1 = B1 + np.array([0., -s, 0.])
    t_in = unit(COR - B1); t_out = unit(RISE - COR)
    if direction == 'U':
        n = np.array([0., 0., 1.]); n2 = n
    elif direction == 'TAUT':
        n = np.zeros(3); n2 = n
    else:
        n = perp_h(t_in, direction); n2 = perp_h(t_out, direction)
    if dh > 0.05:
        Pa = B1 + 0.25 * (COR - B1) + dh * n
        Pb = B1 + 0.75 * (COR - B1) + dh * n
        out = [B0, B1, Pa, Pb, COR]
    else:
        out = [B0, B1, COR]
    if dc > 0:
        out.append(COR + 0.5 * (RISE - COR) + dc * n2)
    out.append(RISE)
    out += [np.array(p, float) for p in rest]
    return [list(map(float, p)) for p in out]

def plen(i, dr, dh, dc, s):
    try:
        w, L = F.build_wire(state_points(i, dr, dh, dc, s))
    except Exception:
        return None
    return None if w is None else L

# ---------- Part A ----------
partA = {}
for k, rec in stored['strands'].items():
    i = int(k) - 1
    dr = rec['dir']; dh0, dc = rec['d']
    L_st = rec['len_right']
    L60 = plen(i, dr, 0.0, dc, 6.0)
    shortfall = None if L60 is None else round(max(0.0, L60 - L_st), 2)
    # s_max by bisection on feasibility L(s,0) <= L_st
    def feas(s):
        L = plen(i, dr, 0.0, dc, s)
        return L is not None and L <= L_st + 1e-9
    if feas(6.0):
        s_max = 6.0
    elif not feas(0.0):
        s_max = 0.0
    else:
        lo, hi = 0.0, 6.0
        for _ in range(6):
            mid = (lo + hi) / 2
            if feas(mid): lo = mid
            else: hi = mid
        s_max = round(lo, 2)
    partA[k] = {'dir': dr, 'delta': rec['delta_right'], 's_max': s_max,
                'shortfall_at_6mm': shortfall}
    log('A strand', k, dr, 'delta', rec['delta_right'], 's_max', s_max,
        'shortfall@6', shortfall)
json.dump(partA, open(f'{RT}/round18/gate3_partA.json', 'w'), indent=1)

# ---------- shared solids ----------
bodies17 = dict(F.bodies_of(17))
wires = {}
for k, rec in stored['strands'].items():
    i = int(k)
    for side in ('right', 'left'):
        r, why = R.build_s(rec[f'points_{side}'])
        assert r is not None
        wires[f'Wire-{side}-{i:02d}'] = r[0]
wb = {n: F.bounds(s) for n, s in wires.items()}

def hits_moved(moved, obstacles):
    cnt, det = 0, []
    for nm, ob in obstacles:
        if F._gap(F.bounds(moved), F.bounds(ob)) > 0: continue
        v = F.volume(moved, ob)
        if v > F.HIT: cnt += 1; det.append((nm, round(v, 3)))
    return cnt, det

# ---------- Part B: shell removal ----------
shells = {n: bodies17[n] for n in ('shell-central', 'strip-left', 'strip-right')}
obstB = [(n, s) for n, s in wires.items()] + \
        [(n, s) for n, s in bodies17.items() if n.startswith('switch-envelope')]
partB = {}
for z in (2, 5, 10, 25):
    tot, det = 0, []
    for nm, sh in shells.items():
        c, d = hits_moved(sh.moved(Location(Vector(0, 0, z))), obstB)
        tot += c; det += [(nm, x) for x in d]
    partB[str(z)] = {'hits': tot, 'detail': det[:10]}
    log('B z', z, 'hits', tot)
json.dump(partB, open(f'{RT}/round18/gate3_partB.json', 'w'), indent=1)

# ---------- Part C: lift-out (right) ----------
# extraction-state right wires
state_wires = {}
for k, rec in stored['strands'].items():
    i = int(k) - 1
    s_i = min(6.0, partA[k]['s_max'])
    dr = rec['dir']; dh0, dc = rec['d']
    L_st = rec['len_right']
    # solve dh at s_i for length conservation
    dh_i = 0.0
    if s_i > 0 and dh0 > 0:
        lo, hi = 0.0, dh0
        for _ in range(6):
            mid = (lo + hi) / 2
            L = plen(i, dr, mid, dc, s_i)
            if L is None: hi = mid; continue
            if L < L_st: lo = mid
            else: hi = mid
        dh_i = round((lo + hi) / 2, 2)
    r, why = R.build_s(state_points(i, dr, dh_i, dc, s_i))
    assert r is not None, (k, why)
    state_wires[f'Wire-right-{int(k):02d}'] = r[0]
    log('C strand', k, 's', s_i, 'dh', dh_i)

group_pref = ('wing_right', 'plate-right', 'switch-envelope-R',
              'underside-right', 'plate-screw-right', 'plate-washer-right')
group = {n: s for n, s in bodies17.items() if n.startswith(group_pref)}
obstC = [(n, s) for n, s in state_wires.items()] + \
        [(n, s) for n, s in wires.items() if n.startswith('Wire-left')] + \
        [(n, bodies17[n]) for n in ('tray-right', 'tray-left', 'main')]
partC = {}
for z in (5, 20):
    tot, det = 0, []
    for nm, g in group.items():
        c, d = hits_moved(g.moved(Location(Vector(0, 0, z))), obstC)
        tot += c; det += [(nm, x) for x in d]
    partC[str(z)] = {'hits': tot, 'detail': det[:12]}
    log('C z', z, 'hits', tot, det[:4])
json.dump(partC, open(f'{RT}/round18/gate3_partC.json', 'w'), indent=1)
log('gate3 done')
