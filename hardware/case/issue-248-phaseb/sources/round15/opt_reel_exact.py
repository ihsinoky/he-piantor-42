"""Round 15 reel fan optimisation with EXACT body penalties (v2).

Variables per strand (15): climb waypoint W (X pinned to the strand
plane fx; the corridor->rise climb must thread the Wing board's south
edge - a straight climb crosses the board, exact distance -0.35 at
strand 1), reel fans F1 (rise_top -> E) and F2 (X -> P), 2 points
each. Right side (left mirrors; per-side reel centres (+/-13, 5),
reel2.py). Penalties: wire-wire hinge 1.30 (arc-arc cross-strand
pairs excluded - Z-ladder separation 1.12 by design), EXACT signed
body distances (both pitches), slope ceiling, R5 buildability
margins on every pre/post chain segment (trim criterion of
geometry.rounded, 1.0 mm buffer, FD gradient for this separable
term), E/X joint deflection <= 100 deg, approach angle at P.
R per strand re-solved between fan rounds with reel_build's slack
accounting (adapted to reel2 + W).
Usage: opt_reel_exact.py [fan rounds]
Writes RT15/reel_fans.json ({W,F1,F2} per strand) and reel_R.json.
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
ORG = {i: dz15.rise_top(i) for i in range(14)}
COR = {i: dz15.corridor(i) for i in range(14)}
PNT = {i: dz.stations(B, A, i)[2] for i in range(14)}

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

def arc_samples(i, R, n=25):
    C = reel2.C; z = reel2.z_of(i)
    e = reel2.entry(i, R)
    a0 = np.arctan2(e[1] - C[1], e[0] - C[0])
    return np.array([[C[0] + R * np.cos(a0 - np.radians(270.0) * k / (n - 1)),
                      C[1] + R * np.sin(a0 - np.radians(270.0) * k / (n - 1)), z]
                     for k in range(n)])

def samples_of(ch, nseg=9):
    pts = []
    for a, b in zip(ch, ch[1:]):
        for tt in np.linspace(0, 1, nseg)[:-1]: pts.append(a + (b - a) * tt)
    pts.append(ch[-1])
    return np.array(pts)

FIXPRE = {i: samples_of([np.array(B[i][0], float), np.array(B[i][1], float), COR[i]]) for i in range(14)}
FIXTAIL = {i: samples_of([dz.stations(B, A, i)[2], dz.stations(B, A, i)[1], np.array(A[i][6], float)]) for i in range(14)}
ARC = {i: arc_samples(i, RSTATE[i]) for i in range(14)}

NV = 15  # W(3) F1a(3) F1b(3) F2a(3) F2b(3)
BLK = dict(W=0, F1a=3, F1b=6, F2a=9, F2b=12)
def _chain(pts3, blocks, nseg=6):
    pts = []; Js = []
    for s in range(len(pts3) - 1):
        a, b = pts3[s], pts3[s + 1]
        ba, bb = blocks[s], blocks[s + 1]
        for k in range(nseg):
            t = k / nseg
            pts.append(a + (b - a) * t)
            J = np.zeros((3, NV))
            if ba is not None: J[:, ba:ba + 3] = (1 - t) * np.eye(3)
            if bb is not None: J[:, bb:bb + 3] = t * np.eye(3)
            Js.append(J)
    pts.append(pts3[-1]); Js.append(np.zeros((3, NV)))
    return np.array(pts), Js

def var_chains(x, i):
    v = x[i * NV:(i + 1) * NV]
    W = v[0:3]; f1a = v[3:6]; f1b = v[6:9]; f2a = v[9:12]; f2b = v[12:15]
    E = reel2.entry(i, RSTATE[i]); X = reel2.exitp(i, RSTATE[i])
    climb = _chain([COR[i], W, ORG[i]], [None, BLK['W'], None])
    fan1 = _chain([ORG[i], f1a, f1b, E], [None, BLK['F1a'], BLK['F1b'], None])
    fan2 = _chain([X, f2a, f2b, PNT[i]], [None, BLK['F2a'], BLK['F2b'], None])
    return climb, fan1, fan2

def all_samples(x):
    pts = []; own = []; kind = []; Js = []
    for i in range(14):
        for arr, kd in ((FIXPRE[i], 0), (ARC[i], 2), (FIXTAIL[i], 0)):
            pts.append(arr); own += [i] * len(arr); kind += [kd] * len(arr)
            Js += [None] * len(arr)
        for arr, jlist in var_chains(x, i):
            pts.append(arr); own += [i] * len(arr); kind += [1] * len(arr); Js += jlist
    return np.vstack(pts), np.array(own), np.array(kind), Js

def _bez(a, q, b, t):
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * q + t ** 2 * b
X0 = np.zeros(14 * NV)
for i in range(14):
    E = reel2.entry(i, RSTATE[i]); X = reel2.exitp(i, RSTATE[i])
    W = np.array([dz.fx_of(i), -14.0, 6.8])
    q1 = ORG[i] + 0.45 * (E - ORG[i]) + np.array([0., 0., 1.5])
    f1 = [_bez(ORG[i], q1, E, 1 / 3), _bez(ORG[i], q1, E, 2 / 3)]
    q2 = X + 0.5 * (PNT[i] - X) + np.array([0., 0., -1.0])
    f2 = [_bez(X, q2, PNT[i], 1 / 3), _bez(X, q2, PNT[i], 2 / 3)]
    X0[i * NV:(i + 1) * NV] = np.concatenate([W] + f1 + f2)
CAND = {}
for i in range(14):
    pts = np.vstack([c[0] for c in var_chains(X0, i)] + [ARC[i]])
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
    th = min(max(th, 1e-4), np.pi - 1e-4)
    d = 5.0 / np.tan(th / 2)
    return float(min(d, 50.0)) if np.isfinite(d) else 50.0

def build_pen(i, v):
    W = v[0:3]; f1a = v[3:6]; f1b = v[6:9]; f2a = v[9:12]; f2b = v[12:15]
    E = reel2.entry(i, RSTATE[i]); X = reel2.exitp(i, RSTATE[i])
    ep, G, P = dz.stations(B, A, i)
    pre = [np.array(B[i][1], float), COR[i], W, ORG[i], f1a, f1b, E]
    post = [X, f2a, f2b, P, G]
    pen = 0.0
    for ch in (pre, post):
        tr = [0.0] + [trim(ch[k - 1], ch[k], ch[k + 1]) for k in range(1, len(ch) - 1)] + [0.0]
        for k in range(len(ch) - 1):
            seg = float(np.linalg.norm(ch[k + 1] - ch[k]))
            margin = seg - tr[k] - tr[k + 1]
            if margin < 1.0: pen += 50.0 * (1.0 - margin) ** 2
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
        if kind[a] == 2 and kind[b] == 2: continue
        dvec = allp[a] - allp[b]; d = float(np.linalg.norm(dvec))
        if d < 1e-9: continue
        loss += WW * ((HW - d) / 0.45) ** 2
        gv = -2 * WW * (HW - d) / 0.2025 * (dvec / d)
        for idx, sgn in ((a, 1.0), (b, -1.0)):
            if kind[idx] == 1:
                i = own[idx]
                grad[i * NV:(i + 1) * NV] += sgn * (Js[idx].T @ gv)
    for i in range(14):
        for arr, jlist in var_chains(x, i):
            for k, p in enumerate(arr):
                for key in CAND[i]:
                    ob = OBST[key]
                    dlb = np.maximum(np.maximum(ob.lo - p, p - ob.hi), 0.0)
                    if float(dlb @ dlb) > (HB + 0.6) ** 2: continue
                    d, q = ob.dist_capped(p, HB)
                    if d < HB and q is not None:
                        loss += WB * ((HB - d) / 0.45) ** 2
                        nrm = float(np.linalg.norm(p - q))
                        if nrm > 1e-9:
                            dirv = (p - q) / nrm if d >= 0 else (q - p) / nrm
                            gv = -2 * WB * (HB - d) / 0.2025 * dirv
                            grad[i * NV:(i + 1) * NV] += jlist[k].T @ gv
                c, dc = ceiling(p[1])
                if p[2] > c:
                    u = p[2] - c
                    loss += WC * (u / 0.45) ** 2
                    gv = 2 * WC * u / 0.2025 * np.array([0.0, -dc, 1.0])
                    grad[i * NV:(i + 1) * NV] += jlist[k].T @ gv
        v = x[i * NV:(i + 1) * NV]
        pen0 = build_pen(i, v)
        loss += pen0
        eps = 1e-6
        for k in range(NV):
            vp = v.copy(); vp[k] += eps
            grad[i * NV + k] += (build_pen(i, vp) - pen0) / eps
        f2b = x[i * NV + 12:i * NV + 15]
        u = PNT[i] - f2b; L = float(np.linalg.norm(u)); kk = -AXV
        c = float(u @ kk) / L
        if c < 0.3:
            loss += 6.0 * ((0.3 - c) / 0.2) ** 2
            dcdu = kk / L - (u @ kk) * u / L ** 3
            grad[i * NV + 12:i * NV + 15] += (-2 * 6.0 * (0.3 - c) / 0.04) * (-dcdu)
    loss += 0.001 * float(np.sum((x - X0) ** 2)); grad += 0.002 * (x - X0)
    return loss, grad

def report(x, label):
    wb_ = (9, None); ww_ = (9, None)
    allp, own, kind, Js = all_samples(x)
    for i in range(14):
        for arr, jlist in var_chains(x, i):
            for p in arr:
                for key in CAND[i]:
                    d, q = OBST[key].dist(p)
                    if d < wb_[0]: wb_ = (d, (i + 1, key, np.round(p, 1)))
    fb = (9, None)
    for i in range(14):
        for p in FIXPRE[i]:
            for key in CAND[i]:
                d, q = OBST[key].dist(p)
                if d < fb[0]: fb = (d, (i + 1, key, np.round(p, 1)))
    tree = cKDTree(allp)
    for a, b in tree.query_pairs(2.2):
        if own[a] == own[b] or (kind[a] == 2 and kind[b] == 2): continue
        d = float(np.linalg.norm(allp[a] - allp[b]))
        if d < ww_[0]: ww_ = (d, (int(own[a]) + 1, int(own[b]) + 1, np.round(allp[a], 1)))
    print(label, 'min body', round(float(wb_[0]), 3), wb_[1], '| fixed-pre', round(float(fb[0]), 3),
          fb[1], '| min WW', round(float(ww_[0]), 3), ww_[1],
          '| max build pen', round(float(max(build_pen(i, x[i * NV:(i + 1) * NV]) for i in range(14))), 2), flush=True)
    return wb_, ww_

def path_len(pts):
    return rounded(split_corners(pts)).length
def lossf(phi):
    return 10.0 * np.tan(phi / 2) - 5.0 * phi
def chains(i, R, sol):
    """sol[i] = (W, F1, F2). Returns pre, M, post, E, X."""
    W, F1, F2 = sol[i]
    ep, G, P = dz.stations(B, A, i)
    E = reel2.entry(i, R); M = reel2.midp(i, R); X = reel2.exitp(i, R)
    pre = [list(B[i][0]), list(B[i][1]), COR[i].tolist(), np.asarray(W, float).tolist(),
           ORG[i].tolist()] + [np.asarray(p, float).tolist() for p in F1] + [E.tolist()]
    post = [X.tolist()] + [np.asarray(p, float).tolist() for p in F2] + \
           [P.tolist(), G.tolist(), list(A[i][6])]
    return pre, M, post, E, X
def slack_true(i, R, sol):
    pre, M, post, E, X = chains(i, R, sol)
    W, F1, F2 = sol[i]
    stored = path_len(pre) + R * np.radians(270.0) + path_len(post)
    arr = np.array(E) - np.array(F1[-1], float); arr = arr / np.linalg.norm(arr)
    phiE_s = np.arccos(np.clip(float(arr @ reel2.T_ENTRY), -1, 1))
    dep = np.array(F2[0], float) - np.array(X); dep = dep / np.linalg.norm(dep)
    phiX_s = np.arccos(np.clip(float(reel2.T_EXIT @ dep), -1, 1))
    stored -= (lossf(phiE_s) + lossf(phiX_s))
    chord = float(np.linalg.norm(np.array(X) - np.array(E)))
    cd = (np.array(X) - np.array(E)) / chord
    phiE_t = np.arccos(np.clip(float(arr @ cd), -1, 1))
    phiX_t = np.arccos(np.clip(float(cd @ dep), -1, 1))
    taut = path_len(pre) + chord + path_len(post) - lossf(phiE_t) - lossf(phiX_t)
    return stored - taut, stored, taut
def solve_R(i, sol, target=30.2):
    lo, hi = 5.0, 10.5
    flo = slack_true(i, lo, sol)[0]; fhi = slack_true(i, hi, sol)[0]
    if not (flo < target < fhi): return None, flo, fhi
    for _ in range(10):
        mid = (lo + hi) / 2
        if slack_true(i, mid, sol)[0] < target: lo = mid
        else: hi = mid
    R = (lo + hi) / 2
    return R, slack_true(i, R, sol)[0], None

def sol_of(x):
    return {i: (x[i * NV:i * NV + 3],
                [x[i * NV + 3:i * NV + 6], x[i * NV + 6:i * NV + 9]],
                [x[i * NV + 9:i * NV + 12], x[i * NV + 12:i * NV + 15]]) for i in range(14)}

if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    x = X0.copy()
    report(x, 'init')
    BND = []
    for i in range(14):
        fx = dz.fx_of(i)
        BND += [(fx - 0.001, fx + 0.001), (-17.5, -8.0), (4.8, 10.4)]
        BND += [(0, 46), (-16, 44), (3.4, 21.8)] * 4
    for rnd in range(rounds):
        t = time.time(); nit = 0
        for chunk in range(4):
            r = minimize(objective, x, jac=True, method='L-BFGS-B', bounds=BND,
                         options={'maxiter': 60, 'ftol': 1e-11, 'maxls': 40})
            x = r.x; nit += r.nit
            print(f'  chunk {chunk}: loss {r.fun:.1f} nit {r.nit} msg {r.message}', flush=True)
            report(x, f'  chunk {chunk}')
        print(f'fan round {rnd}: loss {r.fun:.3f} nit {nit} time {time.time()-t:.0f}s', flush=True)
        report(x, f'fan round {rnd}')
        sol = sol_of(x)
        bad = []
        for i in range(14):
            R, s, bracket = solve_R(i, sol)
            if R is None: bad.append((i + 1, bracket))
            else: RSTATE[i] = R
        print('R solve:', {i + 1: round(RSTATE[i], 2) for i in range(14)}, 'bracket failures:', bad, flush=True)
        ARC.update({i: arc_samples(i, RSTATE[i]) for i in range(14)})
        json.dump({str(i + 1): {'W': [round(float(v), 3) for v in sol[i][0]],
                                'F1': [[round(float(v), 3) for v in p] for p in sol[i][1]],
                                'F2': [[round(float(v), 3) for v in p] for p in sol[i][2]]} for i in range(14)},
                  open(f'{RT15}/reel_fans.json', 'w'), indent=1)
        json.dump({str(i + 1): round(float(RSTATE[i]), 4) for i in range(14)},
                  open(f'{RT15}/reel_R.json', 'w'), indent=1)
    print('saved reel_fans.json + reel_R.json', flush=True)
