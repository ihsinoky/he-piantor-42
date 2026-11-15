"""Round 15 feed re-optimisation with EXACT body penalties.

Skeleton as round 14 (ORG -> M1 -> M2 -> TGT per strand, right side;
left mirrors). The fixed-body term uses exact signed BRep distances
(exact_oracle, verified vs DistShapeShape) against fixed solids of
BOTH pitch assemblies, with analytic gradients from closest-point
witnesses. Wire-wire hinge, slope ceiling, approach-angle and segment
length terms with analytic gradients throughout.
Usage: opt_feed_exact.py [rounds]
Writes RT15/feed_exact.json (+ per-round logs to stdout).
"""
import json, sys, time
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
RT14 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round14'
RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
D = json.load(open(f'{HERE}/routes-round9.json')); B, A = D['before'], D['after']
TAUT14 = json.load(open(f'{RT14}/taut_opt.json'))

ROUTE_BOX_LO = np.array([-6., -22., 2.]); ROUTE_BOX_HI = np.array([48., 46., 24.])
OBST = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, k, s in raw:
        if n.startswith('Wire'): continue
        lo = np.array([s.bounding_box().min.X, s.bounding_box().min.Y, s.bounding_box().min.Z])
        hi = np.array([s.bounding_box().max.X, s.bounding_box().max.Y, s.bounding_box().max.Z])
        if np.any(hi < ROUTE_BOX_LO) or np.any(lo > ROUTE_BOX_HI): continue
        if hi[0] < -2: continue            # left-side bodies excluded
        ob = OracleBody(n, s).restrict(ROUTE_BOX_LO - 3, ROUTE_BOX_HI + 3)
        if len(ob.faces): OBST[(pitch, n)] = ob
print('obstacle bodies:', len(OBST), flush=True)

ORG = {i: dz15.rise_top(i) for i in range(14)}
TGT = {i: dz.stations(B, A, i)[2] for i in range(14)}
AXV = np.array([0.8660254, -0.5, 0.0])
NSEG = 6
X0 = np.zeros(84)
for j in range(14):
    X0[j * 6:j * 6 + 3] = TAUT14[str(j + 1)]['M1']; X0[j * 6 + 3:j * 6 + 6] = TAUT14[str(j + 1)]['M2']
# Geometric warm init (round 15 run 2): M2 on the -a approach ray at
# P's height (the proven tail slot Z ~11), M1 mid-way at clamped Z.
# Round 14's body-blind M points sit in the plate band (Z ~12.7) and
# trap the optimiser in a stiff coupled valley.
AXU = np.array([0.8660254, -0.5, 0.0])
for j in range(14):
    ep, G, P = dz.stations(B, A, j)
    M2 = P - 5.5 * AXU
    M1 = ORG[j] + 0.45 * (P - ORG[j]); M1[2] = min(M1[2], 11.2)
    X0[j * 6:j * 6 + 3] = M1; X0[j * 6 + 3:j * 6 + 6] = M2
import os
if os.path.exists(f'{RT15}/feed_exact.json'):
    _WARM = json.load(open(f'{RT15}/feed_exact.json'))
    for j in range(14):
        X0[j * 6:j * 6 + 3] = _WARM[str(j + 1)]['M1']; X0[j * 6 + 3:j * 6 + 6] = _WARM[str(j + 1)]['M2']
    print('warm start from feed_exact.json', flush=True)


def fixed_samples(i):
    pts = []
    ep, G, P = dz.stations(B, A, i)
    chains = [[np.array(B[i][0], float), np.array(B[i][1], float), dz15.corridor(i), ORG[i]],
              [P, G, ep]]
    for ch in chains:
        for a, b in zip(ch, ch[1:]):
            for tt in np.linspace(0, 1, 9)[:-1]: pts.append(a + (b - a) * tt)
        pts.append(ch[-1])
    return np.array(pts)
FIX = {i: fixed_samples(i) for i in range(14)}
FIXALL = np.vstack([FIX[i] for i in range(14)])
FIXOWN = np.concatenate([[i] * len(FIX[i]) for i in range(14)])

def var_samples(x, i):
    m1 = x[i * 6:i * 6 + 3]; m2 = x[i * 6 + 3:i * 6 + 6]
    chain = [ORG[i], m1, m2, TGT[i]]
    pts = []; Js = []
    for s in range(3):
        a, b = chain[s], chain[s + 1]
        ns = max(NSEG, int(np.ceil(float(np.linalg.norm(b - a)) / 1.5)))
        for k in range(ns):
            t = k / ns
            pts.append(a + (b - a) * t)
            J = np.zeros((3, 6))
            if s == 0: J[:, 0:3] = t * np.eye(3)
            elif s == 1: J[:, 0:3] = (1 - t) * np.eye(3); J[:, 3:6] = t * np.eye(3)
            else: J[:, 3:6] = (1 - t) * np.eye(3)
            Js.append(J)
    pts.append(TGT[i].copy()); Js.append(np.zeros((3, 6)))
    return np.array(pts), Js

