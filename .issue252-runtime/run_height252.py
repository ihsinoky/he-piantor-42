import json, sys, time
sys.path.insert(0, '.')
import fitlib252 as C
import fitlib252h as H
import repair252 as RP

S = float(sys.argv[1])            # Z shift (plate_top - 13.55)
SRC = sys.argv[2] if len(sys.argv) > 2 else 'design_state.json'
T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

_orig = C.seg_points
C.seg_points = lambda D, i, side: H.seg_points_s(D, i, side, S)
D = json.load(open(SRC))
bodies = H.bodies_at(S)
rp = RP.SegRepair(D, bodies)
log(f'height shift {S}: initial locals:',
    {f'{s_}{i + 1}': rp.locals[(s_, i)] for s_ in ('SegW', 'SegM') for i in range(14)})
for p in (1, 2):
    traj = rp.run_pass(budget_s=900, eval_cap=40, log=lambda *a, **kw: log(*a))
    json.dump(rp.D, open(f'design_state_h{S}.json', 'w'), indent=1)
    log(f'pass {p} done; locals:',
        {f'{s_}{i + 1}': rp.locals[(s_, i)] for s_ in ('SegW', 'SegM') for i in range(14)})
log('DONE')
