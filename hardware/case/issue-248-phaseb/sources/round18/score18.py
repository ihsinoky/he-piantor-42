"""Full fitted score of a candidate M dict (default: repair_state M).
Usage: score18.py [M.json] [out.json]"""
import json, sys, time
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime'
mpath = sys.argv[1] if len(sys.argv) > 1 else f'{RT}/round18/repair_state.json'
opath = sys.argv[2] if len(sys.argv) > 2 else f'{RT}/round18/score_current.json'
raw = json.load(open(mpath))
M = raw['M'] if 'M' in raw else raw
wires, lens, failed = F.build_all(M)
print('failed', failed, 'longest', max(lens.values()) if lens else None, flush=True)
bodies = {p: F.bodies_of(p) for p in (17, 16)}
sc = F.Scorer(wires, bodies)
t0 = time.time()
ww, wf = sc.full()
out = {'failed': failed, 'lens': lens, 'ww': ww, 'wf': {str(p): wf[p] for p in wf},
       'gate1': {str(p): len(ww) + len(wf[p]) for p in wf}}
print('score', round(time.time() - t0, 1), 's', out['gate1'], 'WW', len(ww), flush=True)
json.dump(out, open(opath, 'w'), indent=1)
print('saved', opath, flush=True)
