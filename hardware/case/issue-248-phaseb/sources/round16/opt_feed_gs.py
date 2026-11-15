"""Round 16 feed optimisation, GAUSS-SEIDEL variant.

The joint 84-var exact-oracle optimisation (rounds 15-16) stalls:
L-BFGS-B line searches fail on the kinked landscape and Adam
oscillates. Here each strand's (M1, M2) is optimised in turn
(6 vars, L-BFGS-B) against the stage body set (exact oracle) plus
ALL other strands' current chains and the fixed chains as sample
obstacles; sweeps repeat. Same objective terms, weights, hinge
targets and bounds as opt_feed_curr (imported as a module so the
stage body sets / weight continuation / warm starts are identical).
State: RT16/feed_state.json (shared with opt_feed_curr).
Usage: opt_feed_gs.py [sweeps] [iters]  with env vars GS_STAGE,
GS_INIT, GS_WMUL, GS_WMULW.
"""
import json, os, sys, time
import numpy as np
from scipy.optimize import minimize
from scipy.spatial import cKDTree

_MYARGS = sys.argv[1:]
STAGE = os.environ.get('GS_STAGE', '1')
INIT = os.environ.get('GS_INIT', 'taut14')
WMUL = os.environ.get('GS_WMUL', '1.0')
WMULW = os.environ.get('GS_WMULW', '')
sys.argv = ['opt_feed_curr.py', '--stage', STAGE, '--init', INIT, '--wmul', WMUL] + \
           (['--wmulw', WMULW] if WMULW else [])
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round16')
import opt_feed_curr as ofc

RT16 = ofc.RT16
HB, WB, HW, WW, WC = ofc.HB, ofc.WB, ofc.HW, ofc.WW, ofc.WC
ORG, TGT = ofc.ORG, ofc.TGT
FIXALL = ofc.FIXALL
BND = []
for i in range(14): BND += [(0, 46), (-10, 44), (5.6, 21.8)] * 2

def strand_objective(v, x, i, env_pts):
    """Objective terms involving strand i only; env_pts = samples of
    all other strands' variable chains + FIXALL (static this call)."""
    xf = x.copy(); xf[i * 6:(i + 1) * 6] = v
    loss = 0.0; grad = np.zeros(6)
    sp, Js = ofc.var_samples(xf, i)
    # wire-wire vs environment
    tree = cKDTree(env_pts)
    # strand-i samples vs env: ball query per sample
    idxs = tree.query_ball_point(sp, HW)
    for a, lst in enumerate(idxs):
        for b in lst:
            dvec = sp[a] - env_pts[b]; d = float(np.linalg.norm(dvec))
            if d < 1e-9: continue
            loss += WW * ((HW - d) / 0.3) ** 2
            gv = -2 * WW * (HW - d) / 0.09 * (dvec / d)
            grad += Js[a].T @ gv
    # wire-wire within strand i (var samples vs own FIX samples are in
    # env via FIXALL; var-var self pairs cannot occur on one chain at
    # these spacings, but include var vs own fixed dress/tail:)
    # (already covered: FIXALL is part of env_pts)
    # body + ceiling
    for k, p in enumerate(sp):
        for key in ofc.CAND[i]:
            ob = ofc.OBST[key]
            dlb = np.maximum(np.maximum(ob.lo - p, p - ob.hi), 0.0)
            if float(dlb @ dlb) > (HB + 0.6) ** 2: continue
            d, q = ob.dist_capped(p, HB)
            if d < HB and q is not None:
                loss += WB * ((HB - d) / 0.3) ** 2
                nrm = float(np.linalg.norm(p - q))
                if nrm > 1e-9:
                    dirv = (p - q) / nrm if d >= 0 else (q - p) / nrm
                    gv = -2 * WB * (HB - d) / 0.09 * dirv
                    grad += Js[k].T @ gv
        c, dc = ofc.ceiling(p[1])
        if p[2] > c:
            u = p[2] - c
            loss += WC * (u / 0.3) ** 2
            gv = 2 * WC * u / 0.09 * np.array([0.0, -dc, 1.0])
            grad += Js[k].T @ gv
    # approach angle + segment lengths (strand i)
    m1 = v[0:3]; m2 = v[3:6]
    u = TGT[i] - m2; L = float(np.linalg.norm(u)); kk = -ofc.AXV
    c = float(u @ kk) / L
    if c < 0.3:
        loss += 6.0 * ((0.3 - c) / 0.2) ** 2
        dcdu = kk / L - (u @ kk) * u / L ** 3
        grad[3:6] += (-2 * 6.0 * (0.3 - c) / 0.04) * (-dcdu)
    chain = [ORG[i], m1, m2, TGT[i]]
    for s in range(3):
        a, b = chain[s], chain[s + 1]; ab = b - a; L = float(np.linalg.norm(ab))
        if 1e-9 < L < 7.0:
            loss += 10.0 * ((7.0 - L) / 1.5) ** 2
            gv = -2 * 10.0 * (7.0 - L) / 2.25 * (ab / L)
            if s == 0: grad[0:3] += gv
            elif s == 1: grad[0:3] += -gv; grad[3:6] += gv
            else: grad[3:6] += -gv
    pen0 = ofc.feed_build_pen(i, v)
    loss += pen0
    eps = 1e-5
    for k in range(6):
        vp = v.copy(); vp[k] += eps
        grad[k] += (ofc.feed_build_pen(i, vp) - pen0) / eps
    loss += 0.001 * float(np.sum((v - ofc.X0[i * 6:(i + 1) * 6]) ** 2))
    grad += 0.002 * (v - ofc.X0[i * 6:(i + 1) * 6])
    if not np.isfinite(loss): loss = 1e12
    grad = np.clip(np.nan_to_num(grad, nan=0.0, posinf=1e4, neginf=-1e4), -1e4, 1e4)
    return loss, grad

