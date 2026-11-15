"""Round 15 reel fan optimisation with EXACT body penalties.

Fans F1 (rise_top -> E) and F2 (X -> P), 2 points per fan per strand,
right side (left mirrors; per-side reel centres (+/-13, 5), see
reel2.py). Penalties: wire-wire hinge 1.30 (arc-arc cross-strand pairs
excluded - Z-ladder separation 1.12 by design), EXACT signed body
distances (both pitches), slope ceiling, R5 buildability margins on
every pre/post chain segment (trim criterion of geometry.rounded,
1.0 mm buffer, FD gradient for this separable term), E/X joint
deflection <= 100 deg, approach angle at P. R per strand is re-solved
between fan rounds with reel_build's slack accounting (adapted).
Usage: opt_reel_exact.py [fan rounds]
Writes RT15/reel_fans.json and RT15/reel_R.json.
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
import reel2
from exact_oracle import OracleBody
from routes_round14 import split_corners

HERE = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
D = json.load(open(f'{HERE}/routes-round9.json')); B, A = D['before'], D['after']
AXV = np.array([0.8660254, -0.5, 0.0])
RSTATE = {i: 9.2 for i in range(14)}

BOX_LO = np.array([-4., -24., 2.]); BOX_HI = np.array([48., 46., 24.])
OBST = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, k, s in raw:
        if n.startswith('Wire'): continue
        lo = np.array([s.bounding_box().min.X, s.bounding_box().min.Y, s.bounding_box().min.Z])
        hi = np.array([s.bounding_box().max.X, s.bounding_box().max.Y, s.bounding_box().max.Z])
        if np.any(hi < BOX_LO) or np.any(lo > BOX_HI): continue
        if hi[0] < -2: continue
        ob = OracleBody(n, s).restrict(BOX_LO - 3, BOX_HI + 3)
        if len(ob.faces): OBST[(pitch, n)] = ob
print('obstacle bodies:', len(OBST), flush=True)

ORG = {i: dz15.rise_top(i) for i in range(14)}
PNT = {i: dz.stations(B, A, i)[2] for i in range(14)}

def arc_samples(i, R, n=25):
    C = reel2.C; z = reel2.z_of(i)
    e = reel2.entry(i, R)
    a0 = np.arctan2(e[1] - C[1], e[0] - C[0])
    return np.array([[C[0] + R * np.cos(a0 - np.radians(270.0) * k / (n - 1)),
                      C[1] + R * np.sin(a0 - np.radians(270.0) * k / (n - 1)), z]
                     for k in range(n)])

def fixed_pre(i):
    pts = []
    ch = [np.array(B[i][0], float), np.array(B[i][1], float), dz15.corridor(i), ORG[i]]
    for a, b in zip(ch, ch[1:]):
        for tt in np.linspace(0, 1, 9)[:-1]: pts.append(a + (b - a) * tt)
    pts.append(ch[-1])
    return np.array(pts)

def fixed_tail(i):
    ep, G, P = dz.stations(B, A, i)
    pts = []
    for a, b in ((P, G), (G, ep)):
        for tt in np.linspace(0, 1, 9)[:-1]: pts.append(a + (b - a) * tt)
    pts.append(ep)
    return np.array(pts)

FIXPRE = {i: fixed_pre(i) for i in range(14)}
FIXTAIL = {i: fixed_tail(i) for i in range(14)}
ARC = {i: arc_samples(i, RSTATE[i]) for i in range(14)}

NV = 12  # F1a(3) F1b(3) F2a(3) F2b(3)
def var_chains(x, i):
    """Returns (pre_pts, pre_J, post_pts, post_J): samples of the variable
    fan chains with (3,12) Jacobians wrt the strand's 12 vars."""
    f1a = x[i * NV:i * NV + 3]; f1b = x[i * NV + 3:i * NV + 6]
    f2a = x[i * NV + 6:i * NV + 9]; f2b = x[i * NV + 9:i * NV + 12]
    E = reel2.entry(i, RSTATE[i]); X = reel2.exitp(i, RSTATE[i])
    def chain(pts3, blocks):
        pts = []; Js = []
        for s in range(len(pts3) - 1):
            a, b = pts3[s], pts3[s + 1]
            ba, bb = blocks[s], blocks[s + 1]
            for k in range(6):
                t = k / 6
                pts.append(a + (b - a) * t)
                J = np.zeros((3, NV))
                if ba is not None: J[:, ba:ba + 3] = (1 - t) * np.eye(3)
                if bb is not None: J[:, bb:bb + 3] = t * np.eye(3)
                Js.append(J)
        pts.append(pts3[-1]); Js.append(np.zeros((3, NV)))
        return np.array(pts), Js
    pre = chain([ORG[i], f1a, f1b, E], [None, 0, 3, None])
    post = chain([X, f2a, f2b, PNT[i]], [None, 6, 9, None])
    return pre, post

