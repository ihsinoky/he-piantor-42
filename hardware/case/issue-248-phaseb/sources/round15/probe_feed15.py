"""Fitted probe of the round-15 exact-optimised TAUT candidate
(feed_exact.json M points on the design_r15 skeleton), both pitches:
wire-wire Common volumes (all pairs) and wire-fixed (assembly fixed
bodies). Writes RT15/feed_probe15.json."""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
import design_r14 as dz
import design_r15 as dz15
import routes_round14 as rr

RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
dz.rise_top = lambda B, A, i: dz15.rise_top(i)
dz.corridor = dz15.corridor
rr.TAUT = json.load(open(f'{RT15}/feed_exact.json'))

def aabb_overlap(a, b):
    ba, bb = a.bounding_box(), b.bounding_box()
    return all(min(getattr(ba.max, k), getattr(bb.max, k)) -
               max(getattr(ba.min, k), getattr(bb.min, k)) > 0 for k in 'XYZ')

wires = {}; lens = {}
for sgn, side in ((1, 'right'), (-1, 'left')):
    built = rr.build_side(sgn, 'taut')
    for pin, rec in built.items():
        name = f'Wire-{side}-{pin:02d}'
        wires[name] = rec['solid']; lens[name] = round(rec['length'] + 7.3, 3)
print('built wires:', len(wires), 'longest finished:', max(lens.values()), flush=True)
names = sorted(wires)
ww = {}
for a_i in range(len(names)):
    for b_i in range(a_i + 1, len(names)):
        a, b = names[a_i], names[b_i]
        if not aabb_overlap(wires[a], wires[b]): continue
        v = volume(wires[a], wires[b])
        if v > 1e-6: ww[f'{a}x{b}'] = round(v, 4)
print('WW hits:', ww, flush=True)
out = dict(wire_wire=ww, finished_lengths=lens)
for pitch in (17, 16):
    idx, raw = cached(pitch)
    fixed = {n: s for n, k, s in raw if not n.startswith('Wire')}
    wf = {}
    for wn, w in wires.items():
        for fn, f in fixed.items():
            if not aabb_overlap(w, f): continue
            v = volume(w, f)
            if v > 1e-6: wf.setdefault(wn, {})[fn] = round(v, 4)
    out[f'wire_fixed_{pitch}'] = wf
    tot = sum(sum(d.values()) for d in wf.values())
    print(pitch, 'wire-fixed: wires with hits', len(wf), 'total vol', round(tot, 2), flush=True)
    for wn, d in wf.items(): print('  ', wn, d, flush=True)
json.dump(out, open(f'{RT15}/feed_probe15.json', 'w'), indent=1)
print('saved feed_probe15.json', flush=True)