def _trim15(p_prev, p, p_next):
    u = p_prev - p; v = p_next - p
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-12 or nv < 1e-12: return 50.0
    th = np.arccos(np.clip(float(u @ v) / (nu * nv), -1, 1))
    th = min(max(th, 1e-4), np.pi - 1e-4)
    d = 5.0 / np.tan(th / 2)
    return float(min(d, 50.0)) if np.isfinite(d) else 50.0

def feed_build_pen(i, v):
    """R5 trim-margin penalty on the feed chain (buffer 0.3 mm);
    keeps the fitted fillets from cutting across neighbours."""
    m1 = v[0:3]; m2 = v[3:6]
    ep, G, P = dz.stations(B, A, i)
    ch = [dz15.corridor(i), ORG[i], m1, m2, P, G]
    tr = [0.0] + [_trim15(ch[k - 1], ch[k], ch[k + 1]) for k in range(1, len(ch) - 1)] + [0.0]
    pen = 0.0
    for k in range(len(ch) - 1):
        seg = float(np.linalg.norm(ch[k + 1] - ch[k]))
        margin = seg - tr[k] - tr[k + 1]
        if margin < 0.3: pen += 50.0 * (0.3 - margin) ** 2
    return pen

CAND = {}
for i in range(14):
    pts, _ = var_samples(X0, i)
    cand = []
    for key, ob in OBST.items():
        dlb = np.maximum(np.maximum(ob.lo - pts, pts - ob.hi), 0.0)
        if float(np.min(np.sum(dlb * dlb, axis=1))) < 3.5 ** 2: cand.append(key)
    CAND[i] = cand
print('cand per strand:', [len(CAND[i]) for i in range(14)], flush=True)

HB, WB = 1.15, 30.0
HW, WW = 1.35, 3.0
WC = 2.0

def ceiling(y):
    if y < 1.935593: return 21.65, 0.0
    t = min(max((y - 1.935593) / 36.578838, 0), 1)
    return 21.65 - 11.10 * t, (-11.10 / 36.578838 if t < 1 else 0.0)

def objective(x):
    loss = 0.0; grad = np.zeros(84)
    allp = []; allo = []; allJ = []
    for i in range(14):
        sp, Js = var_samples(x, i); allp.append(sp); allJ += Js; allo += [i] * len(sp)
    allp = np.vstack(allp); allo = np.array(allo)
    # wire-wire
    comb = np.vstack([allp, FIXALL]); own = np.concatenate([allo, FIXOWN])
    tree = cKDTree(comb)
    for a, b in tree.query_pairs(HW):
        if own[a] == own[b] or (a >= len(allp) and b >= len(allp)): continue
        dvec = comb[a] - comb[b]; d = float(np.linalg.norm(dvec))
        if d < 1e-9: continue
        loss += WW * ((HW - d) / 0.3) ** 2
        gv = -2 * WW * (HW - d) / 0.09 * (dvec / d)
        for idx, sgn in ((a, 1.0), (b, -1.0)):
            if idx < len(allp):
                i = allo[idx]
                grad[i * 6:i * 6 + 6] += sgn * (allJ[idx].T @ gv)
    # body + ceiling per strand
    for i in range(14):
        sp, Js = var_samples(x, i)
        for k, p in enumerate(sp):
            for key in CAND[i]:
                ob = OBST[key]
                dlb = np.maximum(np.maximum(ob.lo - p, p - ob.hi), 0.0)
                if float(dlb @ dlb) > (HB + 0.6) ** 2: continue
                d, q = ob.dist_capped(p, HB)
                if d < HB and q is not None:
                    loss += WB * ((HB - d) / 0.3) ** 2
                    nrm = float(np.linalg.norm(p - q))
                    if nrm > 1e-9:
                        dirv = (p - q) / nrm if d >= 0 else (q - p) / nrm
                        gv = -2 * WB * (HB - d) / 0.09 * dirv
                        grad[i * 6:i * 6 + 6] += Js[k].T @ gv
            c, dc = ceiling(p[1])
            if p[2] > c:
                u = p[2] - c
                loss += WC * (u / 0.3) ** 2
                gv = 2 * WC * u / 0.09 * np.array([0.0, -dc, 1.0])
                grad[i * 6:i * 6 + 6] += Js[k].T @ gv
    # approach angle + segment lengths + regularisation
    for i in range(14):
        m1 = x[i * 6:i * 6 + 3]; m2 = x[i * 6 + 3:i * 6 + 6]
        u = TGT[i] - m2; L = float(np.linalg.norm(u)); k = -AXV
        c = float(u @ k) / L
        if c < 0.3:
            loss += 6.0 * ((0.3 - c) / 0.2) ** 2
            dcdu = k / L - (u @ k) * u / L ** 3
            grad[i * 6 + 3:i * 6 + 6] += (-2 * 6.0 * (0.3 - c) / 0.04) * (-dcdu)
        chain = [ORG[i], m1, m2, TGT[i]]
        for s in range(3):
            a, b = chain[s], chain[s + 1]; ab = b - a; L = float(np.linalg.norm(ab))
            if 1e-9 < L < 7.0:
                loss += 10.0 * ((7.0 - L) / 1.5) ** 2
                gv = -2 * 10.0 * (7.0 - L) / 2.25 * (ab / L)  # dpen/d(end)
                if s == 0: grad[i * 6:i * 6 + 3] += gv
                elif s == 1: grad[i * 6:i * 6 + 3] += -gv; grad[i * 6 + 3:i * 6 + 6] += gv
                else: grad[i * 6 + 3:i * 6 + 6] += -gv
    for i in range(14):
        v = x[i * 6:(i + 1) * 6]
        pen0 = feed_build_pen(i, v)
        loss += pen0
        eps = 1e-6
        for k in range(6):
            vp = v.copy(); vp[k] += eps
            grad[i * 6 + k] += (feed_build_pen(i, vp) - pen0) / eps
    loss += 0.001 * float(np.sum((x - X0) ** 2)); grad += 0.002 * (x - X0)
    return loss, grad

