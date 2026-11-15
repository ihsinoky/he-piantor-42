"""Round 15 reel v3 optimisation: per-strand disk placements
(reel3.py / RT15/reel_place.json), sides independent.

Variables per (side, strand): climb waypoint W (X pinned to the
strand plane), fans F1 (rise -> entry) and F2 (exit -> P), 2 points
each (15 vars; 420 total). Penalties: wire-wire hinge 1.30 (1.05 for
arc-arc), EXACT signed body distances both pitches (dense samples,
<= 1.5 mm spacing - the coarse 6/segment screen of earlier runs was
blind to shallow crossings), slope ceiling, R5 buildability margins
(FD gradient), joint deflections, approach angle at P. R re-solved
per strand between rounds (round-14 slack accounting, reel3
geometry). Usage: opt_reel3.py [rounds]
Writes RT15/reel_fans3.json, RT15/reel_R3.json.
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
import reel3
from exact_oracle import OracleBody
from routes_round14 import split_corners

HERE = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
D = json.load(open(f'{HERE}/routes-round9.json')); B, A = D['before'], D['after']
SIDES = ('right', 'left')
SGN = {'right': 1, 'left': -1}
KEYS = [(s, i) for s in SIDES for i in range(14)]
KIDX = {k: n for n, k in enumerate(KEYS)}
RSTATE = {k: reel3.PLACE_R[k[0]][k[1]] for k in KEYS}

def mir(side, p):
    p = np.array(p, float)
    return p * [SGN[side], 1, 1]
ORG = {k: mir(k[0], dz15.rise_top(k[1])) for k in KEYS}
COR = {k: mir(k[0], dz15.corridor(k[1])) for k in KEYS}
PNT = {k: mir(k[0], dz.stations(B, A, k[1])[2]) for k in KEYS}
GST = {k: mir(k[0], dz.stations(B, A, k[1])[1]) for k in KEYS}
EPT = {k: mir(k[0], A[k[1]][6]) for k in KEYS}
B0 = {k: mir(k[0], B[k[1]][0]) for k in KEYS}
B1 = {k: mir(k[0], B[k[1]][1]) for k in KEYS}

BOX_LO = np.array([-48., -24., 2.]); BOX_HI = np.array([48., 46., 24.])
OBST = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, kk, s in raw:
        if n.startswith('Wire'): continue
        lo = np.array([s.bounding_box().min.X, s.bounding_box().min.Y, s.bounding_box().min.Z])
        hi = np.array([s.bounding_box().max.X, s.bounding_box().max.Y, s.bounding_box().max.Z])
        if np.any(hi < BOX_LO) or np.any(lo > BOX_HI): continue
        ob = OracleBody(n, s).restrict(BOX_LO - 3, BOX_HI + 3)
        if len(ob.faces): OBST[(pitch, n)] = ob
print('obstacle bodies:', len(OBST), flush=True)
OBST_SIDE = {}
for side in SIDES:
    if side == 'right':
        OBST_SIDE[side] = {k: v for k, v in OBST.items() if v.hi[0] >= -2}
    else:
        OBST_SIDE[side] = {k: v for k, v in OBST.items() if v.lo[0] <= 2}

def arc_samples(k, R, n=25):
    C, Z = reel3.PLACE[k[0]][k[1]]
    e = reel3.entry(k[0], k[1], R)
    a0 = np.arctan2(e[1] - C[1], e[0] - C[0])
    sweep = -np.radians(270.0) * SGN[k[0]]
    return np.array([[C[0] + R * np.cos(a0 + sweep * j / (n - 1)),
                      C[1] + R * np.sin(a0 + sweep * j / (n - 1)), Z] for j in range(n)])

def samples_of(ch, nseg=9):
    pts = []
    for a, b in zip(ch, ch[1:]):
        for tt in np.linspace(0, 1, nseg)[:-1]: pts.append(a + (b - a) * tt)
    pts.append(ch[-1])
    return np.array(pts)

FIXPRE = {k: samples_of([B0[k], B1[k], COR[k]]) for k in KEYS}
FIXTAIL = {k: samples_of([PNT[k], GST[k], EPT[k]]) for k in KEYS}
ARC = {k: arc_samples(k, RSTATE[k]) for k in KEYS}

NV = 15
def _chain(pts3, blocks):
    pts = []; Js = []
    for s in range(len(pts3) - 1):
        a, b = pts3[s], pts3[s + 1]
        ba, bb = blocks[s], blocks[s + 1]
        ns = max(6, int(np.ceil(float(np.linalg.norm(b - a)) / 1.5)))
        for kk in range(ns):
            t = kk / ns
            pts.append(a + (b - a) * t)
            J = np.zeros((3, NV))
            if ba is not None: J[:, ba:ba + 3] = (1 - t) * np.eye(3)
            if bb is not None: J[:, bb:bb + 3] = t * np.eye(3)
            Js.append(J)
    pts.append(pts3[-1]); Js.append(np.zeros((3, NV)))
    return np.array(pts), Js

def var_chains(x, k):
    base = KIDX[k] * NV
    v = x[base:base + NV]
    W = v[0:3]; f1a = v[3:6]; f1b = v[6:9]; f2a = v[9:12]; f2b = v[12:15]
    E = reel3.entry(k[0], k[1], RSTATE[k]); X = reel3.exitp(k[0], k[1], RSTATE[k])
    climb = _chain([COR[k], W, ORG[k]], [None, 0, None])
    fan1 = _chain([ORG[k], f1a, f1b, E], [None, 3, 6, None])
    fan2 = _chain([X, f2a, f2b, PNT[k]], [None, 9, 12, None])
    return climb, fan1, fan2

def all_samples(x):
    pts = []; own = []; kind = []; Js = []
    for k in KEYS:
        for arr, kd in ((FIXPRE[k], 0), (ARC[k], 2), (FIXTAIL[k], 0)):
            pts.append(arr); own += [KIDX[k]] * len(arr); kind += [kd] * len(arr)
            Js += [None] * len(arr)
        for arr, jlist in var_chains(x, k):
            pts.append(arr); own += [KIDX[k]] * len(arr); kind += [1] * len(arr); Js += jlist
    return np.vstack(pts), np.array(own), np.array(kind), Js

def _bez(a, q, b, t):
    return (1 - t) ** 2 * a + 2 * (1 - t) * t * q + t ** 2 * b
X0 = np.zeros(len(KEYS) * NV)
for k in KEYS:
    base = KIDX[k] * NV
    E = reel3.entry(k[0], k[1], RSTATE[k]); X = reel3.exitp(k[0], k[1], RSTATE[k])
    W = np.array([dz.fx_of(k[1]) * SGN[k[0]], -14.0, 6.8])
    q1 = ORG[k] + 0.45 * (E - ORG[k]) + np.array([0., 0., 1.5])
    f1 = [_bez(ORG[k], q1, E, 1 / 3), _bez(ORG[k], q1, E, 2 / 3)]
    q2 = X + 0.5 * (PNT[k] - X) + np.array([0., 0., -1.0])
    f2 = [_bez(X, q2, PNT[k], 1 / 3), _bez(X, q2, PNT[k], 2 / 3)]
    X0[base:base + NV] = np.concatenate([W] + f1 + f2)
CAND = {}
for k in KEYS:
    pts = np.vstack([c[0] for c in var_chains(X0, k)] + [ARC[k]])
    cand = []
    for key, ob in OBST_SIDE[k[0]].items():
        dlb = np.maximum(np.maximum(ob.lo - pts, pts - ob.hi), 0.0)
        if float(np.min(np.sum(dlb * dlb, axis=1))) < 3.5 ** 2: cand.append(key)
    CAND[k] = cand
print('cand per strand:', [len(CAND[k]) for k in KEYS], flush=True)

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
    if nu < 1e-12 or nv < 1e-12: return 50.0
    th = np.arccos(np.clip(float(u @ v) / (nu * nv), -1, 1))
    th = min(max(th, 1e-4), np.pi - 1e-4)
    d = 5.0 / np.tan(th / 2)
    return float(min(d, 50.0)) if np.isfinite(d) else 50.0

def build_pen(k, v):
    W = v[0:3]; f1a = v[3:6]; f1b = v[6:9]; f2a = v[9:12]; f2b = v[12:15]
    E = reel3.entry(k[0], k[1], RSTATE[k]); X = reel3.exitp(k[0], k[1], RSTATE[k])
    TE, TX = reel3.tangents(k[0])
    pre = [B1[k], COR[k], W, ORG[k], f1a, f1b, E]
    post = [X, f2a, f2b, PNT[k], GST[k]]
    pen = 0.0
    for ch in (pre, post):
        tr = [0.0] + [trim(ch[j - 1], ch[j], ch[j + 1]) for j in range(1, len(ch) - 1)] + [0.0]
        for j in range(len(ch) - 1):
            seg = float(np.linalg.norm(ch[j + 1] - ch[j]))
            margin = seg - tr[j] - tr[j + 1]
            if margin < 1.0: pen += 50.0 * (1.0 - margin) ** 2
    for a, b, t in ((f1b, E, TE), (X, f2a, TX)):
        u = (b - a); u = u / np.linalg.norm(u)
        phi = np.degrees(np.arccos(np.clip(float(u @ t), -1, 1)))
        if phi > 100.0: pen += 20.0 * ((phi - 100.0) / 10.0) ** 2
    return pen

def objective(x):
    loss = 0.0; grad = np.zeros(len(KEYS) * NV)
    allp, own, kind, Js = all_samples(x)
    tree = cKDTree(allp)
    for a, b in tree.query_pairs(HW):
        if own[a] == own[b]: continue
        hinge = 1.05 if (kind[a] == 2 and kind[b] == 2) else HW
        dvec = allp[a] - allp[b]; d = float(np.linalg.norm(dvec))
        if d < 1e-9 or d >= hinge: continue
        loss += WW * ((hinge - d) / 0.45) ** 2
        gv = -2 * WW * (hinge - d) / 0.2025 * (dvec / d)
        for idx, sgn in ((a, 1.0), (b, -1.0)):
            if kind[idx] == 1:
                base = own[idx] * NV
                grad[base:base + NV] += sgn * (Js[idx].T @ gv)
    for k in KEYS:
        base = KIDX[k] * NV
        for arr, jlist in var_chains(x, k):
            for kk, p in enumerate(arr):
                for key in CAND[k]:
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
                            grad[base:base + NV] += jlist[kk].T @ gv
                c, dc = ceiling(p[1])
                if p[2] > c:
                    u = p[2] - c
                    loss += WC * (u / 0.45) ** 2
                    gv = 2 * WC * u / 0.2025 * np.array([0.0, -dc, 1.0])
                    grad[base:base + NV] += jlist[kk].T @ gv
        v = x[base:base + NV]
        pen0 = build_pen(k, v)
        loss += pen0
        eps = 1e-6
        for j in range(NV):
            vp = v.copy(); vp[j] += eps
            grad[base + j] += (build_pen(k, vp) - pen0) / eps
        f2b = x[base + 12:base + 15]
        axv = np.array([0.8660254 * SGN[k[0]], -0.5, 0.0])
        u = PNT[k] - f2b; L = float(np.linalg.norm(u)); kk2 = -axv
        c = float(u @ kk2) / L
        if c < 0.3:
            loss += 6.0 * ((0.3 - c) / 0.2) ** 2
            dcdu = kk2 / L - (u @ kk2) * u / L ** 3
            grad[base + 12:base + 15] += (-2 * 6.0 * (0.3 - c) / 0.04) * (-dcdu)
    loss += 0.001 * float(np.sum((x - X0) ** 2)); grad += 0.002 * (x - X0)
    return loss, grad

def report(x, label):
    wb_ = (9, None); ww_ = (9, None)
    allp, own, kind, Js = all_samples(x)
    for k in KEYS:
        for arr, jlist in var_chains(x, k):
            for p in arr:
                for key in CAND[k]:
                    d, q = OBST[key].dist(p)
                    if d < wb_[0]: wb_ = (d, (k, key, np.round(p, 1)))
    tree = cKDTree(allp)
    for a, b in tree.query_pairs(2.2):
        if own[a] == own[b]: continue
        d = float(np.linalg.norm(allp[a] - allp[b]))
        if d < ww_[0]: ww_ = (d, (KEYS[own[a]], KEYS[own[b]], np.round(allp[a], 1)))
    print(label, 'min body', round(float(wb_[0]), 3), wb_[1], '| min WW', round(float(ww_[0]), 3),
          ww_[1], '| max build pen', round(float(max(build_pen(k, x[KIDX[k] * NV:(KIDX[k] + 1) * NV]) for k in KEYS)), 2), flush=True)

def path_len(pts):
    return rounded(split_corners(pts)).length
def lossf(phi):
    return 10.0 * np.tan(phi / 2) - 5.0 * phi
def chains(k, R, sol):
    W, F1, F2 = sol[k]
    E = reel3.entry(k[0], k[1], R); M = reel3.midp(k[0], k[1], R); X = reel3.exitp(k[0], k[1], R)
    pre = [B0[k].tolist(), B1[k].tolist(), COR[k].tolist(), np.asarray(W, float).tolist(),
           ORG[k].tolist()] + [np.asarray(p, float).tolist() for p in F1] + [E.tolist()]
    post = [X.tolist()] + [np.asarray(p, float).tolist() for p in F2] + \
           [PNT[k].tolist(), GST[k].tolist(), EPT[k].tolist()]
    return pre, M, post, E, X
def slack_true(k, R, sol):
    pre, M, post, E, X = chains(k, R, sol)
    W, F1, F2 = sol[k]
    TE, TX = reel3.tangents(k[0])
    stored = path_len(pre) + R * np.radians(270.0) + path_len(post)
    arr = np.array(E) - np.array(F1[-1], float); arr = arr / np.linalg.norm(arr)
    phiE_s = np.arccos(np.clip(float(arr @ TE), -1, 1))
    dep = np.array(F2[0], float) - np.array(X); dep = dep / np.linalg.norm(dep)
    phiX_s = np.arccos(np.clip(float(TX @ dep), -1, 1))
    stored -= (lossf(phiE_s) + lossf(phiX_s))
    chord = float(np.linalg.norm(np.array(X) - np.array(E)))
    cd = (np.array(X) - np.array(E)) / chord
    phiE_t = np.arccos(np.clip(float(arr @ cd), -1, 1))
    phiX_t = np.arccos(np.clip(float(cd @ dep), -1, 1))
    taut = path_len(pre) + chord + path_len(post) - lossf(phiE_t) - lossf(phiX_t)
    return stored - taut, stored, taut
def solve_R(k, sol, target=30.2):
    lo, hi = max(6.5, RSTATE[k] - 1.5), min(10.3, RSTATE[k] + 0.3)
    try:
        flo = slack_true(k, lo, sol)[0]; fhi = slack_true(k, hi, sol)[0]
    except AssertionError:
        return None, None, None
    if not (flo < target < fhi): return None, flo, fhi
    for _ in range(10):
        mid = (lo + hi) / 2
        try:
            sm = slack_true(k, mid, sol)[0]
        except AssertionError:
            return None, None, None
        if sm < target: lo = mid
        else: hi = mid
    R = (lo + hi) / 2
    return R, slack_true(k, R, sol)[0], None

def sol_of(x):
    out = {}
    for k in KEYS:
        base = KIDX[k] * NV; v = x[base:base + NV]
        out[k] = (v[0:3], [v[3:6], v[6:9]], [v[9:12], v[12:15]])
    return out

if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    x = X0.copy()
    report(x, 'init')
    BND = []
    for k in KEYS:
        fx = dz.fx_of(k[1]) * SGN[k[0]]
        BND += [(fx - 0.001, fx + 0.001), (-17.5, -8.0), (4.8, 10.4)]
        xb = (0, 46) if k[0] == 'right' else (-46, 0)
        BND += [xb, (-16, 44), (3.4, 21.8)] * 4
    for rnd in range(rounds):
        t = time.time(); nit = 0
        for chunk in range(4):
            r = minimize(objective, x, jac=True, method='L-BFGS-B', bounds=BND,
                         options={'maxiter': 60, 'ftol': 1e-11, 'maxls': 40})
            x = r.x; nit += r.nit
            print(f'  chunk {chunk}: loss {r.fun:.1f} nit {r.nit} msg {r.message}', flush=True)
            report(x, f'  chunk {chunk}')
        print(f'round {rnd}: loss {r.fun:.3f} nit {nit} time {time.time()-t:.0f}s', flush=True)
        sol = sol_of(x)
        bad = []
        for k in KEYS:
            R, s, bracket = solve_R(k, sol)
            if R is None: bad.append((k, bracket))
            else: RSTATE[k] = R
        print('R solve:', {f'{k[0][0]}{k[1]+1}': round(RSTATE[k], 2) for k in KEYS}, 'failures:', bad, flush=True)
        ARC.update({k: arc_samples(k, RSTATE[k]) for k in KEYS})
        json.dump({s: {str(i): {'W': [round(float(v), 3) for v in sol[(s, i)][0]],
                                'F1': [[round(float(v), 3) for v in p] for p in sol[(s, i)][1]],
                                'F2': [[round(float(v), 3) for v in p] for p in sol[(s, i)][2]]}
                       for i in range(14)} for s in SIDES},
                  open(f'{RT15}/reel_fans3.json', 'w'), indent=1)
        json.dump({s: {str(i): round(float(RSTATE[(s, i)]), 4) for i in range(14)} for s in SIDES},
                  open(f'{RT15}/reel_R3.json', 'w'), indent=1)
    print('saved reel_fans3.json + reel_R3.json', flush=True)
