#!/usr/bin/env python3
"""Set-based alignment: official pads (unlabeled) vs derived pads (unlabeled).
For each dihedral transform of the official set (centroid-aligned), compute
nearest-neighbour distances both ways."""
import json, math

off = json.load(open('official-pads.json'))
der = json.load(open('../isp1807-derived-pads.json'))
O = [(v[0], v[1]) for v in off.values()]
D = [(v[0], v[1]) for v in der.values()]

def centroid(P):
    return (sum(p[0] for p in P)/len(P), sum(p[1] for p in P)/len(P))

oc, dc = centroid(O), centroid(D)
Oc = [(x-oc[0], y-oc[1]) for x, y in O]
Dc = [(x-dc[0], y-dc[1]) for x, y in D]

def tf(p, name):
    x, y = p
    return {'id': (x, y), 'rot90': (-y, x), 'rot180': (-x, -y), 'rot270': (y, -x),
            'flipx': (-x, y), 'flipy': (x, -y), 'flipxy': (y, x), 'flipx_rot90': (-y, -x)}[name]

for name in ['id', 'rot90', 'rot180', 'rot270', 'flipx', 'flipy', 'flipxy', 'flipx_rot90']:
    T = [tf(p, name) for p in Oc]
    # derived -> nearest official
    errs = []
    for d in Dc:
        errs.append(min(math.hypot(d[0]-t[0], d[1]-t[1]) for t in T))
    within = sum(1 for e in errs if e < 0.05)
    print(f'{name:12s} derived->official: max {max(errs):.3f} mean {sum(errs)/len(errs):.3f} within0.05 {within}/{len(errs)}')
