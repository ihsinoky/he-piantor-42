"""Round 18 baseline: incumbent (round-14 taut) fitted score under the
repaired standard, both pitches, + per-strand local counts."""
import json, sys, time
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F

RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime'
M = json.load(open(f'{RT}/round14/taut_opt.json'))
t0 = time.time()
wires, lens, failed = F.build_all(M)
print('build', round(time.time() - t0, 1), 's; wires', len(wires), 'failed', failed, flush=True)
bodies = {p: F.bodies_of(p) for p in (17, 16)}
sc = F.Scorer(wires, bodies)
t0 = time.time()
ww, wf = sc.full()
print('full score', round(time.time() - t0, 1), 's', flush=True)
out = {'failed': failed, 'lens': lens, 'ww': ww,
       'wf': {str(p): wf[p] for p in wf}}
for p in (17, 16):
    print(p, 'WW', len(ww), 'WF', len(wf[p]), 'gate1', len(ww) + len(wf[p]), flush=True)
loc = {}
for name in wires:
    c, v = sc.local(name)
    loc[name] = [c, round(v, 3)]
out['local'] = dict(sorted(loc.items(), key=lambda kv: -kv[1][0]))
for k, v in out['local'].items(): print('local', k, v, flush=True)
json.dump(out, open(f'{RT}/round18/baseline.json', 'w'), indent=1)
print('saved baseline.json', flush=True)
