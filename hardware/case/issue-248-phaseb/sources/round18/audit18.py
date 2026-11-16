"""Full fitted audit of an arbitrary point-list assembly (stored.json).
Usage: audit18.py <points-json> <out-json>   (points-json: stored.json
or {'M': ...} for the taut M; output: per-pitch gate-1 counts, WW, and
a body-category breakdown)."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
import repair18_lib as R

RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime'
T0 = time.time()
def log(*a): print(round(time.time() - T0, 1), *a, flush=True)

src = json.load(open(sys.argv[1]))
if 'strands' in src:
    pts = {}
    for k, rec in src['strands'].items():
        i = int(k)
        for side in ('right', 'left'):
            pts[f'Wire-{side}-{i:02d}'] = rec[f'points_{side}']
else:
    M = src['M']
    pts = {}
    for side in ('right', 'left'):
        for pin in range(1, 15):
            pts[f'Wire-{side}-{pin:02d}'] = F.points_of(M, pin - 1, side)

bodies, body_bnd = R.load_bodies()
wires, samp, wb = {}, {}, {}
for nm, p in pts.items():
    r, why = R.build_s(p)
    assert r is not None, (nm, why)
    wires[nm] = r[0]; samp[nm] = r[1]; wb[nm] = F.bounds(r[0])
log('wires built', len(wires))

# WW pairs (true, repaired) once per side; gate counts both pitches x2
ww_pairs, ww_vol = [], 0.0
names = list(wires)
for a in range(len(names)):
    for b in range(a + 1, len(names)):
        na, nb = names[a], names[b]
        if na.split('-')[1] != nb.split('-')[1]: continue
        v = R.vol_pair(wires[na], wires[nb], wb[na], wb[nb], repair=True,
                       sa=samp[na], sb=samp[nb])
        if v > F.HIT:
            ww_pairs.append([na, nb, round(v, 3)]); ww_vol += v
log('WW pairs', len(ww_pairs), 'vol', round(ww_vol, 2))

out = {'ww_pairs': ww_pairs, 'ww_count': len(ww_pairs)}
for p in (17, 16):
    cnt, vol = 0, 0.0
    cats, hits = {}, []
    for nm, w in wires.items():
        for bn, bs in bodies[p]:
            v = R.vol_pair(w, bs, wb[nm], body_bnd[p][bn])
            if v > F.HIT:
                cnt += 1; vol += v
                cat = bn.split('-')[0] if '-' in bn else bn
                cats[cat] = cats.get(cat, 0) + 1
                hits.append([nm, bn, round(v, 3)])
    gate1 = cnt + len(ww_pairs)
    out[str(p)] = {'wire_fixed': cnt, 'wf_vol': round(vol, 2),
                   'gate1': gate1, 'cats': cats}
    log(f'pitch {p}: WF {cnt} vol {vol:.1f} gate1 {gate1} (WW {len(ww_pairs)}x2)')
    out[f'{p}_hits'] = hits
json.dump(out, open(sys.argv[2], 'w'), indent=1)
log('saved', sys.argv[2])
