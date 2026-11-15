"""Round 17 storage prototype v3, ONE strand (right side).
Stored route = taut route with:
 (a) a BIGHT on the dress segment: spur at 45 deg between dress dir
     and most-down, hairpin arc R5 (sampled), return leg; J2 lands
     2*R*that along the dress from J1.
 (b) a bulge point DET on the climb (westward), handled by the
     standard split_corners/rounded builder.
Closed loops excluded by proof (length >= 2*pi*R for R>=5 loops;
secant entries need >90 deg deflection). Open detours tune to
exactly +30.20 fitted.
Usage: proto_storage.py [pin] [s_len] [det_dx] [det_dy] [det_z]"""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round14')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round15')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round17')
from common import *
import design_r14 as dz
import design_r15 as dz15
import routes_round17 as rr
from geometry import rounded
from build123d import sweep, Face, Wire, Plane, Vector
from exact_dist import Body
from pathbuild import build_path

dz.rise_top = lambda B_, A_, i: dz15.rise_top(i)
dz.corridor = dz15.corridor

PIN = int(sys.argv[1]) if len(sys.argv) > 1 else 1
S_LEN = float(sys.argv[2]) if len(sys.argv) > 2 else 6.5
DDX = float(sys.argv[3]) if len(sys.argv) > 3 else -5.5
DDY = float(sys.argv[4]) if len(sys.argv) > 4 else -14.0
DDZ = float(sys.argv[5]) if len(sys.argv) > 5 else 7.2
RH = 5.0

def bight(Pa, Pb, u_j1, s_len):
    """Bight inserted on segment Pa->Pb at arc position u_j1.
    Spur dir s = normalize(0.7*d + 0.7*m0); lane dir t = normalize(
    0.7*d - 0.7*m0) (both 45 deg). Hairpin: centre S1 + RH*t, arc
    from S1 (tangent s) through +s side to S2 = S1 + 2*RH*t.
    Returns points strictly between Pa and Pb."""
    d = Pb - Pa; L = np.linalg.norm(d); d = d / L
    down = np.array([0., 0., -1.]); m0 = down - (down @ d) * d; m0 /= np.linalg.norm(m0)
    s = 0.7 * d + 0.7 * m0; s /= np.linalg.norm(s)
    t = 0.7 * d - 0.7 * m0; t /= np.linalg.norm(t)
    J1 = Pa + u_j1 * d
    S1 = J1 + s_len * s
    Cc = S1 + RH * t
    S2 = S1 + 2 * RH * t
    J2 = S2 - s_len * s
    deep = Cc + RH * s
    return [J1, S1, S2, J2], deep

def strand_verts(pin, stored=False):
    """Returns (verts, arcs, no_fillet) for pathbuild.build_path."""
    pts = [np.array(p, float) for p in rr.points(pin - 1, 'taut')]
    if not stored:
        return pts, {}, ()
    B1, corr, ORG = pts[1], pts[2], pts[3]
    bg, deep = bight(B1, corr, 3.3, S_LEN)
    fx = corr[0]
    DET = np.array([fx + DDX, DDY, DDZ])
    # verts: B0, B1, J1, S1, [arc samples in bg are replaced], S2, J2, corr, DET, ORG, ...
    # bg = [J1, S1, arc samples..., S2, J2]; keep only J1, S1, S2, J2
    J1, S1, S2, J2 = bg[0], bg[1], bg[-2], bg[-1]
    verts = [pts[0], B1, J1, S1, S2, J2, corr, DET, ORG] + pts[4:]
    return verts, {3: deep}, (3, 4)

def build_wire(verts, arcs, no_fillet):
    path, plen = build_path(verts, arcs=arcs, no_fillet=no_fillet)
    d0 = np.array(verts[1], float) - np.array(verts[0], float)
    w = sweep(Face(Wire.make_circle(.5, Plane(origin=Vector(*map(float, verts[0])),
                      z_dir=Vector(*map(float, d0))))), path=path)
    return w, plen

def samples_of(pts, step=0.8):
    out = []
    for a, b in zip(pts[:-1], pts[1:]):
        a = np.array(a, float); b = np.array(b, float)
        nn = max(int(np.linalg.norm(b - a) / step), 1)
        for k in range(nn):
            out.append(a + (b - a) * k / nn)
    out.append(np.array(pts[-1], float))
    return out

tv, ta, tnf = strand_verts(PIN)
sv, sa, snf = strand_verts(PIN, stored=True)
wt, lt = build_wire(tv, ta, tnf); ws, ls = build_wire(sv, sa, snf)
taut = tv
stored = sv[:4] + [sa[3]] + sv[4:]  # deep point inserted for sampling
print(f'pin {PIN}: taut fitted {lt:.3f}  stored fitted {ls:.3f}  delta {ls - lt:+.3f} (target +30.20)')
print(f'  stored valid {ws.is_valid()} taut valid {wt.is_valid()}')

idx, raw = cached(17)
bodies = []
for nm, kind, shp in raw:
    if nm.startswith('Wire') or nm in ('tray-right', 'tray-left'):
        continue
    if shp.bounding_box().max.X < -2:
        continue
    bodies.append(Body(nm, shp))
ss = samples_of(stored)
worst = (9e9, None, None)
for p in ss:
    for ob in bodies:
        dd = ob.dist(p)
        if dd < worst[0]:
            worst = (dd, ob.name, p)
print(f'  min oracle dist (tray excl): {worst[0]:.3f} vs {worst[1]} at {np.round(worst[2],1)}')
arr = np.array(ss); mind = 9e9
for k in range(len(arr)):
    dv = arr[k + 13:] - arr[k]
    if len(dv):
        mind = min(mind, float(np.min(np.linalg.norm(dv, axis=1))))
print(f'  min self-proximity (gap>12): {mind:.3f}')
for np_ in (PIN - 2, PIN - 1, PIN + 1, PIN + 2):
    if 1 <= np_ <= 14:
        nv, _, _ = strand_verts(np_)
        ns = np.array(samples_of(nv))
        dmin = 9e9
        for p in ss:
            dmin = min(dmin, float(np.min(np.linalg.norm(ns - p, axis=1))))
        print(f'  min dist to taut pin {np_}: {dmin:.3f}')
