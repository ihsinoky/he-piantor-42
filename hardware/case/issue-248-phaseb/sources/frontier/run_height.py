"""Frontier sweep driver for one deck height.
Usage: run_height.py <plate_z> <seed_json> <tag>
seed_json: {'s': seed_shift, 'M': {...}} (round-18 M has s=0).
Writes .issue248-runtime/frontier/result_<tag>.json and
state_<tag>.json (final M at this height, for warm-start chaining).
Uniform budget: 2 seed candidates scored; 2 repair passes
(900 s / 40 evals per design); slack build 900 s; full audits."""
import json, sys, time
import numpy as np
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/frontier'
sys.path.insert(0, PB); sys.path.insert(0, f'{PB}/sources/frontier')
import fitlibF as FF
import frontier_lib as FL

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

plate_z = float(sys.argv[1]); seed_p = sys.argv[2]; tag = sys.argv[3]
s = round(plate_z - 13.55, 3)
seed = json.load(open(seed_p))
M_seed = FF.shift_M(seed['M'], s - seed['s'])
FF.set_height(s)
log('height plate', plate_z, 's', s)
bodies = {p: FF.bodies_at(p, s) for p in (17, 16)}
log('bodies built')

def lower_fan(M, drop):
    M2 = json.loads(json.dumps(M))
    for k, v in M2.items():
        for kk in v:
            v[kk] = [v[kk][0], v[kk][1], max(4.2, v[kk][2] - drop)]
    return M2

cands = {'shift': M_seed}
if s > 0.3:
    cands['lowered'] = lower_fan(M_seed, min(3.0, s))
seed_scores = {}
best = None
for name, Mc in cands.items():
    sc = FL.full_score(Mc, bodies)
    seed_scores[name] = {k: sc.get(k) for k in
                         ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16',
                          'longest', 'vol_sum', 'failed')}
    log('seed', name, seed_scores[name])
    key = (sc.get('gate1_17', 999) + sc.get('gate1_16', 999), sc.get('vol_sum', 1e9))
    if best is None or key < best[0]:
        best = (key, Mc)
M = best[1]
log('seed chosen, gate1 sum', best[0][0])

rep = FL.Repair(M, bodies)
traj_all = []
for pno in range(2):
    traj = rep.run_pass(budget_s=900, eval_cap=40, log=log)
    traj_all += [{'pass': pno, **t} for t in traj]
    M = rep.M
    json.dump({'s': s, 'M': M}, open(f'{RT}/state_{tag}.json', 'w'), indent=1)
    sc = FL.full_score(M, bodies)
    log('after pass', pno, {k: sc.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'longest')})
taut = FL.full_score(M, bodies)
log('taut final', {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')})

rec, stored_wires = FL.slack_build(M, bodies, target=30.2, budget_s=900, log=log)
json.dump({'M': M, 'strands': rec}, open(f'{RT}/stored_{tag}.json', 'w'), indent=1)
# stored full audit
wires2, lens2 = {}, {}
for nm, w in stored_wires.items():
    wires2[nm] = w
lens2 = {}
for k, r in rec.items():
    lens2[f'Wire-right-{int(k):02d}'] = r['finished_right']
    lens2[f'Wire-left-{int(k):02d}'] = r['finished_right']
sc_st = FF.Scorer(wires2, bodies)
ww_st, wf_st = sc_st.full()
stored_score = {'ww_count': len(ww_st), 'wf_17': len(wf_st[17]), 'wf_16': len(wf_st[16]),
                'gate1_17': len(ww_st) + len(wf_st[17]), 'gate1_16': len(ww_st) + len(wf_st[16]),
                'longest': max(lens2.values())}
log('stored score', stored_score)
partA = FL.extraction_partA(M, rec)
log('partA min s_max', min(v['s_max'] for v in partA.values()))
deltas = sorted(r['delta_right'] for r in rec.values())
result = {'plate_z': plate_z, 's': s, 'B': round(7.35 + s, 2),
          'plateau_z': round(plate_z + 11.10, 2),
          'seed_scores': seed_scores, 'repair_traj': traj_all,
          'taut': {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')},
          'taut_ww': taut.get('ww'), 'taut_wf': taut.get('wf'),
          'slack': {'delta_min': deltas[0], 'delta_median': deltas[len(deltas) // 2],
                    'delta_max': deltas[-1], 'per_strand': {k: rec[k]['delta_right'] for k in rec},
                    'stored_score': stored_score},
          'gate3_partA': partA,
          'elapsed_s': round(time.time() - T0, 1)}
json.dump(result, open(f'{RT}/result_{tag}.json', 'w'), indent=1)
log('DONE', tag)
