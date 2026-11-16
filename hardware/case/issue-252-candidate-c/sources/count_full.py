"""Full fitted gate-1 count (repaired audit standard) for a design,
optionally at a Z shift s. WW via _vol_fast (repaired), WF via plain
Common with the sample/AABB prefilter. Prints JSON."""
import json, sys, time
sys.path.insert(0, '.')
import numpy as np
import fitlib252 as C
import fitlib252h as H
import fitlib18 as F
import repair18_lib as R
import repair252 as RP

S = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
D = json.load(open(sys.argv[1]))
T0 = time.time()
if S == 0:
    bodies = C.all_bodies()
    wires, lens, failed = C.build_all(D)
else:
    bodies = H.bodies_at(S)
    wires, lens, failed = H.build_all_s(D, S)
assert not failed, failed
solids = {n: r[0] for n, r in wires.items()}
samp = {n: r[1] for n, r in wires.items()}
wb = {n: F.bounds(s) for n, s in solids.items()}
bb = {p: {n: F.bounds(s) for n, s in bl} for p, bl in bodies.items()}
names = list(solids)
ww = {}
for a in range(len(names)):
    for b in range(a + 1, len(names)):
        na, nb = names[a], names[b]
        v = RP.SegRepair._vol_fast(solids[na], solids[nb], wb[na], wb[nb], samp[na], samp[nb])
        if v > F.HIT: ww[f'{na}x{nb}'] = round(v, 3)
wf = {}
for p in (17, 16):
    d = {}
    for wn, w in solids.items():
        for bn, bs in bodies[p]:
            dmin, h = RP.SegRepair._near(samp[wn], bb[p][bn])
            if dmin > 1.0 + h / 2 * 1.05 + 0.05: continue
            v = R.vol_pair(w, bs, wb[wn], bb[p][bn])
            if v > F.HIT: d[f'{wn}x{bn}'] = round(v, 3)
    wf[str(p)] = d
out = {'s': S, 'ww_count': len(ww), 'wf_17': len(wf['17']), 'wf_16': len(wf['16']),
       'gate1_17': len(ww) + len(wf['17']), 'gate1_16': len(ww) + len(wf['16']),
       'ww': ww, 'wf': wf, 'lens': lens,
       'longest_seg': max(lens.values()), 'elapsed_s': round(time.time() - T0, 1)}
print(json.dumps({k: out[k] for k in ('s', 'ww_count', 'wf_17', 'wf_16', 'gate1_17', 'gate1_16', 'longest_seg', 'elapsed_s')}))
json.dump(out, open(f'full_count_s{S}.json', 'w'), indent=1)
