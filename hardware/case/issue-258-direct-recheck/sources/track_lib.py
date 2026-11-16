"""Issue #258 shared harness machinery: frontier pipeline with
per-track body/route modifications. Import AFTER inserting the
phaseb + frontier paths (drivers do that)."""
import json, sys, time
import numpy as np

PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, PB)
sys.path.insert(0, f'{PB}/sources/round18')
sys.path.insert(0, f'{PB}/sources/frontier')
import fitlibF as FF
import frontier_lib as FL
import fitlib18 as F
import routes_round17 as rr
import design_r14 as d14

SEED = json.load(open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/frontier/seed_r18.json'))


def score_and_repair(M, bodies, log, npass=2):
    sc0 = FL.full_score(M, bodies)
    log('seed score', {k: sc0.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum', 'failed')})
    rep = FL.Repair(M, bodies)
    traj = []
    for pno in range(npass):
        traj += [{'pass': pno, **t} for t in rep.run_pass(budget_s=900, eval_cap=40, log=log)]
        M = rep.M
        sc = FL.full_score(M, bodies)
        log('after pass', pno, {k: sc.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'longest')})
    taut = FL.full_score(M, bodies)
    log('taut final', {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')})
    return M, sc0, taut, traj


def slack_and_partA(M, bodies, log, partA_fn):
    rec, stored_wires = FL.slack_build(M, bodies, target=30.2, budget_s=900, log=log)
    sc = FF.Scorer(stored_wires, bodies)
    ww, wf = sc.full()
    stored = {'ww_count': len(ww), 'wf_17': len(wf[17]), 'wf_16': len(wf[16]),
              'gate1_17': len(ww) + len(wf[17]), 'gate1_16': len(ww) + len(wf[16])}
    log('stored score', stored)
    partA = partA_fn(M, rec)
    log('partA min s_max', min(v['s_max'] for v in partA.values()))
    deltas = sorted(r['delta_right'] for r in rec.values())
    slack = {'delta_min': deltas[0], 'delta_median': deltas[len(deltas) // 2],
             'delta_max': deltas[-1],
             'per_strand': {k: rec[k]['delta_right'] for k in rec},
             'stored_score': stored}
    return rec, slack, partA


def partA_baseline(M, rec):
    return FL.extraction_partA(M, rec)


def _state_points_x(M, i, direction, dh, dc, s):
    """FL._state_points variant: outlet extraction shift along -X
    (N3 mating axis, right frame; left mirrors to +X)."""
    pts = FF.points_of(M, i, 'right')
    B0, B1, COR, RISE = [np.array(p, float) for p in pts[:4]]
    rest = pts[4:]
    B0 = B0 + np.array([-s, 0., 0.]); B1 = B1 + np.array([-s, 0., 0.])
    t_in = FL._unit(COR - B1); t_out = FL._unit(RISE - COR)
    if direction == 'U':
        n = np.array([0., 0., 1.]); n2 = n
    elif direction == 'D':
        n = np.array([0., 0., -1.]); n2 = n
    elif direction == 'TAUT':
        n = np.zeros(3); n2 = n
    else:
        n = FL._perp_h(t_in, direction); n2 = FL._perp_h(t_out, direction)
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


def partA_n3(M, rec):
    out = {}
    for k, r in rec.items():
        i = int(k) - 1
        dr = r['dir']; dh0, dc = r['d']
        L_st = r['len_right']
        def plen(dh_, s_):
            try:
                w, L = FF.build_wire(_state_points_x(M, i, dr, dh_, dc, s_))
            except Exception:
                return None
            return None if w is None else L
        L60 = plen(0.0, 6.0)
        shortfall = None if L60 is None else round(max(0.0, L60 - L_st), 2)
        def feas(s_):
            L = plen(0.0, s_)
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
        out[k] = {'dir': dr, 'delta': r['delta_right'], 's_max': s_max,
                  'shortfall_at_6mm': shortfall}
    return out
