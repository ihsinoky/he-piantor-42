"""Round 16 feed optimisation: CURRICULUM over body sets + hinge-weight continuation, warm-started, state persisted in RT16.

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
RT16 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round16'
import os as _os
_os.makedirs(RT16, exist_ok=True)
import argparse
_ap = argparse.ArgumentParser()
_ap.add_argument('--stage', type=int, default=3)
_ap.add_argument('--init', default='state')   # taut14 | state | geom | exact15
_ap.add_argument('--chunks', type=int, default=4)
_ap.add_argument('--iters', type=int, default=25)
_ap.add_argument('--wmul', type=float, default=1.0)
_ap.add_argument('--wmulw', type=float, default=None)
_ap.add_argument('--trimul', type=float, default=1.0)
_ap.add_argument('--seed', type=int, default=16)
_ap.add_argument('--solver', default='lbfgsb')   # lbfgsb | adam
_ap.add_argument('--steps', type=int, default=50)  # adam steps per chunk
_ap.add_argument('--lr', type=float, default=0.08)
ARGS = _ap.parse_args()

def _stage_ok(name):
    if ARGS.stage >= 3: return True
    if name.startswith('switch-envelope') or name in ('wing_right', 'wing_left') \
       or name.startswith('plate-'): return True
    if ARGS.stage == 1: return False
    return name.startswith('tray-') or name.startswith('underside-') or name.startswith('POM-')

D = json.load(open(f'{HERE}/routes-round9.json')); B, A = D['before'], D['after']
TAUT14 = json.load(open(f'{RT14}/taut_opt.json'))

ROUTE_BOX_LO = np.array([-6., -22., 2.]); ROUTE_BOX_HI = np.array([48., 46., 24.])
OBST = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    for n, k, s in raw:
        if n.startswith('Wire'): continue
        if not _stage_ok(n): continue
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
def _load_M(path):
    _W = json.load(open(path))
    for j in range(14):
        X0[j * 6:j * 6 + 3] = _W[str(j + 1)]['M1']; X0[j * 6 + 3:j * 6 + 6] = _W[str(j + 1)]['M2']
if ARGS.init == 'taut14':
    for j in range(14):
        X0[j * 6:j * 6 + 3] = TAUT14[str(j + 1)]['M1']; X0[j * 6 + 3:j * 6 + 6] = TAUT14[str(j + 1)]['M2']
    print('init: round14 taut_opt (WW-2 feed)', flush=True)
elif ARGS.init == 'exact15':
    _load_M(f'{RT15}/feed_exact.json'); print('init: round15 feed_exact', flush=True)
elif ARGS.init == 'state':
    if os.path.exists(f'{RT16}/feed_state.json'):
        _load_M(f'{RT16}/feed_state.json'); print('init: RT16 feed_state', flush=True)
    elif os.path.exists(f'{RT15}/feed_exact.json'):
        _load_M(f'{RT15}/feed_exact.json'); print('init: round15 feed_exact (no RT16 state)', flush=True)
print('init mode:', ARGS.init, flush=True)


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

SEG_N = {}
for _i in range(14):
    _ch = [ORG[_i], X0[_i * 6:_i * 6 + 3], X0[_i * 6 + 3:_i * 6 + 6], TGT[_i]]
    SEG_N[_i] = [max(NSEG, int(np.ceil(float(np.linalg.norm(_ch[_s + 1] - _ch[_s])) / 1.5))) for _s in range(3)]

def var_samples(x, i):
    m1 = x[i * 6:i * 6 + 3]; m2 = x[i * 6 + 3:i * 6 + 6]
    chain = [ORG[i], m1, m2, TGT[i]]
    pts = []; Js = []
    for s in range(3):
        a, b = chain[s], chain[s + 1]
        ns = SEG_N[i][s]   # FIXED counts: length-dependent counts made the objective discontinuous (sample birth/death cliffs) and broke every L-BFGS-B line search
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
    """SMOOTH R5 buildability penalty (round-16 fix): per-corner
    fillet tangent length t = R*tan(deflection/2) on the chain
    [corridor, ORG, M1, M2, P, G, ep]; each straight must cover its
    two end trims + 0.3 mm buffer. Replaces the kinked/capped
    _trim15 form whose FD gradient exploded near sharp corners."""
    m1 = v[0:3]; m2 = v[3:6]
    ep, G, P = dz.stations(B, A, i)
    ch = [dz15.corridor(i), ORG[i], m1, m2, P, G, ep]
    tr = [0.0]
    for k in range(1, len(ch) - 1):
        u = ch[k] - ch[k - 1]; w = ch[k + 1] - ch[k]
        nu = float(np.linalg.norm(u)); nv = np.linalg.norm(w)
        if nu < 1e-9 or nv < 1e-9: tr.append(12.9); continue
        c = float(np.clip((u @ w) / (nu * nv), -1.0, 1.0))
        thd = min(float(np.arccos(c)), 2.4)   # deflection angle, 0 = straight
        tr.append(5.0 * float(np.tan(thd / 2.0)))
    tr.append(0.0)
    pen = 0.0
    for k in range(len(ch) - 1):
        seg = float(np.linalg.norm(ch[k + 1] - ch[k]))
        margin = seg - tr[k] - tr[k + 1]
        if margin < 0.3: pen += 50.0 * (0.3 - margin) ** 2
    return pen

OBST = {k: v for k, v in OBST.items() if _stage_ok(k[1])}
print('stage', ARGS.stage, 'bodies:', len(OBST), flush=True)

CAND = {}
for i in range(14):
    pts, _ = var_samples(X0, i)
    cand = []
    for key, ob in OBST.items():
        dlb = np.maximum(np.maximum(ob.lo - pts, pts - ob.hi), 0.0)
        if float(np.min(np.sum(dlb * dlb, axis=1))) < 3.5 ** 2: cand.append(key)
    CAND[i] = cand
print('cand per strand:', [len(CAND[i]) for i in range(14)], flush=True)


_TAU = 0.08
def body_dist_grad(ob, p, cap):
    """Soft-min signed distance over the body's two closest faces
    (round-16 fix): the exact distance is non-differentiable on
    medial surfaces (e.g. mid-plane of a plate), where the returned
    witness flips and the analytic gradient points the wrong way -
    this broke every L-BFGS-B line search. Soft-min over faces
    (tau=0.08) is smooth, and conservative (underestimates the
    clearance by <= tau*ln2 = 0.055 mm). Returns (d, grad_d) with
    d >= cap signalled as (cap, None)."""
    from OCP.BRepClass3d import BRepClass3d_SolidClassifier
    from OCP.gp import gp_Pnt
    from OCP.TopAbs import TopAbs_IN
    p = np.asarray(p, float)
    lbn = np.maximum(np.maximum(ob._flo - p, p - ob._fhi), 0.0)
    lb = np.sqrt(np.sum(lbn * lbn, axis=1))
    cand = [k for k in np.argsort(lb) if lb[k] < cap + 0.5]
    if not cand: return cap, None
    ds = []
    for k in cand:
        d, q = ob.faces[k].dist(p)
        ds.append((float(d), q))
        if len(ds) >= 6: break
    ds.sort(key=lambda t: t[0])
    d1, q1 = ds[0]
    if d1 >= cap + 0.5: return cap, None
    if len(ds) > 1 and ds[1][0] < d1 + 6 * _TAU:
        d2, q2 = ds[1]
        e1 = np.exp(-d1 / _TAU); e2 = np.exp(-d2 / _TAU)
        U = -_TAU * np.log(e1 + e2)
        w1 = e1 / (e1 + e2); w2 = e2 / (e1 + e2)
        gU = np.zeros(3)
        for (dd, qq, ww) in ((d1, q1, w1), (d2, q2, w2)):
            if dd > 1e-7 and qq is not None:
                gU += ww * (p - qq) / dd
    else:
        U = d1
        gU = (p - q1) / d1 if d1 > 1e-7 and q1 is not None else np.zeros(3)
    if U >= cap: return cap, None
    if U <= 1e-12: return 0.0, gU
    if np.all(p >= ob.lo) and np.all(p <= ob.hi):
        if ob._cls is None:
            ob._cls = BRepClass3d_SolidClassifier(ob.shape.wrapped)
        ob._cls.Perform(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), 1e-7)
        if ob._cls.State() == TopAbs_IN:
            return -U, -gU
    return U, gU

HB, WB = 1.15, 30.0 * ARGS.wmul
HW, WW = 1.35, 3.0 * (ARGS.wmul if ARGS.wmulw is None else ARGS.wmulw)
WC = 2.0

def ceiling(y):
    if y < 1.935593: return 21.65, 0.0
    t = min(max((y - 1.935593) / 36.578838, 0), 1)
    return 21.65 - 11.10 * t, (-11.10 / 36.578838 if t < 1 else 0.0)

STATS = {}
def objective(x):
    loss = 0.0; grad = np.zeros(84)
    _st = dict(ww=0.0, body=0.0, ceil=0.0, appr=0.0, seg=0.0, trim=0.0,
               n_body_viol=0, worst_body=(9, None), n_ww_viol=0, worst_ww=(9, None))
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
        _st['ww'] += WW * ((HW - d) / 0.3) ** 2; _st['n_ww_viol'] += 1
        if d < _st['worst_ww'][0]: _st['worst_ww'] = (d, (int(own[a]), int(own[b])))
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
                d, gd = body_dist_grad(ob, p, HB)
                if d < HB and gd is not None:
                    _st['body'] += WB * ((HB - d) / 0.3) ** 2; _st['n_body_viol'] += 1
                    if d < _st['worst_body'][0]: _st['worst_body'] = (d, (i, key))
                    loss += WB * ((HB - d) / 0.3) ** 2
                    gv = -2 * WB * (HB - d) / 0.09 * gd
                    grad[i * 6:i * 6 + 6] += Js[k].T @ gv
            c, dc = ceiling(p[1])
            if p[2] > c:
                u = p[2] - c
                _st['ceil'] += WC * (u / 0.3) ** 2
                loss += WC * (u / 0.3) ** 2
                gv = 2 * WC * u / 0.09 * np.array([0.0, -dc, 1.0])
                grad[i * 6:i * 6 + 6] += Js[k].T @ gv
    # approach angle + segment lengths + regularisation
    for i in range(14):
        m1 = x[i * 6:i * 6 + 3]; m2 = x[i * 6 + 3:i * 6 + 6]
        u = TGT[i] - m2; L = float(np.linalg.norm(u)); k = -AXV
        c = float(u @ k) / L
        if c < 0.3:
            _st['appr'] += 6.0 * ((0.3 - c) / 0.2) ** 2
            loss += 6.0 * ((0.3 - c) / 0.2) ** 2
            dcdu = k / L - (u @ k) * u / L ** 3
            grad[i * 6 + 3:i * 6 + 6] += (-2 * 6.0 * (0.3 - c) / 0.04) * (-dcdu)
        chain = [ORG[i], m1, m2, TGT[i]]
        for s in range(3):
            a, b = chain[s], chain[s + 1]; ab = b - a; L = float(np.linalg.norm(ab))
            if 1e-9 < L < 7.0:
                _st['seg'] += 10.0 * ((7.0 - L) / 1.5) ** 2
                loss += 10.0 * ((7.0 - L) / 1.5) ** 2
                gv = -2 * 10.0 * (7.0 - L) / 2.25 * (ab / L)  # dpen/d(end)
                if s == 0: grad[i * 6:i * 6 + 3] += gv
                elif s == 1: grad[i * 6:i * 6 + 3] += -gv; grad[i * 6 + 3:i * 6 + 6] += gv
                else: grad[i * 6 + 3:i * 6 + 6] += -gv
    for i in range(14):
        v = x[i * 6:(i + 1) * 6]
        pen0 = feed_build_pen(i, v) * ARGS.trimul
        _st['trim'] += pen0
        loss += pen0
        eps = 1e-6
        for k in range(6):
            vp = v.copy(); vp[k] += eps
            grad[i * 6 + k] += (feed_build_pen(i, vp) * ARGS.trimul - pen0) / eps
    loss += 0.001 * float(np.sum((x - X0) ** 2)); grad += 0.002 * (x - X0)
    STATS.update(_st)
    if not np.isfinite(loss): loss = 1e12
    grad = np.clip(np.nan_to_num(grad, nan=0.0, posinf=1e4, neginf=-1e4), -1e4, 1e4)
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

if __name__ == '__main__' and '--diag' in sys.argv:
    f, g = objective(X0)
    print('total', round(float(f), 1))
    for k, v in STATS.items(): print(' ', k, v if not isinstance(v, float) else round(v, 1), flush=True)
    sys.exit(0)
if __name__ == '__main__':
    rng = np.random.default_rng(ARGS.seed)
    f0, g0 = objective(X0)
    print('init loss', round(float(f0), 2), flush=True)
    report(X0, 'init')
    BND = []
    for i in range(14): BND += [(0, 46), (-10, 44), (5.6, 21.8)] * 2

    def save(x, tag):
        M = {str(i + 1): {'M1': [round(float(v), 4) for v in x[i * 6:i * 6 + 3]],
                          'M2': [round(float(v), 4) for v in x[i * 6 + 3:i * 6 + 6]]} for i in range(14)}
        json.dump(M, open(f'{RT16}/feed_state.json', 'w'), indent=1)
        np.save(f'{RT16}/feed_state.npy', x)
        json.dump(M, open(f'{RT16}/feed_state_{tag}.json', 'w'), indent=1)

    x = X0.copy(); save(x, f's{ARGS.stage}_init')
    logf = open(f'{RT16}/feed_log.jsonl', 'a')
    if ARGS.solver == 'adam':
        sig = f"{ARGS.stage}|{ARGS.wmul}|{ARGS.wmulw}"
        sigf = f'{RT16}/adam_sig.txt'
        if os.path.exists(sigf) and open(sigf).read() == sig and os.path.exists(f'{RT16}/adam_m.npy'):
            am = np.load(f'{RT16}/adam_m.npy'); av = np.load(f'{RT16}/adam_v.npy'); at = int(open(f'{RT16}/adam_t.txt').read())
            print('adam moments resumed, t =', at, flush=True)
        else:
            am = np.zeros(84); av = np.zeros(84); at = 0
            open(sigf, 'w').write(sig)
        lo = np.array([b[0] for b in BND]); hi = np.array([b[1] for b in BND])
        for chunk in range(ARGS.chunks):
            t = time.time(); fcur = None
            for step in range(ARGS.steps):
                fcur, g = objective(x)
                g = np.clip(g, -3000.0, 3000.0)
                at += 1
                am = 0.9 * am + 0.1 * g; av = 0.999 * av + 0.001 * g * g
                mh = am / (1 - 0.9 ** at); vh = av / (1 - 0.999 ** at)
                x = np.clip(x - ARGS.lr * mh / (np.sqrt(vh) + 1e-8), lo, hi)
            np.save(f'{RT16}/adam_m.npy', am); np.save(f'{RT16}/adam_v.npy', av)
            open(f'{RT16}/adam_t.txt', 'w').write(str(at))
            wb, ww2 = report(x, f'  s{ARGS.stage} adam chunk {chunk}')
            save(x, f's{ARGS.stage}_c{chunk}')
            rec = dict(stage=ARGS.stage, chunk=chunk, solver='adam', wmul=ARGS.wmul,
                       wmulw=ARGS.wmulw, loss=round(float(fcur), 1), steps=ARGS.steps,
                       min_body=round(float(wb[0]), 3), min_ww=round(float(ww2[0]), 3),
                       secs=round(time.time() - t))
            logf.write(json.dumps(rec) + '\n'); logf.flush()
            print('  rec', rec, flush=True)
        print('done stage', ARGS.stage, '(adam)', flush=True)
        sys.exit(0)
    x_best = x.copy(); f_best = float(f0)
    for chunk in range(ARGS.chunks):
        t = time.time()
        r = minimize(objective, x, jac=True, method='L-BFGS-B', bounds=BND,
                     options={'maxiter': ARGS.iters, 'ftol': 1e-11, 'maxls': 40})
        if float(r.fun) < f_best: f_best = float(r.fun); x_best = r.x.copy()
        x = r.x
        wb, ww2 = report(x, f'  s{ARGS.stage} chunk {chunk}')
        save(x_best, f's{ARGS.stage}_c{chunk}')
        x = x_best
        rec = dict(stage=ARGS.stage, chunk=chunk, wmul=ARGS.wmul, wmulw=ARGS.wmulw, loss=round(float(r.fun), 1), f_best=round(f_best, 1),
                   nit=int(r.nit), msg=str(r.message)[:40], min_body=round(float(wb[0]), 3),
                   min_ww=round(float(ww2[0]), 3), secs=round(time.time() - t))
        logf.write(json.dumps(rec) + '\n'); logf.flush()
        print('  rec', rec, flush=True)
        if r.nit == 0 or 'ABNORMAL' in str(r.message):
            x = x + rng.normal(0, 0.05, size=84)
            print('  jitter applied (stall escape)', flush=True)
    print('done stage', ARGS.stage, flush=True)
