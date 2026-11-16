"""Shared round-18 fitted machinery (extracted from repair18.py).
Acceptance: candidate design-strand local fitted count (both sides,
both pitches, gate-1 convention: WW repaired-standard, WF plain
Common, threshold 0.005 mm3) must not regress; prefer strict count
improvement, then >=2% volume improvement at equal count.
WW zero-Common pairs are prefiltered by exact centreline samples:
samples at <=0.25 mm arc spacing give curve_min >= d_points - 0.25,
so d_points > 1.28 proves solid distance > 0.03 (disjoint).
State: .issue248-runtime/round18/repair_state.json; resumable."""
import json, sys, time
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlib18 as F
import audit_repair as ar
from geometry import rounded
from OCP.BRepAdaptor import BRepAdaptor_Curve
from OCP.GCPnts import GCPnts_QuasiUniformAbscissa  # unused, kept for reference
from OCP.BRepGProp import BRepGProp
from OCP.GProp import GProp_GProps

RT = '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime'

def path_samples(path, step=0.2):
    """(samples, h): samples along the rounded path at <=step spacing;
    h = max consecutive gap. curve_min >= d_points - (hA + hB)/2."""
    out = []
    for e in path.edges():
        ad = BRepAdaptor_Curve(e.wrapped)
        n = max(2, int(np.ceil(e.length / step)) + 1)
        for u in np.linspace(ad.FirstParameter(), ad.LastParameter(), n):
            p = ad.Value(float(u)); out.append([p.X(), p.Y(), p.Z()])
    A = np.array(out)
    gaps = np.sqrt(((A[1:] - A[:-1]) ** 2).sum(-1))
    return A, float(gaps.max())

def build_s(pts):
    """Strict build + centreline samples. (solid, samples) or (None, why)."""
    try:
        path = rounded(F.rr.split_corners(pts))
    except AssertionError as e:
        return None, f'rounded: {str(e)[:50]}'
    from build123d import sweep, Face, Wire, Plane, Vector
    d0 = np.array(pts[1], float) - np.array(pts[0], float)
    try:
        w = sweep(Face(Wire.make_circle(.5, Plane(origin=Vector(*pts[0]),
                  z_dir=Vector(*map(float, d0))))), path=path)
    except Exception as e:
        return None, f'sweep: {str(e)[:50]}'
    if not (w.is_valid and len(w.solids()) == 1):
        return None, 'invalid'
    return (w, path_samples(path)), None

def min_pp(A, B):
    best = 1e9
    for s in range(0, len(A), 256):
        d = np.sqrt(((A[s:s + 256, None, :] - B[None, :, :]) ** 2).sum(-1))
        best = min(best, float(d.min()))
    return best


def load_bodies():
    bodies = {p: F.bodies_of(p) for p in (17, 16)}
    bb = {p: {n: F.bounds(s) for n, s in bl} for p, bl in bodies.items()}
    return bodies, bb

def vol_pair(a, b, ab, bb, repair=False, sa=None, sb=None):
    if F._gap(ab, bb) > 0: return 0.0
    if repair and sa is not None and sb is not None:
        thr = 1.0 + (sa[1] + sb[1]) / 2 * 1.05 + 0.05
        if min_pp(sa[0], sb[0]) > thr: return 0.0
    v = F.volume(a, b)
    if v > 0 or not repair: return v
    d = ar.solid_distance(a, b)
    if d > ar.DIST_CLEAR: return 0.0
    return ar.clipped_common_volume(a, b)

def eval_wire(name, solid, smp, wires, samp, wb, bodies, body_bnd):
    """(count, vol, hits) for one wire vs all other wires in `wires`
    + all bodies, gate-1 both-pitches convention (WW x2)."""
    cnt, vol, hits = 0, 0.0, []
    wbnd = F.bounds(solid)
    for oname, ow in wires.items():
        if oname == name: continue
        v = vol_pair(solid, ow, wbnd, wb[oname], repair=True, sa=smp, sb=samp[oname])
        if v > F.HIT: cnt += 2; vol += 2 * v; hits.append((oname, round(v, 3)))
    for p in (17, 16):
        for bn, bs in bodies[p]:
            v = vol_pair(solid, bs, wbnd, body_bnd[p][bn])
            if v > F.HIT: cnt += 1; vol += v; hits.append((f'{bn}@{p}', round(v, 3)))
    return cnt, vol, hits
