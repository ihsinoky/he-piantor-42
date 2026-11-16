"""Track 2: thinned GH stack (plate 12.95) x direct round-9 route.
Stack: floor top 2.00->1.60 (fuse band -0.40..-0.60 for tray-class),
stack bodies -0.60, floor-anchored hardware -0.40, corridor Z 5.10->
4.70 (channel is floor-anchored), stations/rise -0.60 via set_height.
Seed: round-18 M shifted -0.60. Budget: 2 repair passes 900s/40,
slack 900s (frontier-uniform)."""
import json, sys, time
import numpy as np
RT = '/home/hatch/workspace/projects/he-piantor-direct/.issue258-runtime'
sys.path.insert(0, RT)
import track_lib as TL
FF, FL, F, rr, d14 = TL.FF, TL.FL, TL.F, TL.rr, TL.d14

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

S_STACK = -0.60
S_FLOOR = -0.40
FF.set_height(S_STACK)
d14.corridor = lambda i: np.array([d14.fx_of(i), -18.0, 5.1 + S_FLOOR])
log('height set', S_STACK, 'corridor z', 5.1 + S_FLOOR)

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
            if b[0][2] >= 1.0:  # floor-top-anchored hardware follows floor
                out.append((n, solid.translate((0, 0, S_FLOOR))))
            else:               # rubber feet etc. under the case bottom
                out.append((n, solid))
        else:
            out.append((n, solid))
    return out

bodies = {p: bodies_t2(p) for p in (17, 16)}
log('bodies built')
for probe in ('underside-right-J_WING', 'wing_right', 'tray-right'):
    for n, s in bodies[17]:
        if n == probe:
            log('probe', probe, [[round(c, 2) for c in pt] for pt in F.bounds(s)])

M = FF.shift_M(TL.SEED['M'], S_STACK)
M, sc0, taut, traj = TL.score_and_repair(M, bodies, log)
json.dump({'M': M}, open(f'{RT}/state_track2.json', 'w'), indent=1)
rec, slack, partA = TL.slack_and_partA(M, bodies, log, TL.partA_baseline)
result = {'track': 2, 'plate_z': 12.95, 'B': 6.75, 'floor_top': 1.60,
          'keytop_provisional': 24.05,
          'seed_score': {k: sc0.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')},
          'repair_traj': traj,
          'taut': {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')},
          'taut_ww': taut.get('ww'), 'taut_wf': taut.get('wf'),
          'slack': slack, 'gate3_partA': partA,
          'elapsed_s': round(time.time() - T0, 1)}
json.dump(result, open(f'{RT}/result_track2.json', 'w'), indent=1)
log('DONE track2')
