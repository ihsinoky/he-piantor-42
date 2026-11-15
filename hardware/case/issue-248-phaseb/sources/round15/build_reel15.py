"""Round 15 reel candidate builder + fitted probe.

Builds all 28 reel wires (right from opt_reel_exact chains; left =
mirror with design index jj = 14 - pin), verifies per-strand slack
accounting, then probes fitted Common volumes: wire-wire (all pairs)
and wire-fixed (both pitch assemblies).
Writes RT15/reel_probe15.json. Usage: build_reel15.py [probe|build]
"""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
import reel2
import opt_reel_exact as ore
from routes_round14 import split_corners

RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
FANS = {int(k): ([np.array(p) for p in v['F1']], [np.array(p) for p in v['F2']])
        for k, v in json.load(open(f'{RT15}/reel_fans.json')).items()}
FANS = {k - 1: v for k, v in FANS.items()}
RADII = {int(k) - 1: v for k, v in json.load(open(f'{RT15}/reel_R.json')).items()}

def wire_from_chains(pre, M, post):
    a = rounded(split_corners(pre))
    arc = Edge.make_three_point_arc(Vector(*pre[-1]), Vector(*M), Vector(*post[0]))
    b = rounded(split_corners(post))
    path = Wire([e for s in (a, Wire([arc]), b) for e in s.edges()])
    d0 = np.array(pre[1], float) - np.array(pre[0], float)
    q = sweep(Face(Wire.make_circle(.5, Plane(origin=Vector(*pre[0]),
                        z_dir=Vector(*map(float, d0))))), path=path)
    assert q.is_valid and len(q.solids()) == 1
    return q, path.length

def build_all():
    wires = {}; meta = {}
    for side, sgn in (('right', 1), ('left', -1)):
        for pin in range(1, 15):
            i = (pin - 1) if sgn > 0 else (14 - pin)
            R = RADII[i]
            pre, M, post, E, X, F1, F2 = ore.chains(i, R, FANS)
            if sgn < 0:
                mir = lambda pts: [[-q[0], q[1], q[2]] for q in pts]
                pre, post = mir(pre), mir(post)
                M = [-M[0], M[1], M[2]]
            q, L = wire_from_chains(pre, M, post)
            name = f'Wire-{side}-{pin:02d}'
            wires[name] = q
            s, st, tt = ore.slack_true(i, R, FANS)
            meta[name] = dict(design_i=i, R=round(R, 3), fitted=round(L, 3),
                              finished=round(L + 7.3, 3), slack=round(s, 3),
                              stored_ref=round(st, 3), taut_ref=round(tt, 3))
            print(name, meta[name], flush=True)
    return wires, meta

def aabb_overlap(a, b, pad=0.0):
    ba, bb = a.bounding_box(), b.bounding_box()
    return all(min(getattr(ba.max, k), getattr(bb.max, k)) -
               max(getattr(ba.min, k), getattr(bb.min, k)) > -pad for k in 'XYZ')

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'probe'
    wires, meta = build_all()
    out = dict(meta=meta)
    if mode == 'probe':
        names = sorted(wires)
        ww = {}
        for a_i in range(len(names)):
            for b_i in range(a_i + 1, len(names)):
                a, b = names[a_i], names[b_i]
                if not aabb_overlap(wires[a], wires[b]): continue
                v = volume(wires[a], wires[b])
                if v > 1e-6: ww[f'{a}x{b}'] = round(v, 4)
        out['wire_wire'] = ww
        print('WW hits:', ww, flush=True)
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
            print(pitch, 'wire-fixed wires with hits:', len(wf), flush=True)
            for wn, d in wf.items(): print('  ', wn, d, flush=True)
    json.dump(out, open(f'{RT15}/reel_probe15.json', 'w'), indent=1)
    print('saved reel_probe15.json', flush=True)
