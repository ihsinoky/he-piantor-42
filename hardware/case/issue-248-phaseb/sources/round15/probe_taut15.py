"""Round 15 taut candidate, STRICT build: round-14 optimised feed
on the design_r15 rise skeleton. No point-dropping fallback -
a rounded() assert is recorded as a build failure for that strand.
Fitted probe: wire-wire + wire-fixed volumes, both pitches, and
finished lengths. Writes RT15/taut15_probe.json."""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
import design_r14 as dz
import design_r15 as dz15
import routes_round14 as rr
from geometry import rounded
from build123d import sweep, Face, Wire, Plane, Vector

dz.rise_top = lambda B, A, i: dz15.rise_top(i)
dz.corridor = dz15.corridor
RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
out = {}
for pitch in (17, 16):
    idx, raw = cached(pitch)
    bodies = [(n, s) for n, k, s in raw if not n.startswith('Wire')]
    wires = {}; lens = {}; failed = []
    for side in ('right', 'left'):
        sgn = 1 if side == 'right' else -1
        for pin in range(1, 15):
            jj = pin - 1
            pts = [np.array(p, float) * [sgn, 1, 1] for p in rr.points(jj, 'taut')]
            try:
                path = rounded(rr.split_corners(pts))
            except AssertionError as e:
                failed.append((side, pin, str(e)[:80])); continue
            d0 = pts[1] - pts[0]
            w = sweep(Face(Wire.make_circle(.5, Plane(origin=Vector(*pts[0]),
                      z_dir=Vector(*map(float, d0))))), path=path)
            assert w.is_valid and len(w.solids()) == 1
            wires[f'Wire-{side}-{pin:02d}'] = w
            lens[f'{side}-{pin:02d}'] = round(path.length + 7.30, 2)
    ww = {}; wf = {}
    names = list(wires)
    for a in range(len(names)):
        for b in range(a + 1, len(names)):
            c = wires[names[a]].intersect(wires[names[b]])
            v = sum(s.volume for s in c.solids()) if c else 0.0
            if v > 0.005: ww[f'{names[a]}x{names[b]}'] = round(v, 3)
    for wn, w in wires.items():
        for bn, bs in bodies:
            c = w.intersect(bs)
            v = sum(s.volume for s in c.solids()) if c else 0.0
            if v > 0.005: wf[f'{wn}x{bn}'] = round(v, 3)
    out[str(pitch)] = {'ww': ww, 'wf': wf, 'failed': failed,
                       'longest': max(lens.values()), 'lens': lens}
    print(pitch, 'WW pairs', len(ww), 'WF hits', len(wf), 'failed', failed,
          'longest', max(lens.values()), flush=True)
    print('  WW:', ww, flush=True)
    print('  WF:', wf, flush=True)
json.dump(out, open(f'{RT15}/taut15_probe.json', 'w'), indent=1)
print('saved taut15_probe.json', flush=True)