def all_samples(x):
    """Pooled samples with owner + kind tags: 0 fixed, 1 var, 2 arc."""
    pts = []; own = []; kind = []; Js = []
    for i in range(14):
        for arr, kd in ((FIXPRE[i], 0), (ARC[i], 2), (FIXTAIL[i], 0)):
            pts.append(arr); own += [i] * len(arr); kind += [kd] * len(arr)
            Js += [None] * len(arr)
        (pp, pJ), (qp, qJ) = var_chains(x, i)
        for arr, jlist in ((pp, pJ), (qp, qJ)):
            pts.append(arr); own += [i] * len(arr); kind += [1] * len(arr); Js += jlist
    return np.vstack(pts), np.array(own), np.array(kind), Js

X0 = np.zeros(14 * NV)
for i in range(14):
    E = reel2.entry(i, RSTATE[i]); X = reel2.exitp(i, RSTATE[i])
    f1 = [ORG[i] + (E - ORG[i]) * f for f in (1 / 3, 2 / 3)]
    f2 = [X + (PNT[i] - X) * f for f in (1 / 3, 2 / 3)]
    X0[i * NV:i * NV + 12] = np.concatenate(f1 + f2)
CAND = {}
for i in range(14):
    (pp, _), (qp, _) = var_chains(X0, i)
    pts = np.vstack([pp, qp, ARC[i]])
    cand = []
    for key, ob in OBST.items():
        dlb = np.maximum(np.maximum(ob.lo - pts, pts - ob.hi), 0.0)
        if float(np.min(np.sum(dlb * dlb, axis=1))) < 3.5 ** 2: cand.append(key)
    CAND[i] = cand
print('cand per strand:', [len(CAND[i]) for i in range(14)], flush=True)

HB, WB = 1.15, 30.0
HW, WW = 1.30, 3.0
WC = 2.0

def ceiling(y):
    if y < 1.935593: return 21.65, 0.0
    t = min(max((y - 1.935593) / 36.578838, 0), 1)
    return 21.65 - 11.10 * t, (-11.10 / 36.578838 if t < 1 else 0.0)

def trim(p_prev, p, p_next):
    u = p_prev - p; v = p_next - p
    nu = np.linalg.norm(u); nv = np.linalg.norm(v)
    if nu < 1e-12 or nv < 1e-12: return 1e6
    th = np.arccos(np.clip(float(u @ v) / (nu * nv), -1, 1))
    d = 5.0 / np.tan(th / 2) if th < 2.9 else 0.0
    return d if np.isfinite(d) and d >= 1e-8 else 0.0

def build_pen(i, v):
    """Buildability + joint-angle penalty for strand i (vars v, 12,)."""
    f1a, f1b, f2a, f2b = v[0:3], v[3:6], v[6:9], v[9:12]
    E = reel2.entry(i, RSTATE[i]); X = reel2.exitp(i, RSTATE[i])
    ep, G, P = dz.stations(B, A, i)
    pre = [np.array(B[i][1], float), dz15.corridor(i), ORG[i], f1a, f1b, E]
    post = [X, f2a, f2b, P, G]
    pen = 0.0
    for ch in (pre, post):
        tr = [0.0] + [trim(ch[k - 1], ch[k], ch[k + 1]) for k in range(1, len(ch) - 1)] + [0.0]
        for k in range(len(ch) - 1):
            seg = float(np.linalg.norm(ch[k + 1] - ch[k]))
            margin = seg - tr[k] - tr[k + 1]
            if margin < 1.0: pen += 50.0 * (1.0 - margin) ** 2
    # joint deflections at E and X (vs arc tangents)
    for a, b, t in ((f1b, E, reel2.T_ENTRY), (X, f2a, reel2.T_EXIT)):
        u = (b - a); u = u / np.linalg.norm(u)
        phi = np.degrees(np.arccos(np.clip(float(u @ t), -1, 1)))
        if phi > 100.0: pen += 20.0 * ((phi - 100.0) / 10.0) ** 2
    return pen

