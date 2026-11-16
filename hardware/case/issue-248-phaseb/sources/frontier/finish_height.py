"""Finish a height whose repair completed but whose process died
during slack/audit: taut score + slack + stored audit + Part A.
Usage: finish_height.py <plate_z> <state_json> <tag>"""
import json, sys, time
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/frontier'
sys.path.insert(0, PB); sys.path.insert(0, f'{PB}/sources/frontier')
import fitlibF as FF
import frontier_lib as FL

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

plate_z = float(sys.argv[1]); state_p = sys.argv[2]; tag = sys.argv[3]
s = round(plate_z - 13.55, 3)
st = json.load(open(state_p))
assert abs(st['s'] - s) < 1e-6, (st['s'], s)
M = st['M']
FF.set_height(s)
bodies = {p: FF.bodies_at(p, s) for p in (17, 16)}
taut = FL.full_score(M, bodies)
log('taut', {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')})
rec, stored_wires = FL.slack_build(M, bodies, target=30.2, budget_s=1200, log=log)
json.dump({'M': M, 'strands': rec}, open(f'{RT}/stored_{tag}.json', 'w'), indent=1)
lens2 = {}
for k, r in rec.items():
    lens2[f'Wire-right-{int(k):02d}'] = r['finished_right']
    lens2[f'Wire-left-{int(k):02d}'] = r['finished_right']
sc_st = FF.Scorer(stored_wires, bodies)
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
          'resumed_from_state': state_p,
          'taut': {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')},
          'taut_ww': taut.get('ww'), 'taut_wf': taut.get('wf'),
          'slack': {'delta_min': deltas[0], 'delta_median': deltas[len(deltas) // 2],
                    'delta_max': deltas[-1], 'per_strand': {k: rec[k]['delta_right'] for k in rec},
                    'stored_score': stored_score},
          'gate3_partA': partA,
          'elapsed_s': round(time.time() - T0, 1)}
json.dump(result, open(f'{RT}/result_{tag}.json', 'w'), indent=1)
log('DONE', tag)
