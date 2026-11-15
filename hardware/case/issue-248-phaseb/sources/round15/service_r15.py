"""Round 15 gate 3 qualification: unplug-first service (PO definition,
round 13/14). States per pitch, exact-Common checked:
  S0 stored (from the round 15 audit itself - not repeated here)
  E(delta): Wing-side plugs extracted delta in {2,4,6} mm along the
     outlet axis e = unit(B0 - B1); each strand's reel arc flattens
     (sagitta factor s bisected) so the fitted path length is
     conserved (the loop feeds the extraction). Wing stack unmoved.
  L: after full extraction, the Wing stack (wing board, plate,
     underside parts, switch envelopes, POM spacers, plate screws/
     washers of that side) lifted +12 mm in Z; harness unmoved
     (plugs hang free at the extracted position).
Shell removal precedes extraction and only removes obstacles (subset
of S0 pairs) - covered by the stored audit, noted in REPORT.
Checks per state: wire vs fixed (excluding the moving set in L),
wire vs wire. Volumes > 1e-6 mm3 are hits.
Writes RT15/service15.json. Usage: service_r15.py [17|16]
"""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
from common import *
import reel2
import opt_reel_exact as ore
import build_reel15 as br
from routes_round14 import split_corners

RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
D9 = json.load(open('/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/routes-round9.json'))
B9 = D9['before']

def moved_names(side, allnames):
    S = 'R' if side == 'right' else 'L'
    out = []
    for n in allnames:
        if n in (f'wing_{side}', f'plate-{side}'): out.append(n)
        elif n.startswith(f'underside-{side}-'): out.append(n)
        elif n.startswith(f'switch-envelope-{S}_'): out.append(n)
        elif n.startswith(f'POM-{side}-'): out.append(n)
        elif n.startswith((f'plate-screw-{side}', f'plate-washer-{side}')): out.append(n)
    return out

def state_wire(i, R, fans, sgn, delta, sag):
    pre, M, post, E, X, F1, F2 = ore.chains(i, R, fans)
    pre = [list(p) for p in pre]; post = [list(p) for p in post]; M = list(M)
    b0 = np.array(B9[i][0], float)
    b1 = np.array(B9[i][1], float)
    e = (b0 - b1); e = e / np.linalg.norm(e)
    pre[0] = (np.array(pre[0]) + delta * e).tolist()
    chord_mid = (np.array(E) + np.array(X)) / 2
    Mv = (chord_mid + sag * (np.array(M) - chord_mid)).tolist()
    if sgn < 0:
        pre = [[-q[0], q[1], q[2]] for q in pre]; post = [[-q[0], q[1], q[2]] for q in post]
        Mv = [-Mv[0], Mv[1], Mv[2]]
    return br.wire_from_chains(pre, Mv, post)

def check_state(wires, fixed, label, out):
    hits = {}
    names = sorted(wires)
    for wn in names:
        w = wires[wn]
        for fn, f in fixed.items():
            if not br.aabb_overlap(w, f): continue
            v = volume(w, f)
            if v > 1e-6: hits.setdefault(wn, {})[fn] = round(v, 4)
    ww = {}
    for a_i in range(len(names)):
        for b_i in range(a_i + 1, len(names)):
            a, b = names[a_i], names[b_i]
            if not br.aabb_overlap(wires[a], wires[b]): continue
            v = volume(wires[a], wires[b])
            if v > 1e-6: ww[f'{a}x{b}'] = round(v, 4)
    out[label] = dict(wire_fixed=hits, wire_wire=ww)
    print(label, 'wire-fixed wires:', len(hits), 'WW pairs:', len(ww), flush=True)
    for wn, d in hits.items(): print('   ', wn, d, flush=True)
    for k, v in ww.items(): print('   WW', k, v, flush=True)

if __name__ == '__main__':
    pitch = int(sys.argv[1]) if len(sys.argv) > 1 else 17
    idx, raw = cached(pitch)
    fixed_all = {n: s for n, k, s in raw if not n.startswith('Wire')}
    out = {}
    base_len = {}
    stored_wires = {}
    for side, sgn in (('right', 1), ('left', -1)):
        for pin in range(1, 15):
            i = (pin - 1) if sgn > 0 else (14 - pin)
            name = f'Wire-{side}-{pin:02d}'
            q, L = state_wire(i, br.RADII[i], br.FANS, sgn, 0.0, 1.0)
            stored_wires[name] = q; base_len[name] = L
    for delta in (2.0, 4.0, 6.0):
        wires = {}
        for side, sgn in (('right', 1), ('left', -1)):
            for pin in range(1, 15):
                i = (pin - 1) if sgn > 0 else (14 - pin)
                name = f'Wire-{side}-{pin:02d}'
                lo, hi = 0.0, 1.0
                for _ in range(12):
                    mid = (lo + hi) / 2
                    q, L = state_wire(i, br.RADII[i], br.FANS, sgn, delta, mid)
                    if L > base_len[name]: hi = mid
                    else: lo = mid
                sag = (lo + hi) / 2
                q, L = state_wire(i, br.RADII[i], br.FANS, sgn, delta, sag)
                wires[name] = q
                print(name, f'delta {delta} sag {sag:.3f} len {L:.2f} vs {base_len[name]:.2f}', flush=True)
        check_state(wires, fixed_all, f'extract_{delta:g}mm', out)
    # lift-out: stored wires at delta 6 geometry vs Wing stacks lifted
    wires = {}
    for side, sgn in (('right', 1), ('left', -1)):
        for pin in range(1, 15):
            i = (pin - 1) if sgn > 0 else (14 - pin)
            name = f'Wire-{side}-{pin:02d}'
            lo, hi = 0.0, 1.0
            for _ in range(12):
                mid = (lo + hi) / 2
                q, L = state_wire(i, br.RADII[i], br.FANS, sgn, 6.0, mid)
                if L > base_len[name]: hi = mid
                else: lo = mid
            q, L = state_wire(i, br.RADII[i], br.FANS, sgn, 6.0, (lo + hi) / 2)
            wires[name] = q
    fixed_lift = dict(fixed_all)
    moved = []
    for side in ('right', 'left'):
        for n in moved_names(side, list(fixed_all)):
            moved.append(n)
            fixed_lift[n] = fixed_all[n].moved(Location(Vector(0, 0, 12)))
    out['moved_bodies'] = moved
    print('moved bodies:', moved, flush=True)
    check_state(wires, fixed_lift, 'lift_out_+12mm', out)
    json.dump(out, open(f'{RT15}/service15_{pitch}.json', 'w'), indent=1)
    print('saved', flush=True)
