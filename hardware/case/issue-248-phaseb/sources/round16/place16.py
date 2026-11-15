"""Round 16 CONTINUOUS slack placement (task 2, phase A).

Generalises round 15's quantised disk placement: per design strand
(14, right frame; left wires are X-mirrors per build_reel15's
convention) the storage ring is a full circle with CONTINUOUS
centre C=(cx,cy), height Z, radius R, entry angle a0 and CW sweep
theta. Placement checks the FULL circle (32 samples) against the
exact oracle (both pitches) and against all other rings (28 physical
rings = 14 right + 14 mirrors), so the phase-B theta re-solve for
the exact +30.20 slack accounting cannot leave checked territory.
Arc extra A = R*(theta - 2 sin(theta/2)) is targeted at 29.0 in
placement (fans + theta re-solve close the accounting in phase B).
State: RT16/place16.json (+ place16.npy). Usage:
  place16.py [chunks] [iters]  (warm-starts from place16.json)
"""
import json, os, sys, time
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
import design_r14 as dz
import design_r15 as dz15
from exact_oracle import OracleBody

HERE = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
RT16 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round16'
os.makedirs(RT16, exist_ok=True)
D = json.load(open(f'{HERE}/routes-round9.json')); B, A = D['before'], D['after']

BOX_LO = np.array([-50., -26., 2.]); BOX_HI = np.array([50., 30., 24.])
OBST = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, k, s in raw:
        if n.startswith('Wire'): continue
        lo = np.array([s.bounding_box().min.X, s.bounding_box().min.Y, s.bounding_box().min.Z])
        hi = np.array([s.bounding_box().max.X, s.bounding_box().max.Y, s.bounding_box().max.Z])
        if np.any(hi < BOX_LO) or np.any(lo > BOX_HI): continue
        ob = OracleBody(n, s).restrict(BOX_LO - 3, BOX_HI + 3)
        if len(ob.faces): OBST[(pitch, n)] = ob
print('obstacle bodies:', len(OBST), flush=True)

# fixed route samples (feed optimiser's FIX sets; right + mirrored left)
def fixed_samples(i):
    pts = []
    ep, G, P = dz.stations(B, A, i)
    chains = [[np.array(B[i][0], float), np.array(B[i][1], float), dz15.corridor(i), dz15.rise_top(i)],
              [P, G, ep]]
    for ch in chains:
        for a, b in zip(ch, ch[1:]):
            for tt in np.linspace(0, 1, 9)[:-1]: pts.append(a + (b - a) * tt)
        pts.append(ch[-1])
    return np.array(pts)
FIXR = np.vstack([fixed_samples(i) for i in range(14)])
FIXL = FIXR * np.array([-1., 1., 1.])
FIXALL = np.vstack([FIXR, FIXL])

NS = 32           # full-circle samples per ring
NV = 6            # cx, cy, Z, R, a0, th  per design strand
HB2, WB2 = 1.05, 60.0     # body hinge / weight
HR2, WR2 = 1.10, 60.0     # ring-ring + ring-fixed hinge / weight
WSLK = 2.0
TARGET_A = 29.0

def ring_pts(v, mirror=False):
    """v: 6 vars of one design strand. Returns (NS,3) pts, (NS,3,6) J
    in the strand's own frame; mirror flips X (left physical wire)."""
    cx, cy, Z, R, a0, th = v
    fr = np.arange(NS) / NS
    ang = a0 - th * fr                      # CW full circle when th=2pi
    ca, sa = np.cos(ang), np.sin(ang)
    pts = np.stack([cx + R * ca, cy + R * sa, np.full(NS, Z)], axis=1)
    J = np.zeros((NS, 3, NV))
    J[:, 0, 0] = 1.0; J[:, 1, 1] = 1.0; J[:, 2, 2] = 1.0
    J[:, 0, 3] = ca; J[:, 1, 3] = sa
    J[:, 0, 4] = -R * sa; J[:, 1, 4] = R * ca
    J[:, 0, 5] = -R * sa * (-fr); J[:, 1, 5] = R * ca * (-fr)
    if mirror:
        pts = pts * np.array([-1., 1., 1.]); J[:, 0, :] *= -1.0
    return pts, J

def all_samples(x):
    """28 physical rings: owners (side, design_i); side 0=right uses
    vars of strand i, side 1=left is the mirror of strand i."""
    P, J, O = [], [], []
    for side in (0, 1):
        for i in range(14):
            v = x[i * NV:(i + 1) * NV]
            p, j = ring_pts(v, mirror=(side == 1))
            P.append(p); J.append(j); O += [(side, i)] * NS
    return np.vstack(P), J, O

