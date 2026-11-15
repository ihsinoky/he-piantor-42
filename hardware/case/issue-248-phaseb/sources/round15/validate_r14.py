"""Validate the exact oracle machinery against round 14's fitted hit map.

For every wire-fixed pair in the round-14 audit (17/16 mm):
- fitted HIT  -> min signed centreline distance (oracle) must be < 0.5
- fitted zero-volume candidate or AABB-near pair -> report min distance;
  flag if < 0.48 (would contradict the fitted result).
Centreline = the round-14 taut candidate's rounded path, edges sampled
at <=0.25 mm. Also reports the 2 wire-wire pairs' centreline min distance.
"""
import sys, json
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
import routes_round14 as rr
from exact_oracle import OracleBody

def centreline_samples(pts, mirror=False):
    if mirror: pts = [[-q[0], q[1], q[2]] for q in pts]
    path = rounded(rr.split_corners(pts))
    out = []
    for e in path.edges():
        n = max(2, int(np.ceil(e.length / 0.25)) + 1)
        for k in range(n):
            out.append(tuple(e.position_at(k / (n - 1))))
    return np.array(out)

def build_wires():
    """name -> centreline samples, both sides (taut candidate)."""
    wires = {}
    for side, sgn in (('right', 1), ('left', -1)):
        for pin in range(1, 15):
            jj = (pin - 1) if sgn > 0 else (14 - pin)
            pts = rr.points(jj, 'taut')
            wires[f'Wire-{side}-{pin:02d}'] = centreline_samples(pts, mirror=(sgn < 0))
    return wires

WIRES = build_wires()
print('wires built', flush=True)

def min_dist_to_body(samples, ob, inflate=2.0):
    lo = ob.lo - inflate; hi = ob.hi + inflate
    m = np.all(samples >= lo, axis=1) & np.all(samples <= hi, axis=1)
    sel = samples[m]
    if len(sel) == 0: return None
    return min(ob.dist(p)[0] for p in sel)

report = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    fixed = {n: s for n, k, s in raw if not n.startswith('Wire')}
    audit = read(HERE / f'{pitch}mm/audit.json')
    names = [r['name'] for r in idx]
    oracles = {}
    def oracle(name):
        if name not in oracles: oracles[name] = OracleBody(name, fixed[name])
        return oracles[name]
    hits = [h for h in audit['unexpected_interferences']
            if h['a'].startswith('Wire') != h['b'].startswith('Wire')]
    hit_pairs = set()
    ok = 0; bad = []
    for h in hits:
        wire = h['a'] if h['a'].startswith('Wire') else h['b']
        body = h['b'] if wire == h['a'] else h['a']
        hit_pairs.add((wire, body))
        d = min_dist_to_body(WIRES[wire], oracle(body))
        if d is not None and d < 0.5: ok += 1
        else: bad.append((wire, body, d))
    print(pitch, 'fitted hits', len(hits), 'reproduced (d<0.5):', ok, 'missed:', bad, flush=True)
    # near non-hit pairs from exact_results with zero volume
    flags = []
    checked = 0
    for r in audit['exact_results']:
        a, b = names[r['i']], names[r['j']]
        if a.startswith('Wire') == b.startswith('Wire'): continue
        if r.get('volume_mm3', 0) > 1e-6: continue
        wire = a if a.startswith('Wire') else b
        body = b if wire == a else a
        if (wire, body) in hit_pairs: continue
        d = min_dist_to_body(WIRES[wire], oracle(body))
        if d is None: continue
        checked += 1
        if d < 0.48: flags.append((wire, body, round(float(d), 3)))
    print(pitch, 'zero-volume candidates checked:', checked, 'flagged (d<0.48):', flags, flush=True)
    # the 2 wire-wire crossings: centreline min distance
    from scipy.spatial import cKDTree
    ww = {}
    for w1, w2 in (('Wire-left-04', 'Wire-left-05'), ('Wire-right-10', 'Wire-right-11')):
        t = cKDTree(WIRES[w2])
        d, _ = t.query(WIRES[w1])
        ww[f'{w1}x{w2}'] = round(float(d.min()), 3)
    print(pitch, 'wire-wire centreline min distances:', ww, flush=True)
    report[str(pitch)] = dict(hits=len(hits), reproduced=ok, missed=[list(map(str, b)) for b in bad],
                             near_checked=checked, near_flagged=flags, ww=ww)
json.dump(report, open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15/validate_r14.json', 'w'), indent=1)
print('saved validate_r14.json', flush=True)