def report(x, label):
    worst_b = (9, None); worst_w = (9, None)
    for i in range(14):
        sp, _ = var_samples(x, i)
        for p in sp:
            for key in CAND[i]:
                d, q = OBST[key].dist(p)
                if d < worst_b[0]: worst_b = (d, (i + 1, key, np.round(p, 1)))
    allp = []; allo = []
    for i in range(14):
        sp, _ = var_samples(x, i); allp.append(sp); allo += [i] * len(sp)
    allp = np.vstack(allp); allo = np.array(allo)
    comb = np.vstack([allp, FIXALL]); own = np.concatenate([allo, FIXOWN])
    tree = cKDTree(comb)
    for a, b in tree.query_pairs(2.2):
        if own[a] == own[b] or (a >= len(allp) and b >= len(allp)): continue
        d = float(np.linalg.norm(comb[a] - comb[b]))
        if d < worst_w[0]: worst_w = (d, (int(own[a]) + 1, int(own[b]) + 1, np.round(comb[a], 1)))
    print(label, 'min body dist', round(float(worst_b[0]), 3), worst_b[1],
          '| min WW pair', round(float(worst_w[0]), 3), worst_w[1], flush=True)
    return worst_b, worst_w

if __name__ == '__main__':
    # gradient self-test on 12 random vars
    rng = np.random.default_rng(3)
    f0, g0 = objective(X0)
    idxs = rng.choice(84, 12, replace=False)
    errs = []
    for k in idxs:
        xp = X0.copy(); xp[k] += 1e-6
        fp, _ = objective(xp)
        errs.append(abs((fp - f0) / 1e-6 - g0[k]))
    print('init loss', round(float(f0), 2), 'grad check max err', round(float(max(errs)), 3), flush=True)
    report(X0, 'init')
    BND = []
    for i in range(14): BND += [(0, 46), (-10, 44), (5.6, 21.8)] * 2
    x = X0.copy()
    for rnd in range(int(sys.argv[1]) if len(sys.argv) > 1 else 2):
        t = time.time(); nit = 0
        for chunk in range(4):
            r = minimize(objective, x, jac=True, method='L-BFGS-B', bounds=BND,
                         options={'maxiter': 40, 'ftol': 1e-11, 'maxls': 25})
            x = r.x; nit += r.nit
            print(f'  chunk {chunk}: loss {r.fun:.1f} nit {r.nit} msg {r.message}', flush=True)
            report(x, f'  chunk {chunk}')
            json.dump({str(i + 1): {'M1': [round(float(v), 3) for v in x[i * 6:i * 6 + 3]],
                                    'M2': [round(float(v), 3) for v in x[i * 6 + 3:i * 6 + 6]]} for i in range(14)},
                      open(f'{RT15}/feed_exact.json', 'w'), indent=1)
        print(f'round {rnd}: loss {r.fun:.3f} nit {nit} time {time.time()-t:.0f}s', flush=True)
    json.dump({str(i + 1): {'M1': [round(float(v), 3) for v in x[i * 6:i * 6 + 3]],
                            'M2': [round(float(v), 3) for v in x[i * 6 + 3:i * 6 + 6]]} for i in range(14)},
              open(f'{RT15}/feed_exact.json', 'w'), indent=1)
    print('saved feed_exact.json', flush=True)