def objective(x):
    loss = 0.0; grad = np.zeros(14 * NV)
    allp, own, kind, Js = all_samples(x)
    tree = cKDTree(allp)
    for a, b in tree.query_pairs(HW):
        if own[a] == own[b]: continue
        if kind[a] == 2 and kind[b] == 2: continue   # arc-arc: Z ladder by design
        dvec = allp[a] - allp[b]; d = float(np.linalg.norm(dvec))
        if d < 1e-9: continue
        loss += WW * ((HW - d) / 0.3) ** 2
        gv = -2 * WW * (HW - d) / 0.09 * (dvec / d)
        for idx, sgn in ((a, 1.0), (b, -1.0)):
            if kind[idx] == 1:
                i = own[idx]
                grad[i * NV:(i + 1) * NV] += sgn * (Js[idx].T @ gv)
    for i in range(14):
        (pp, pJ), (qp, qJ) = var_chains(x, i)
        for arr, jlist in ((pp, pJ), (qp, qJ)):
            for k, p in enumerate(arr):
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
                            grad[i * NV:(i + 1) * NV] += jlist[k].T @ gv
                c, dc = ceiling(p[1])
                if p[2] > c:
                    u = p[2] - c
                    loss += WC * (u / 0.3) ** 2
                    gv = 2 * WC * u / 0.09 * np.array([0.0, -dc, 1.0])
                    grad[i * NV:(i + 1) * NV] += jlist[k].T @ gv
        # buildability via FD (separable, cheap)
        v = x[i * NV:(i + 1) * NV]
        pen0 = build_pen(i, v)
        loss += pen0
        eps = 1e-6
        for k in range(NV):
            vp = v.copy(); vp[k] += eps
            grad[i * NV + k] += (build_pen(i, vp) - pen0) / eps
        # approach angle at P (analytic, wrt F2b)
        f2b = x[i * NV + 9:i * NV + 12]
        u = PNT[i] - f2b; L = float(np.linalg.norm(u)); kk = -AXV
        c = float(u @ kk) / L
        if c < 0.3:
            loss += 6.0 * ((0.3 - c) / 0.2) ** 2
            dcdu = kk / L - (u @ kk) * u / L ** 3
            grad[i * NV + 9:i * NV + 12] += (-2 * 6.0 * (0.3 - c) / 0.04) * (-dcdu)
    loss += 0.001 * float(np.sum((x - X0) ** 2)); grad += 0.002 * (x - X0)
    return loss, grad

def report(x, label):
    wb_ = (9, None); ww_ = (9, None)
    allp, own, kind, Js = all_samples(x)
    for i in range(14):
        (pp, _), (qp, _) = var_chains(x, i)
        for arr in (pp, qp):
            for p in arr:
                for key in CAND[i]:
                    d, q = OBST[key].dist(p)
                    if d < wb_[0]: wb_ = (d, (i + 1, key, np.round(p, 1)))
    tree = cKDTree(allp)
    for a, b in tree.query_pairs(2.2):
        if own[a] == own[b] or (kind[a] == 2 and kind[b] == 2): continue
        d = float(np.linalg.norm(allp[a] - allp[b]))
        if d < ww_[0]: ww_ = (d, (int(own[a]) + 1, int(own[b]) + 1, np.round(allp[a], 1)))
    fb = (9, None)
    for i in range(14):
        for p in FIXPRE[i]:
            for key in CAND[i]:
                d, q = OBST[key].dist(p)
                if d < fb[0]: fb = (d, (i + 1, key, np.round(p, 1)))
    print('   fixed-pre min body', round(float(fb[0]), 3), fb[1], flush=True)
    print(label, 'min body', round(float(wb_[0]), 3), wb_[1], '| min WW', round(float(ww_[0]), 3),
          ww_[1], '| max build pen', round(float(max(build_pen(i, x[i * NV:(i + 1) * NV]) for i in range(14))), 2), flush=True)
    return wb_, ww_

