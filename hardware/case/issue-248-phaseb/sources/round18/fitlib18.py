"""Round 18 fitted library: strict build (probe17 standard) + repaired
scoring with cached bounds. Plain Common for wire-fixed (every round's
standard); wire-wire zero-volume AABB-overlapping pairs resolved by
exact distance / clipped Common (audit_repair - the round-9/10 blind
spot was demonstrated only for wire-wire). Wires depend only on the
M dict; bodies come from cached(pitch)."""
import json, sys
import numpy as np
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, PB)
for r in ('round14', 'round15', 'round17'):
    sys.path.insert(0, f'{PB}/sources/{r}')
from common import *
import design_r14 as dz
import design_r15 as dz15
import routes_round17 as rr
from geometry import rounded
from build123d import sweep, Face, Wire, Plane, Vector
import audit_repair as ar

dz.rise_top = lambda B, A, i: dz15.rise_top(i)
dz.corridor = dz15.corridor

HIT = 0.005  # mm3, probe17 threshold

def points_of(M, i, side):
    rr.TAUT = M
    pts = rr.points(i, 'taut')
    if side == 'left':
        pts = [[-p[0], p[1], p[2]] for p in pts]
    return pts

def build_wire(pts):
    """Strict build; returns (solid, path_length) or (None, reason)."""
    try:
        path = rounded(rr.split_corners(pts))
    except AssertionError as e:
        return None, f'rounded: {str(e)[:60]}'
    d0 = np.array(pts[1], float) - np.array(pts[0], float)
    try:
        w = sweep(Face(Wire.make_circle(.5, Plane(origin=Vector(*pts[0]),
                  z_dir=Vector(*map(float, d0))))), path=path)
    except Exception as e:
        return None, f'sweep: {str(e)[:60]}'
    if not (w.is_valid and len(w.solids()) == 1):
        return None, 'invalid/multi-solid'
    return w, path.length

def build_all(M):
    wires, lens, failed = {}, {}, []
    for side in ('right', 'left'):
        for pin in range(1, 15):
            name = f'Wire-{side}-{pin:02d}'
            w, r = build_wire(points_of(M, pin - 1, side))
            if w is None:
                failed.append((name, r)); continue
            wires[name] = w
            lens[name] = round(r + 7.30, 2)
    return wires, lens, failed

def bodies_of(pitch):
    idx, raw = cached(pitch)
    return [(n, s) for n, k, s in raw if not n.startswith('Wire')]

def _gap(ab, bb):
    return max(max(ab[0][d] - bb[1][d], bb[0][d] - ab[1][d]) for d in range(3))

class Scorer:
    def __init__(self, wires, bodies_by_pitch):
        self.wires = wires
        self.wb = {n: bounds(s) for n, s in wires.items()}
        self.bodies = bodies_by_pitch
        self.bb = {p: {n: bounds(s) for n, s in bl}
                   for p, bl in bodies_by_pitch.items()}

    def _vol(self, a, b, ab, bb, repair=False):
        if _gap(ab, bb) > 0:
            return 0.0
        v = volume(a, b)
        if v > 0 or not repair:
            return v
        d = ar.solid_distance(a, b)
        if d > ar.DIST_CLEAR:
            return 0.0
        return ar.clipped_common_volume(a, b)

    def ww_pairs(self):
        ww = {}
        names = list(self.wires)
        for a in range(len(names)):
            for b in range(a + 1, len(names)):
                na, nb = names[a], names[b]
                v = self._vol(self.wires[na], self.wires[nb],
                              self.wb[na], self.wb[nb], repair=True)
                if v > HIT: ww[f'{na}x{nb}'] = round(v, 3)
        return ww

    def wf_pairs(self, pitch):
        wf = {}
        for wn, w in self.wires.items():
            for bn, bs in self.bodies[pitch]:
                v = self._vol(w, bs, self.wb[wn], self.bb[pitch][bn])
                if v > HIT: wf[f'{wn}x{bn}'] = round(v, 3)
        return wf

    def full(self):
        ww = self.ww_pairs()
        return ww, {p: self.wf_pairs(p) for p in self.bodies}

    def local(self, name, ww=None):
        """(count, volume) for pairs involving `name`: WW once +
        WF summed over pitches = gate1_17 + gate1_16 contribution."""
        cnt, vol = 0, 0.0
        w = self.wires[name]
        for oname, ow in self.wires.items():
            if oname == name: continue
            v = self._vol(w, ow, self.wb[name], self.wb[oname], repair=True)
            if v > HIT: cnt += 2; vol += 2 * v  # counts at both pitches
        for p, bl in self.bodies.items():
            for bn, bs in bl:
                v = self._vol(w, bs, self.wb[name], self.bb[p][bn])
                if v > HIT: cnt += 1; vol += v
        return cnt, vol

    def strand_vs(self, name, solid, sbnd):
        """Score one candidate solid for strand `name` against all other
        current wires + all bodies. Returns (count, volume) with the
        same both-pitches convention as local()."""
        cnt, vol = 0, 0.0
        for oname, ow in self.wires.items():
            if oname == name: continue
            v = self._vol(solid, ow, sbnd, self.wb[oname], repair=True)
            if v > HIT: cnt += 2; vol += 2 * v
        for p, bl in self.bodies.items():
            for bn, bs in bl:
                v = self._vol(solid, bs, sbnd, self.bb[p][bn])
                if v > HIT: cnt += 1; vol += v
        return cnt, vol

    def set_wire(self, name, solid):
        self.wires[name] = solid
        self.wb[name] = bounds(solid)
