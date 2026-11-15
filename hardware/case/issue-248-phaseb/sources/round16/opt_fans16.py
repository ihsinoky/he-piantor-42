"""Round 16 reel fan optimisation (task 2, phase B) on CONTINUOUS
placements from place16.py. Generalises round 15's opt_reel_exact:
per design strand the storage ring is (C, Z, R, a0, theta) from
RT16/place16.json; entry/mid/exit and both arc tangents derive from
it. Variables per strand (15): climb waypoint W (X pinned to fx),
fans F1 (rise_top -> E) and F2 (X -> P), 2 points each. Penalties as
round 15: WW hinge 1.30 (arc-arc cross-strand pairs excluded; the
placement phase guaranteed ring-ring sample separation), EXACT
signed body distances (both pitches), slope ceiling, R5 buildability
margins (1.0 mm buffer), E/X joint deflection <= 100 deg vs the
strand's own arc tangents, approach angle at P. Solver: Adam
(persisted moments). After each round, theta is re-solved per
strand (bisection on the generalised slack_true) so the analytic
slack is exactly +30.20; placements updated in place16.json.
State: RT16/fans16.json. Usage: opt_fans16.py [rounds] [chunks] [steps]
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
from routes_round14 import split_corners
from geometry import rounded

HERE = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT16 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round16'
D = json.load(open(f'{HERE}/routes-round9.json')); B, A = D['before'], D['after']
AXV = np.array([0.8660254, -0.5, 0.0])
ORG = {i: dz15.rise_top(i) for i in range(14)}
COR = {i: dz15.corridor(i) for i in range(14)}
PNT = {i: dz.stations(B, A, i)[2] for i in range(14)}

def load_place():
    W = json.load(open(f'{RT16}/place16.json'))
    return {i: dict(C=np.array([W[str(i + 1)][0], W[str(i + 1)][1]]),
                    Z=W[str(i + 1)][2], R=W[str(i + 1)][3],
                    a0=W[str(i + 1)][4], th=W[str(i + 1)][5]) for i in range(14)}
PLACE = load_place()

def u(a): return np.array([np.cos(a), np.sin(a)])
def entry(i):
    p = PLACE[i]; q = p['C'] + p['R'] * u(p['a0']); return np.array([q[0], q[1], p['Z']])
def exitp(i):
    p = PLACE[i]; q = p['C'] + p['R'] * u(p['a0'] - p['th']); return np.array([q[0], q[1], p['Z']])
def midp(i):
    p = PLACE[i]; q = p['C'] + p['R'] * u(p['a0'] - p['th'] / 2); return np.array([q[0], q[1], p['Z']])
def tan_e(i):
    a = PLACE[i]['a0']; return np.array([np.sin(a), -np.cos(a), 0.0])
def tan_x(i):
    a = PLACE[i]['a0'] - PLACE[i]['th']; return np.array([np.sin(a), -np.cos(a), 0.0])

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

def arc_samples(i):
    p = PLACE[i]
    n = max(9, int(np.ceil(p['R'] * p['th'] / 1.5)) + 1)
    fr = np.arange(n) / (n - 1)
    ang = p['a0'] - p['th'] * fr
    return np.array([[p['C'][0] + p['R'] * np.cos(a), p['C'][1] + p['R'] * np.sin(a), p['Z']]
                     for a in ang])
def samples_of(ch, nseg=9):
    pts = []
    for a, b in zip(ch, ch[1:]):
        for tt in np.linspace(0, 1, nseg)[:-1]: pts.append(a + (b - a) * tt)
    pts.append(ch[-1])
    return np.array(pts)

FIXPRE = {i: samples_of([np.array(B[i][0], float), np.array(B[i][1], float), COR[i]]) for i in range(14)}
FIXTAIL = {i: samples_of([dz.stations(B, A, i)[2], dz.stations(B, A, i)[1], np.array(A[i][6], float)]) for i in range(14)}
ARC = {i: arc_samples(i) for i in range(14)}

NV = 15
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
    E = entry(i); X = exitp(i)
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
    E = entry(i); X = exitp(i)
    W = np.array([dz.fx_of(i), -14.0, 6.8])
    q1 = ORG[i] + 0.45 * (E - ORG[i]) + np.array([0., 0., 1.5])
    f1 = [_bez(ORG[i], q1, E, 1 / 3), _bez(ORG[i], q1, E, 2 / 3)]
    q2 = X + 0.5 * (PNT[i] - X) + np.array([0., 0., -1.0])
    f2 = [_bez(X, q2, PNT[i], 1 / 3), _bez(X, q2, PNT[i], 2 / 3)]
    X0[i * NV:(i + 1) * NV] = np.concatenate([W] + f1 + f2)
if os.path.exists(f'{RT16}/fans16.json'):
    _W = json.load(open(f'{RT16}/fans16.json'))
    for i in range(14):
        d = _W[str(i + 1)]
        X0[i * NV:(i + 1) * NV] = np.concatenate([d['W'], d['F1'][0], d['F1'][1], d['F2'][0], d['F2'][1]])
    print('warm start from fans16.json', flush=True)

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
    E = entry(i); X = exitp(i)
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
    for a, b, t in ((f1b, E, tan_e(i)), (X, f2a, tan_x(i))):
        uu = (b - a); uu = uu / np.linalg.norm(uu)
        phi = np.degrees(np.arccos(np.clip(float(uu @ t), -1, 1)))
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
                    uu = p[2] - c
                    loss += WC * (uu / 0.45) ** 2
                    gv = 2 * WC * uu / 0.2025 * np.array([0.0, -dc, 1.0])
                    grad[i * NV:(i + 1) * NV] += jlist[k].T @ gv
        v = x[i * NV:(i + 1) * NV]
        pen0 = build_pen(i, v)
        loss += pen0
        eps = 1e-6
        for k in range(NV):
            vp = v.copy(); vp[k] += eps
            grad[i * NV + k] += (build_pen(i, vp) - pen0) / eps
        f2b = x[i * NV + 12:i * NV + 15]
        uu = PNT[i] - f2b; L = float(np.linalg.norm(uu)); kk = -AXV
        c = float(uu @ kk) / L
        if c < 0.3:
            loss += 6.0 * ((0.3 - c) / 0.2) ** 2
            dcdu = kk / L - (uu @ kk) * uu / L ** 3
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
    tree = cKDTree(allp)
    for a, b in tree.query_pairs(2.2):
        if own[a] == own[b] or (kind[a] == 2 and kind[b] == 2): continue
        d = float(np.linalg.norm(allp[a] - allp[b]))
        if d < ww_[0]: ww_ = (d, (int(own[a]) + 1, int(own[b]) + 1, np.round(allp[a], 1)))
    print(label, 'min body', round(float(wb_[0]), 3), wb_[1], '| min WW', round(float(ww_[0]), 3), ww_[1],
          '| max build pen', round(float(max(build_pen(i, x[i * NV:(i + 1) * NV]) for i in range(14))), 2), flush=True)
    return wb_, ww_

def path_len(pts):
    return rounded(split_corners(pts)).length
def lossf(phi):
    return 10.0 * np.tan(phi / 2) - 5.0 * phi
def chains(i, sol):
    """sol[i] = (W, F1, F2). Returns pre, M, post, E, X."""
    W, F1, F2 = sol[i]
    ep, G, P = dz.stations(B, A, i)
    E = entry(i); M = midp(i); X = exitp(i)
    pre = [list(B[i][0]), list(B[i][1]), COR[i].tolist(), np.asarray(W, float).tolist(),
           ORG[i].tolist()] + [np.asarray(p, float).tolist() for p in F1] + [E.tolist()]
    post = [X.tolist()] + [np.asarray(p, float).tolist() for p in F2] + \
           [P.tolist(), G.tolist(), list(A[i][6])]
    return pre, M, post, E, X
def slack_true(i, sol):
    pre, M, post, E, X = chains(i, sol)
    W, F1, F2 = sol[i]
    R = PLACE[i]['R']; th = PLACE[i]['th']
    stored = path_len(pre) + R * th + path_len(post)
    arr = np.array(E) - np.array(F1[-1], float); arr = arr / np.linalg.norm(arr)
    phiE_s = np.arccos(np.clip(float(arr @ tan_e(i)), -1, 1))
    dep = np.array(F2[0], float) - np.array(X); dep = dep / np.linalg.norm(dep)
    phiX_s = np.arccos(np.clip(float(tan_x(i) @ dep), -1, 1))
    stored -= (lossf(phiE_s) + lossf(phiX_s))
    chord = float(np.linalg.norm(np.array(X) - np.array(E)))
    cd = (np.array(X) - np.array(E)) / chord
    phiE_t = np.arccos(np.clip(float(arr @ cd), -1, 1))
    phiX_t = np.arccos(np.clip(float(cd @ dep), -1, 1))
    taut = path_len(pre) + chord + path_len(post) - lossf(phiE_t) - lossf(phiX_t)
    return stored - taut, stored, taut
def solve_theta(i, sol, target=30.2):
    lo, hi = 3.55, 6.22
    old = PLACE[i]['th']
    def f(t):
        PLACE[i]['th'] = t
        return slack_true(i, sol)[0]
    flo, fhi = f(lo), f(hi)
    if not (flo < target < fhi):
        PLACE[i]['th'] = old
        return None, flo, fhi
    for _ in range(12):
        mid = (lo + hi) / 2
        if f(mid) < target: lo = mid
        else: hi = mid
    PLACE[i]['th'] = (lo + hi) / 2
    return PLACE[i]['th'], slack_true(i, sol)[0], None

def sol_of(x):
    return {i: (x[i * NV:i * NV + 3],
                [x[i * NV + 3:i * NV + 6], x[i * NV + 6:i * NV + 9]],
                [x[i * NV + 9:i * NV + 12], x[i * NV + 12:i * NV + 15]]) for i in range(14)}

def save_fans(x):
    sol = sol_of(x)
    json.dump({str(i + 1): {'W': [round(float(v), 3) for v in sol[i][0]],
                            'F1': [[round(float(v), 3) for v in p] for p in sol[i][1]],
                            'F2': [[round(float(v), 3) for v in p] for p in sol[i][2]]} for i in range(14)},
              open(f'{RT16}/fans16.json', 'w'), indent=1)
def save_place():
    json.dump({str(i + 1): [round(float(PLACE[i]['C'][0]), 4), round(float(PLACE[i]['C'][1]), 4),
                            round(float(PLACE[i]['Z']), 4), round(float(PLACE[i]['R']), 4),
                            round(float(PLACE[i]['a0']), 5), round(float(PLACE[i]['th']), 5)]
               for i in range(14)}, open(f'{RT16}/place16.json', 'w'), indent=1)

if __name__ == '__main__':
    rounds = int(sys.argv[1]) if len(sys.argv) > 1 else 2
    chunks = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    steps = int(sys.argv[3]) if len(sys.argv) > 3 else 50
    lr = float(sys.argv[4]) if len(sys.argv) > 4 else 0.08
    x = X0.copy()
    report(x, 'init')
    BNDLO = np.zeros(14 * NV); BNDHI = np.zeros(14 * NV)
    for i in range(14):
        fx = dz.fx_of(i)
        BNDLO[i * NV:(i + 1) * NV] = [fx - 0.001, -17.5, 4.8] + [0, -16, 3.4] * 4
        BNDHI[i * NV:(i + 1) * NV] = [fx + 0.001, -8.0, 10.4] + [46, 44, 21.8] * 4
    am = np.zeros(14 * NV); av = np.zeros(14 * NV); at = 0
    if os.path.exists(f'{RT16}/fans_adam_m.npy'):
        am = np.load(f'{RT16}/fans_adam_m.npy'); av = np.load(f'{RT16}/fans_adam_v.npy')
        at = int(open(f'{RT16}/fans_adam_t.txt').read())
        print('adam moments resumed, t =', at, flush=True)
    logf = open(f'{RT16}/fans_log.jsonl', 'a')
    for rnd in range(rounds):
        t = time.time()
        for chunk in range(chunks):
            fcur = None
            for step in range(steps):
                fcur, g = objective(x)
                g = np.clip(g, -3000.0, 3000.0)
                at += 1
                am = 0.9 * am + 0.1 * g; av = 0.999 * av + 0.001 * g * g
                mh = am / (1 - 0.9 ** at); vh = av / (1 - 0.999 ** at)
                x = np.clip(x - lr * mh / (np.sqrt(vh) + 1e-8), BNDLO, BNDHI)
            np.save(f'{RT16}/fans_adam_m.npy', am); np.save(f'{RT16}/fans_adam_v.npy', av)
            open(f'{RT16}/fans_adam_t.txt', 'w').write(str(at))
            wb_, ww_ = report(x, f'  r{rnd} chunk {chunk}')
            save_fans(x)
            rec = dict(round=rnd, chunk=chunk, loss=round(float(fcur), 1),
                       min_body=round(float(wb_[0]), 3), min_ww=round(float(ww_[0]), 3),
                       secs=round(time.time() - t))
            logf.write(json.dumps(rec) + '\n'); logf.flush()
            print('  rec', rec, flush=True)
        sol = sol_of(x)
        bad = []
        for i in range(14):
            th, s, bracket = solve_theta(i, sol)
            if th is None: bad.append((i + 1, [round(v, 2) for v in bracket]))
        print('theta solve: failures', bad, flush=True)
        ARC.update({i: arc_samples(i) for i in range(14)})
        save_place(); save_fans(x)
    print('saved fans16.json + place16.json (theta-solved)', flush=True)