# ---- slack accounting (reel_build method, reel2 geometry) ----
def path_len(pts):
    return rounded(split_corners(pts)).length
def lossf(phi):
    return 10.0 * np.tan(phi / 2) - 5.0 * phi
def chains(i, R, fans):
    ep, G, P = dz.stations(B, A, i)
    F1, F2 = fans[i]
    E = reel2.entry(i, R); M = reel2.midp(i, R); X = reel2.exitp(i, R)
    pre = [list(B[i][0]), list(B[i][1]), dz15.corridor(i).tolist(), ORG[i].tolist()] + \
          [p.tolist() for p in F1] + [E.tolist()]
    post = [X.tolist()] + [p.tolist() for p in F2] + [P.tolist(), G.tolist(), list(A[i][6])]
    return pre, M, post, E, X, F1, F2
def slack_true(i, R, fans):
    pre, M, post, E, X, F1, F2 = chains(i, R, fans)
    stored = path_len(pre) + R * np.radians(270.0) + path_len(post)
    arr = np.array(E) - np.array(F1[-1]); arr = arr / np.linalg.norm(arr)
    phiE_s = np.arccos(np.clip(float(arr @ reel2.T_ENTRY), -1, 1))
    dep = np.array(F2[0]) - np.array(X); dep = dep / np.linalg.norm(dep)
    phiX_s = np.arccos(np.clip(float(reel2.T_EXIT @ dep), -1, 1))
    stored -= (lossf(phiE_s) + lossf(phiX_s))
    chord = float(np.linalg.norm(np.array(X) - np.array(E)))
    cd = (np.array(X) - np.array(E)) / chord
    phiE_t = np.arccos(np.clip(float(arr @ cd), -1, 1))
    phiX_t = np.arccos(np.clip(float(cd @ dep), -1, 1))
    taut = path_len(pre) + chord + path_len(post) - lossf(phiE_t) - lossf(phiX_t)
    return stored - taut, stored, taut
def solve_R(i, fans, target=30.2):
    lo, hi = 5.0, 10.5
    flo = slack_true(i, lo, fans)[0]; fhi = slack_true(i, hi, fans)[0]
    if not (flo < target < fhi): return None, flo, fhi
    for _ in range(10):
        mid = (lo + hi) / 2
        if slack_true(i, mid, fans)[0] < target: lo = mid
        else: hi = mid
    R = (lo + hi) / 2
    return R, slack_true(i, R, fans)[0], None

if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    x = X0.copy()
    report(x, 'init')
    BND = []
    for i in range(14): BND += [(0, 46), (-16, 44), (3.4, 21.8)] * 4
    fans = None
    for rnd in range(rounds):
        t = time.time()
        r = minimize(objective, x, jac=True, method='L-BFGS-B', bounds=BND,
                     options={'maxiter': 250, 'ftol': 1e-12})
        x = r.x
        print(f'fan round {rnd}: loss {r.fun:.3f} nit {r.nit} time {time.time()-t:.0f}s', flush=True)
        report(x, f'fan round {rnd}')
        fans = {i: ([x[i * NV:i * NV + 3], x[i * NV + 3:i * NV + 6]],
                    [x[i * NV + 6:i * NV + 9], x[i * NV + 9:i * NV + 12]]) for i in range(14)}
        bad = []
        for i in range(14):
            R, s, bracket = solve_R(i, fans)
            if R is None: bad.append((i + 1, bracket))
            else: RSTATE[i] = R
        print('R solve:', {i + 1: round(RSTATE[i], 2) for i in range(14)}, 'bracket failures:', bad, flush=True)
        ARC.update({i: arc_samples(i, RSTATE[i]) for i in range(14)})
        json.dump({str(i + 1): {'F1': [[round(float(v), 3) for v in p] for p in fans[i][0]],
                                'F2': [[round(float(v), 3) for v in p] for p in fans[i][1]]} for i in range(14)},
                  open(f'{RT15}/reel_fans.json', 'w'), indent=1)
        json.dump({str(i + 1): round(float(RSTATE[i]), 4) for i in range(14)},
                  open(f'{RT15}/reel_R.json', 'w'), indent=1)
    print('saved reel_fans.json + reel_R.json', flush=True)
