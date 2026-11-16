"""Corrected Wing lift-out: carriers REMOVED first (procedure step).
Reports NEW contacts introduced by the lift (lifted hit set minus
fitted-base hit set) for the moving group (Wing PCB + plate + switch
envelopes + its SegW wires) vs everything else, +Z {5, 20}."""
import json, sys, time
sys.path.insert(0, '.')
import fitlib252 as C
import fitlib18 as F
import repair18_lib as R
import repair252 as RP
from build123d import Pos

D = json.load(open('design_state.json'))
bodies = C.all_bodies()
wires, lens, failed = C.build_all(D)
assert not failed
solids = {n: r[0] for n, r in wires.items()}
samp = {n: r[1] for n, r in wires.items()}

def hits_for(moved_solids, fixed):
    out = set()
    for nm, s in moved_solids.items():
        for fn, fs in fixed.items():
            v = R.vol_pair(s, fs, F.bounds(s), F.bounds(fs))
            if v > F.HIT: out.add((nm, fn))
    return out

for side in ('right', 'left'):
    bl = dict(bodies[17])
    env = f'switch-envelope-{"R" if side == "right" else "L"}_'
    moving_b = {n: s for n, s in bl.items()
                if n in (f'wing_{side}', f'plate-{side}') or n.startswith(env)}
    moving_w = {C.wire_name('SegW', side, i): solids[C.wire_name('SegW', side, i)] for i in range(14)}
    fixed = {n: s for n, s in bl.items()
             if n not in moving_b and not n.startswith(f'carrier-{side}') and not n.startswith(f'seat-{side}')}
    fixed.update({n: s for n, s in solids.items() if n not in moving_w})
    base = hits_for({**moving_b, **moving_w}, fixed)
    for dz in (5, 20):
        mv = {n: Pos(0, 0, dz) * s for n, s in {**moving_b, **moving_w}.items()}
        now = hits_for(mv, fixed)
        new = now - base
        print(f'{side} lift +{dz}: base_hits {len(base)}, lifted {len(now)}, NEW {len(new)}',
              sorted(new)[:6], flush=True)
print('DONE')
