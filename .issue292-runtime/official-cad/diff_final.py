#!/usr/bin/env python3
"""Final pad diff: official (Altium PcbLib via KiCad import, KiCad frame)
vs derived footprint (KiCad frame). By-number, over 4 rotations of the
centered official frame; orientation chosen by corner-pin agreement."""
import json, math

alt = {r[0]: r[1:] for r in json.load(open('altium-pads.json'))}
der = json.load(open('../isp1807-derived-pads.json'))
xs = [v[0] for v in alt.values()]; ys = [v[1] for v in alt.values()]
cx, cy = (min(xs)+max(xs))/2, (min(ys)+max(ys))/2
off = {k: [v[0]-cx, v[1]-cy, v[2], v[3]] for k, v in alt.items()}
print('official centered bbox x', min(v[0] for v in off.values()), max(v[0] for v in off.values()),
      'y', min(v[1] for v in off.values()), max(v[1] for v in off.values()))

def rot(p, n):
    x, y = p
    return [(x, y), (-y, x), (-x, -y), (y, -x)][n]

corners_der = {k: v for k, v in der.items() if v[2] > 0.5}
print('derived big pads:', {k: v[:2] for k, v in corners_der.items()})
corners_off = {k: v for k, v in off.items() if v[2] > 0.5}
print('official big pads:', {k: v[:2] for k, v in corners_off.items()})

for n in range(4):
    errs = {}
    for k in der:
        if k in off:
            tx, ty = rot(off[k][:2], n)
            errs[k] = math.hypot(tx-der[k][0], ty-der[k][1])
    med = sorted(errs.values())[len(errs)//2]
    print(f'rot{n*90}: by-number median {med:.3f} max {max(errs.values()):.3f} '
          f'within0.05 {sum(1 for e in errs.values() if e < 0.05)}/69')
