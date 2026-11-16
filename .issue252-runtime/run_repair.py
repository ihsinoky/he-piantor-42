import json, sys, time
sys.path.insert(0, '.')
import fitlib252 as C
import repair252 as RP

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

D = json.load(open(sys.argv[1] if len(sys.argv) > 1 else 'design_seed.json'))
bodies = C.all_bodies()
rp = RP.SegRepair(D, bodies)
log('initial locals:', {f'{s_}{i + 1}': rp.locals[(s_, i)] for s_ in ('SegW', 'SegM') for i in range(14)})
for p in (1, 2):
    traj = rp.run_pass(budget_s=900, eval_cap=40, log=lambda *a, **kw: log(*a))
    json.dump(rp.D, open('design_state.json', 'w'), indent=1)
    log(f'pass {p} done; locals:', {f'{s_}{i + 1}': rp.locals[(s_, i)] for s_ in ('SegW', 'SegM') for i in range(14)})
    log('traj:', traj)
wires, lens, failed = C.build_all(rp.D)
log('build failed:', failed)
log('longest segment:', max(lens.values()) if lens else None)
json.dump({'lens': lens, 'locals': {f'{s_}{i + 1}': rp.locals[(s_, i)] for s_ in ('SegW', 'SegM') for i in range(14)}},
          open('repair_score.json', 'w'), indent=1)
log('DONE')