def env_for(x, i):
    pts = []
    for j in range(14):
        if j == i: continue
        sp, _ = ofc.var_samples(x, j)
        pts.append(sp)
    pts.append(FIXALL[ofc.FIXOWN != i])   # joint objective skips same-owner pairs
    return np.vstack(pts)

def save(x, tag):
    M = {str(i + 1): {'M1': [round(float(v), 4) for v in x[i * 6:i * 6 + 3]],
                      'M2': [round(float(v), 4) for v in x[i * 6 + 3:i * 6 + 6]]} for i in range(14)}
    json.dump(M, open(f'{RT16}/feed_state.json', 'w'), indent=1)
    np.save(f'{RT16}/feed_state.npy', x)
    if tag: json.dump(M, open(f'{RT16}/feed_state_{tag}.json', 'w'), indent=1)

if __name__ == '__main__':
    sweeps = int(_MYARGS[0]) if len(_MYARGS) > 0 else 3
    iters = int(_MYARGS[1]) if len(_MYARGS) > 1 else 40
    x = ofc.X0.copy()
    f0, _ = ofc.objective(x)
    print('GS init joint loss', round(float(f0), 1), flush=True)
    ofc.report(x, 'init')
    logf = open(f'{RT16}/feed_log.jsonl', 'a')
    for sw in range(sweeps):
        t = time.time()
        for i in range(14):
            env = env_for(x, i)
            r = minimize(strand_objective, x[i * 6:(i + 1) * 6], args=(x, i, env),
                         jac=True, method='L-BFGS-B', bounds=BND[i * 6:(i + 1) * 6],
                         options={'maxiter': iters, 'ftol': 1e-11, 'maxls': 40})
            x[i * 6:(i + 1) * 6] = r.x
        wb, ww2 = ofc.report(x, f'  GS s{STAGE} sweep {sw}')
        save(x, f'gs{STAGE}_sw{sw}')
        rec = dict(stage=int(STAGE), solver='GS', sweep=sw, wmul=float(WMUL),
                   min_body=round(float(wb[0]), 3), min_ww=round(float(ww2[0]), 3),
                   secs=round(time.time() - t))
        logf.write(json.dumps(rec) + '\n'); logf.flush()
        print('  rec', rec, flush=True)
    f1, _ = ofc.objective(x)
    print('GS final joint loss', round(float(f1), 1), flush=True)
