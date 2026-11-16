import json, sys, time
sys.path.insert(0, '.')
import fitlib252 as C
T0=time.time()
def log(*a): print(round(time.time()-T0,1), *a, flush=True)
D = C.seed_design()
json.dump(D, open('design_seed.json','w'), indent=1)
bodies = C.all_bodies()
log('bodies', {p: len(b) for p,b in bodies.items()})
sc = C.full_score(D, bodies)
log('failed', sc.get('failed'))
if 'failed' not in sc:
    log({k: sc[k] for k in ('gate1_17','gate1_16','ww_count','wf_17','wf_16','longest_seg')})
    json.dump({'ww': sc['ww'], 'wf': sc['wf'], 'lens': sc['lens']}, open('seed_score.json','w'), indent=1)
log('DONE')
