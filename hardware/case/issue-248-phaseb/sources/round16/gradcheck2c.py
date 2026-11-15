"""Per-(sample, body) FD vs analytic for the BODY term, strand 1, var 11."""
import sys
sys.argv = ['opt_feed_curr.py', '--stage', '1', '--init', 'state', '--wmul', '1.0', '--trimul', '3.0']
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round16')
import numpy as np
import opt_feed_curr as ofc

x = ofc.X0.copy(); i = 1; HB, WB = ofc.HB, ofc.WB
def pair_pen(xx, k, key):
    sp, Js = ofc.var_samples(xx, i)
    p = sp[k]; ob = ofc.OBST[key]
    dlb = np.maximum(np.maximum(ob.lo - p, p - ob.hi), 0.0)
    if float(dlb @ dlb) > (HB + 0.6) ** 2: return 0.0, 0.0
    d, q = ob.dist_capped(p, HB)
    if d < HB and q is not None:
        pen = WB * ((HB - d) / 0.3) ** 2
        nrm = float(np.linalg.norm(p - q))
        if nrm > 1e-9:
            dirv = (p - q) / nrm if d >= 0 else (q - p) / nrm
            gv = -2 * WB * (HB - d) / 0.09 * dirv
            return pen, float((Js[k].T @ gv)[5])   # var 11 = local index 5 (M2.z)
    return 0.0, 0.0

sp, _ = ofc.var_samples(x, i)
h = 1e-6
for k in range(len(sp)):
    for key in ofc.CAND[i]:
        pen0, an = pair_pen(x, k, key)
        xp = x.copy(); xp[11] += h
        pen1, _ = pair_pen(xp, k, key)
        fd = (pen1 - pen0) / h
        if abs(fd - an) > 1.0:
            d, q = ofc.OBST[key].dist_capped(sp[k], 3.0)
            print('sample', k, 'body', key[1], 'FD', round(float(fd), 1), 'analytic', round(float(an), 1),
                  'd', round(float(d), 3), 'p', np.round(sp[k], 2), 'q', np.round(q, 2) if q is not None else None, flush=True)
print('done', flush=True)
