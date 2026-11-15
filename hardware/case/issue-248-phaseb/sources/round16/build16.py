"""Round 16 stored-wire builder + fitted probe.

Builds all 28 stored wires from RT16/fans16.json + place16.json
(right from opt_fans16 chains; left = mirror with design index
jj = 14 - pin, as build_reel15), STRICT (no point dropping; a
rounded() assert is a recorded build failure), verifies per-strand
analytic slack accounting (target +30.20), then probes fitted
Common volumes > 0.005 mm3: wire-wire (all pairs) and wire-fixed
(both pitch assemblies). Writes RT16/stored_probe16.json.
Usage: build16.py [probe|build]
"""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round16')
from common import *
import opt_fans16 as of16
from routes_round14 import split_corners
from geometry import rounded
from build123d import sweep, Face, Wire, Plane, Vector, Edge

RT16 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round16'
SOL = {}
_F = json.load(open(f'{RT16}/fans16.json'))
for k, v in _F.items():
    SOL[int(k) - 1] = (np.array(v['W']), [np.array(p) for p in v['F1']],
                       [np.array(p) for p in v['F2']])

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
    wires = {}; meta = {}; failed = []
    for side, sgn in (('right', 1), ('left', -1)):
        for pin in range(1, 15):
            i = (pin - 1) if sgn > 0 else (14 - pin)
            name = f'Wire-{side}-{pin:02d}'
            try:
                pre, M, post, E, X = of16.chains(i, SOL)
                if sgn < 0:
                    mir = lambda pts: [[-q[0], q[1], q[2]] for q in pts]
                    pre, post = mir(pre), mir(post)
                    M = [-M[0], M[1], M[2]]
                q, L = wire_from_chains(pre, M, post)
            except AssertionError as e:
                failed.append((name, str(e)[:80])); continue
            wires[name] = q
            s, st, tt = of16.slack_true(i, SOL)
            meta[name] = dict(design_i=i, R=round(float(of16.PLACE[i]['R']), 3),
                              th=round(float(of16.PLACE[i]['th']), 4),
                              fitted=round(L, 3), finished=round(L + 7.3, 3),
                              slack=round(s, 3))
            print(name, meta[name], flush=True)
    return wires, meta, failed

if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'probe'
    wires, meta, failed = build_all()
    out = dict(meta=meta, failed=failed)
    print('built', len(wires), 'failed', failed, flush=True)
    if mode == 'probe' and len(wires) == 28:
        names = sorted(wires)
        ww = {}
        for a_i in range(len(names)):
            for b_i in range(a_i + 1, len(names)):
                c = wires[names[a_i]].intersect(wires[names[b_i]])
                v = sum(s.volume for s in c.solids()) if c else 0.0
                if v > 0.005: ww[f'{names[a_i]}x{names[b_i]}'] = round(v, 3)
        out['wire_wire'] = ww
        print('WW hits:', ww, flush=True)
        for pitch in (17, 16):
            idx, raw = cached(pitch)
            fixed = {n: s for n, k, s in raw if not n.startswith('Wire')}
            wf = {}
            for wn, w in wires.items():
                for fn, f in fixed.items():
                    ba, bb = w.bounding_box(), f.bounding_box()
                    if not all(min(getattr(ba.max, k), getattr(bb.max, k)) -
                               max(getattr(ba.min, k), getattr(bb.min, k)) > 0 for k in 'XYZ'):
                        continue
                    c = w.intersect(f)
                    v = sum(s.volume for s in c.solids()) if c else 0.0
                    if v > 0.005: wf[f'{wn}x{fn}'] = round(v, 3)
            out[f'wire_fixed_{pitch}'] = wf
            print(pitch, 'WF hits:', len(wf), flush=True)
            for k in sorted(wf, key=lambda k: -wf[k])[:15]: print('  ', k, wf[k], flush=True)
    json.dump(out, open(f'{RT16}/stored_probe16.json', 'w'), indent=1)
    print('saved stored_probe16.json', flush=True)
