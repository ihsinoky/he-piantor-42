"""Frontier-study fitlib: height-parameterised bodies + points.

Deck height parameter: shift s = plate_top_Z - 13.55 (s=0 is the
Phase B baseline, B=7.35). Body model per height, from the cached
B=7.35 body set (classification by mechanical attachment):
- SHIFT (+s in Z): everything attached to the board plane / deck /
  Fly seat / shells (boards, components, plates, envelopes, POM,
  washers, spacers, Fly set, USB reference, shells, strips, inserts).
- EXTEND (fuse of the solid with its +s translate): parts spanning
  floor to stack whose cross-section extends with B (trays, E-R
  posts, long stack screws). Union overstates material slightly in
  the overlap band (conservative for collision).
- FIXED: floor/desk-anchored parts (splices, joint screws, feet).
Route model per height: round-9 B/A station arrays shifted +s;
rise tops (design_r15) shifted +s; corridor stays absolute
(fx,-18,5.1) (tray channel is floor-anchored geography); M dict is
absolute and is shifted +s only as a seed.
Scoring: fitlib18 standard (plain Common WF; WW repaired via
audit_repair fallback)."""
import sys
import numpy as np
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, PB)
sys.path.insert(0, f'{PB}/sources/round18')
import fitlib18 as F
import routes_round17 as rr
import design_r14 as dz
import design_r15 as dz15

_B0 = [list(map(list, side)) for side in rr.B]
_A0 = [list(map(list, side)) for side in rr.A]

SHIFT_PREFIX = ('Main-', 'EZmate-', 'Fly-', 'USB-reference-', 'POM-',
                'underside-', 'switch-envelope-', 'washer-', 'shell-',
                'strip-', 'cover-Main-spacer-', 'screw-fly-',
                'washer-fly-', 'plate-washer-')
SHIFT_EXACT = {'main', 'wing_left', 'wing_right', 'plate-left',
               'plate-right', 'Fly-170mm'}
EXTEND_PREFIX = ('tray-', 'post-', 'plate-screw-', 'cover-screw-')
EXTEND_EXACT = {'screw-main-H1'}
FIXED_PREFIX = ('splice-', 'joint-screw-', 'rubber-')


def classify(name):
    if name.startswith('Wire'):
        return 'wire'
    if name in SHIFT_EXACT or name.startswith(SHIFT_PREFIX):
        return 'shift'
    if name in EXTEND_EXACT or name.startswith(EXTEND_PREFIX):
        return 'extend'
    if name.startswith(FIXED_PREFIX):
        return 'fixed'
    raise ValueError(f'unclassified body {name}')


_raw_cache = {}


def bodies_at(pitch, s):
    """[(name, shape)] fixed bodies at height shift s (wires excluded)."""
    if pitch not in _raw_cache:
        _raw_cache[pitch] = F.bodies_of(pitch)
    out = []
    for n, solid in _raw_cache[pitch]:
        c = classify(n)
        if s == 0 or c == 'fixed':
            out.append((n, solid))
        elif c == 'shift':
            out.append((n, solid.translate((0, 0, float(s)))))
        else:
            out.append((n, solid.fuse(solid.translate((0, 0, float(s))))))
    return out


def set_height(s):
    rr.B = [[[p[0], p[1], p[2] + s] for p in side] for side in _B0]
    rr.A = [[[p[0], p[1], p[2] + s] for p in side] for side in _A0]
    dz.rise_top = lambda B, A, i: dz15.rise_top(i) + np.array([0., 0., s])
    dz.corridor = dz15.corridor


def points_of(M, i, side):
    return F.points_of(M, i, side)


def shift_M(M, dz_):
    return {k: {kk: [p[0], p[1], p[2] + dz_] for kk, p in v.items()}
            for k, v in M.items()}


build_wire = F.build_wire
Scorer = F.Scorer
bounds = F.bounds
HIT = F.HIT
