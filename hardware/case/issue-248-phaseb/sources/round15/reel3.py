"""Round 15 reel v3 geometry: per-strand disk placements.

Round 15 scans proved no single shared axis fits a 270 deg wrap
(R ~= 9.2, mandated by the +30.2 mm slack equation) at 7-14 stacked
Z levels: tray bosses block low levels, the Wing slab (Z 7.35-8.55)
and switch envelopes block mid levels, the slope cheeks and ceiling
block high levels. The disk-placement scan (RT15/disk_grid.json)
instead found many individually feasible (centre, Z) pockets -
mostly the under-Main / under-plateau bands at Z 5.0-6.05 and a few
northern pockets at Z 9.2-11.3+. Reel v3 therefore gives every
strand its own disk placement (sides independent), Z levels spread
>= 1.05 mm apart (or centres >= 19.4 mm apart in plan), entry/exit
directions and the slack accounting unchanged from round 14.
Placements: RT15/reel_place.json {side: {design_i: {C, Z}}}.
"""
import json
import numpy as np

RT15 = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/round15'
U = np.array([np.cos(np.radians(-45.0)), np.sin(np.radians(-45.0))])
def _rot(v, deg):
    t = np.radians(deg); c, s = np.cos(t), np.sin(t)
    return np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]])
W = _rot(U, -270.0)
TMID = _rot(U, -135.0)
T_ENTRY = np.array([-0.70710678, -0.70710678, 0.0])
T_EXIT = np.array([0.70710678, -0.70710678, 0.0])

try:
    _RAW = json.load(open(f'{RT15}/reel_place.json'))
    PLACE = {side: {int(k): (np.array(v['C'], float), float(v['Z']))
                    for k, v in d.items()}
             for side, d in _RAW.items()}
    PLACE_R = {side: {int(k): float(v.get('R', 9.2)) for k, v in d.items()}
               for side, d in _RAW.items()}
except FileNotFoundError:
    PLACE = {}; PLACE_R = {}

def _dirs(side):
    if side == 'right': return U, W, TMID
    m = np.array([-1.0, 1.0])
    return U * m, W * m, TMID * m
def entry(side, i, R=9.2):
    C, Z = PLACE[side][i]
    p = C + R * _dirs(side)[0]
    return np.array([p[0], p[1], Z])
def exitp(side, i, R=9.2):
    C, Z = PLACE[side][i]
    p = C + R * _dirs(side)[1]
    return np.array([p[0], p[1], Z])
def midp(side, i, R=9.2):
    C, Z = PLACE[side][i]
    p = C + R * _dirs(side)[2]
    return np.array([p[0], p[1], Z])
def tangents(side):
    if side == 'right': return T_ENTRY, T_EXIT
    m = np.array([-1.0, 1.0, 1.0])
    return T_ENTRY * m, T_EXIT * m
