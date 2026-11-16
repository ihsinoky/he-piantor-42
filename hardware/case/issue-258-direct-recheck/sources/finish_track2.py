"""Finish Track 2 from state_track2.json (post-repair M): slack build,
stored audit, Part A. Bodies identical to run_track2.py."""
import json, sys, time
import numpy as np
RT = '/home/hatch/workspace/projects/he-piantor-direct/.issue258-runtime'
sys.path.insert(0, RT)
import track_lib as TL
FF, FL, F, d14 = TL.FF, TL.FL, TL.F, TL.d14

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

S_STACK, S_FLOOR = -0.60, -0.40
FF.set_height(S_STACK)
d14.corridor = lambda i: np.array([d14.fx_of(i), -18.0, 5.1 + S_FLOOR])

def bodies_t2(pitch):
    out = []
    for n, solid in F.bodies_of(pitch):
        c = FF.classify(n)
        if c == 'shift':
            out.append((n, solid.translate((0, 0, S_STACK))))
        elif c == 'extend':
            out.append((n, solid.translate((0, 0, S_STACK)).fuse(
                solid.translate((0, 0, S_FLOOR)))))
        elif c == 'fixed':
            b = F.bounds(solid)
            if b[0][2] >= 1.0:
                out.append((n, solid.translate((0, 0, S_FLOOR))))
            else:
                out.append((n, solid))
        else:
            out.append((n, solid))
    return out

bodies = {p: bodies_t2(p) for p in (17, 16)}
log('bodies built')
M = json.load(open(f'{RT}/state_track2.json'))['M']
taut = FL.full_score(M, bodies)
log('taut recheck', {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')})
rec, slack, partA = TL.slack_and_partA(M, bodies, log, TL.partA_baseline)
result = {'track': 2, 'plate_z': 12.95, 'B': 6.75, 'floor_top': 1.60,
          'keytop_provisional': 24.05,
          'taut': {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')},
          'taut_ww': taut.get('ww'), 'taut_wf': taut.get('wf'),
          'slack': slack, 'gate3_partA': partA,
          'note': 'seed/repair numbers from track2.log (killed at 3590s during slack record build); slack/partA from this finish run on the same saved M',
          'elapsed_s': round(time.time() - T0, 1)}
json.dump(result, open(f'{RT}/result_track2.json', 'w'), indent=1)
log('DONE finish track2')
