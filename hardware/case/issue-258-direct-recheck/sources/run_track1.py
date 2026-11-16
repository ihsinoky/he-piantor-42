"""Track 1: N3 bay-facing J_WING harness at plate Z13.55.
- rr.B outlet/dress replaced by N3 exits (case-frame rotation about
  O_case=(27,-41) of the Rev.4 exits; left follows the machinery
  mirror = round-4 verified convention, pin 14-i <-> 14-i).
- J_WING fitted reservations rotated rigidly about O_case Z axis.
- Seed: round-18 M (s=0). Budget: 2 repair passes 900s/40, slack 900s."""
import json, sys, time
import numpy as np
RT = '/home/hatch/workspace/projects/he-piantor-direct/.issue258-runtime'
sys.path.insert(0, RT)
import track_lib as TL
FF, FL, F, rr = TL.FF, TL.FL, TL.F, TL.rr

T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

# ---- N3 outlet points ----
exits = json.load(open(f'{RT}/n3_exits.json'))['17mm-right']['exits_new']
B = [[list(p) for p in strand] for strand in rr.B]
for i in range(14):
    x, y = exits[i]
    B[i][0] = [x, y, 5.75]
    B[i][1] = [x - 6.0, y, 5.75]
rr.B = B
FF._B0 = [[list(p) for p in strand] for strand in B]
FF.set_height(0)
log('N3 outlets installed; exit0', B[0][0], 'exit13', B[13][0])

# ---- bodies with rotated J_WING ----
from build123d import Axis
def rot_jwing(solid, cx, ang):
    return solid.rotate(Axis((cx, -41.0, 0.0), (0, 0, 1)), ang)

bodies = {}
for p in (17, 16):
    out = []
    for n, s in FF.bodies_at(p, 0):
        if n == 'underside-right-J_WING':
            s2 = rot_jwing(s, 27.0, 90.0)
            log(p, 'J_WING right rotated bounds', [[round(c, 2) for c in pt] for pt in F.bounds(s2)])
            out.append((n, s2))
        elif n == 'underside-left-J_WING':
            s2 = rot_jwing(s, -27.0, -90.0)
            out.append((n, s2))
        else:
            out.append((n, s))
    bodies[p] = out
log('bodies built')

M = TL.SEED['M']
M, sc0, taut, traj = TL.score_and_repair(M, bodies, log)
json.dump({'M': M}, open(f'{RT}/state_track1.json', 'w'), indent=1)
rec, slack, partA = TL.slack_and_partA(M, bodies, log, TL.partA_n3)
result = {'track': 1, 'plate_z': 13.55,
          'seed_score': {k: sc0.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')},
          'repair_traj': traj,
          'taut': {k: taut.get(k) for k in ('gate1_17', 'gate1_16', 'ww_count', 'wf_17', 'wf_16', 'longest', 'vol_sum')},
          'taut_ww': taut.get('ww'), 'taut_wf': taut.get('wf'),
          'slack': slack, 'gate3_partA': partA,
          'elapsed_s': round(time.time() - T0, 1)}
json.dump(result, open(f'{RT}/result_track1.json', 'w'), indent=1)
log('DONE track1')