CAND = {}
def build_cand(x):
    P, _, O = all_samples(x)
    for s in range(28):
        cand = []
        pts = P[s * NS:(s + 1) * NS]
        for key, ob in OBST.items():
            dlb = np.maximum(np.maximum(ob.lo - pts, pts - ob.hi), 0.0)
            if float(np.min(np.sum(dlb * dlb, axis=1))) < 3.0 ** 2: cand.append(key)
        CAND[s] = cand

def objective(x):
    loss = 0.0; grad = np.zeros(14 * NV)
    P, J, O = all_samples(x)
    # body term
    for s in range(28):
        i = O[s * NS][1]
        for k in range(NS):
            p = P[s * NS + k]
            for key in CAND.get(s, []):
                ob = OBST[key]
                dlb = np.maximum(np.maximum(ob.lo - p, p - ob.hi), 0.0)
                if float(dlb @ dlb) > (HB2 + 0.6) ** 2: continue
                d, q = ob.dist_capped(p, HB2)
                if d < HB2 and q is not None:
                    loss += WB2 * ((HB2 - d) / 0.3) ** 2
                    nrm = float(np.linalg.norm(p - q))
                    if nrm > 1e-9:
                        dirv = (p - q) / nrm if d >= 0 else (q - p) / nrm
                        gv = -2 * WB2 * (HB2 - d) / 0.09 * dirv
                        grad[i * NV:(i + 1) * NV] += J[s][k].T @ gv
    # ring-ring + ring-fixed term (sample pairs)
    comb = np.vstack([P, FIXALL])
    own = np.array([o[0] * 100 + o[1] for o in O] + [-1] * len(FIXALL))
    tree = cKDTree(comb)
    for a, b in tree.query_pairs(HR2):
        if own[a] == own[b] and own[a] >= 0: continue
        if a >= len(P) and b >= len(P): continue
        dvec = comb[a] - comb[b]; d = float(np.linalg.norm(dvec))
        if d < 1e-9: continue
        loss += WR2 * ((HR2 - d) / 0.3) ** 2
        gv = -2 * WR2 * (HR2 - d) / 0.09 * (dvec / d)
        for idx, sgn in ((a, 1.0), (b, -1.0)):
            if idx < len(P):
                side, i = O[idx]
                grad[i * NV:(i + 1) * NV] += sgn * (J[idx // NS][idx % NS].T @ gv)
    # slack target per design strand
    for i in range(14):
        cx, cy, Z, R, a0, th = x[i * NV:(i + 1) * NV]
        Aex = R * (th - 2 * np.sin(th / 2))
        loss += WSLK * ((Aex - TARGET_A) / 1.5) ** 2
        dA = np.array([0, 0, 0, (th - 2 * np.sin(th / 2)),
                       0, R * (1 - np.cos(th / 2))])
        grad[i * NV:(i + 1) * NV] += 2 * WSLK * (Aex - TARGET_A) / 2.25 * dA
    loss += 0.002 * float(np.sum((x - X0) ** 2)); grad += 0.004 * (x - X0)
    return loss, grad

def solve_theta(R, target):
    lo, hi = 3.6, 6.24
    f = lambda t: R * (t - 2 * np.sin(t / 2))
    if f(hi) < target: return hi
    for _ in range(40):
        mid = (lo + hi) / 2
        if f(mid) < target: lo = mid
        else: hi = mid
    return (lo + hi) / 2

def init_state():
    """Greedy init from round-15 feasible grid entries (full-circle
    clearance >= 0.55), theta solved for arc extra TARGET_A."""
    grid = {}
    for fn in ('disk_grid.json', 'disk_grid2.json'):
        try: grid.update(json.load(open(f'{RT15}/{fn}')))
        except Exception: pass
    feas = []
    for k, v in grid.items():
        q = [float(t) for t in k.split(',')]
        if len(q) == 3: q.append(9.2)   # disk_grid.json: R fixed at 9.2 in the round-15 coarse scan
        cx, cy, Z, R = q
        feas.append((cx, cy, Z, R))
    rng = np.random.default_rng(7)
    order = list(range(14)); rng.shuffle(order)
    x = np.zeros(14 * NV); used = []
    for i in order:
        best = None
        for (cx, cy, Z, R) in feas:
            conf = 0
            for (ux, uy, uZ, uR) in used:
                dz_ = abs(Z - uZ)
                if dz_ < 1.10:
                    d = np.hypot(cx - ux, cy - uy)
                    pd = d - R - uR if d > R + uR else (abs(R - uR) - d if d < abs(R - uR) else 0.0)
                    if pd < 1.10: conf += (1.10 - pd) ** 2 + (1.10 - dz_) * 0.1
            score = conf * 100 + 0.01 * np.hypot(cx - 20, cy - 5)
            if best is None or score < best[0]: best = (score, cx, cy, Z, R)
        _, cx, cy, Z, R = best
        used.append((cx, cy, Z, R))
        th = solve_theta(R, TARGET_A)
        x[i * NV:(i + 1) * NV] = [cx, cy, Z, R, np.radians(-45.0), th]
    return x

X0 = init_state()
if os.path.exists(f'{RT16}/place16.json'):
    _W = json.load(open(f'{RT16}/place16.json'))
    for i in range(14):
        X0[i * NV:(i + 1) * NV] = _W[str(i + 1)]
    print('warm start from place16.json', flush=True)
build_cand(X0)

def save(x, tag=''):
    M = {str(i + 1): [round(float(v), 4) for v in x[i * NV:(i + 1) * NV]] for i in range(14)}
    json.dump(M, open(f'{RT16}/place16.json', 'w'), indent=1)
    np.save(f'{RT16}/place16.npy', x)
    if tag: json.dump(M, open(f'{RT16}/place16_{tag}.json', 'w'), indent=1)

def report(x, label):
    P, _, O = all_samples(x)
    worst_b = (9, None)
    for s in range(28):
        for k in range(NS):
            p = P[s * NS + k]
            for key in CAND.get(s, []):
                d, q = OBST[key].dist(p)
                if d < worst_b[0]: worst_b = (d, (O[s * NS], np.round(p, 1), key[1]))
    comb = np.vstack([P, FIXALL]); own = np.array([o[0] * 100 + o[1] for o in O] + [-1] * len(FIXALL))
    tree = cKDTree(comb); worst_r = (9, None)
    for a, b in tree.query_pairs(2.0):
        if own[a] == own[b] and own[a] >= 0: continue
        if a >= len(P) and b >= len(P): continue
        d = float(np.linalg.norm(comb[a] - comb[b]))
        if d < worst_r[0]: worst_r = (d, (O[a] if a < len(P) else 'FIX', O[b] if b < len(P) else 'FIX'))
    print(label, 'min body', round(float(worst_b[0]), 3), worst_b[1],
          '| min ring pair', round(float(worst_r[0]), 3), worst_r[1], flush=True)
    return worst_b, worst_r

if __name__ == '__main__':
    chunks = int(sys.argv[1]) if len(sys.argv) > 1 else 4
    iters = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    rng = np.random.default_rng(16)
    f0, g0 = objective(X0)
    idxs = rng.choice(14 * NV, 10, replace=False); errs = []
    for k in idxs:
        xp = X0.copy(); xp[k] += 1e-6
        fp, _ = objective(xp)
        errs.append(abs((fp - f0) / 1e-6 - g0[k]))
    print('init loss', round(float(f0), 1), 'grad err', round(float(max(errs)), 3), flush=True)
    report(X0, 'init')
    BND = []
    for i in range(14):
        BND += [(0., 42.), (-20., 28.), (3.4, 12.8), (5.0, 9.6), (-np.pi, np.pi), (3.6, 6.24)]
    x = X0.copy()
    logf = open(f'{RT16}/place_log.jsonl', 'a')
    for chunk in range(chunks):
        t = time.time()
        r = minimize(objective, x, jac=True, method='L-BFGS-B', bounds=BND,
                     options={'maxiter': iters, 'ftol': 1e-11, 'maxls': 25})
        x = r.x
        build_cand(x)
        wb, wr = report(x, f'  chunk {chunk}')
        save(x, f'c{chunk}')
        rec = dict(chunk=chunk, loss=round(float(r.fun), 1), nit=int(r.nit),
                   msg=str(r.message)[:40], min_body=round(float(wb[0]), 3),
                   min_ring=round(float(wr[0]), 3), secs=round(time.time() - t))
        logf.write(json.dumps(rec) + '\n'); logf.flush()
        print('  rec', rec, flush=True)
        if r.nit == 0 or 'ABNORMAL' in str(r.message):
            x = x + rng.normal(0, 0.02, size=14 * NV)
            print('  jitter applied', flush=True)
    print('done', flush=True)
