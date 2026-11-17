"""Issue #261 Stage 1: FPC fitted audit at plate 10.90 (s=-2.65), pitch 17.
Bodies: #248 frontier bodies_at(17,-2.65) minus Main-GH bounds, plus ZIF
envelopes. FPC sheets built as fused station boxes along a Catmull-Rom
centreline (width 10.2, thickness 0.25: FPC 0.15 + allowance)."""
import json, sys, math
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
import fitlib18 as F
import repair18_lib as R
from build123d import Box, Pos, Rot, Solid

RT = '/home/hatch/workspace/projects/he-piantor-lowdeck/.issue261-runtime'

def catmull(P, n_per=14):
    P = [P[0]] + list(P) + [P[-1]]
    out = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = [np.array(x, float) for x in P[i:i+4]]
        for j in range(n_per):
            t = j / n_per
            out.append(0.5 * ((2*p1) + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t*t + (-p0+3*p1-3*p2+p3)*t*t*t))
    out.append(np.array(P[-2], float))
    return out

def sheet_boxes(pts, w=10.2, t=0.25):
    solids = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a; L = float(np.linalg.norm(d))
        if L < 1e-6: continue
        yaw = math.degrees(math.atan2(d[1], d[0]))
        pitch = math.degrees(math.asin(max(-1, min(1, d[2] / L))))
        mid = (a + b) / 2
        box = Pos(mid[0], mid[1], mid[2]) * Rot(0, 0, yaw) * Rot(0, -pitch, 0) * Box(L + 0.35, w, t)
        solids.append(box)
    return solids

def sheet(pts, w=10.2, t=0.25):
    solids = sheet_boxes(pts, w, t)
    s = solids[0]
    for x in solids[1:]:
        s = s.fuse(x)
    return s

def box_at(cx, cy, cz, dx, dy, dz, yaw=0.0):
    return Pos(cx, cy, cz) * Rot(0, 0, yaw) * Box(dx, dy, dz)

CTRL_R = [(27.0, -34.0, 2.95), (26.5, -24.0, 2.95), (25.5, -16.0, 2.95),
          (24.8, -8.0, 2.95), (20.0, -2.0, 2.95), (14.0, -0.5, 2.95),
          (11.5, -1.0, 2.95), (9.0, -3.5, 3.60), (7.5, -7.0, 5.20),
          (7.5, -12.0, 6.90), (11.2, -6.0, 6.90), (13.2, 2.0, 6.90),
          (13.44, 30.21, 6.90), (20.92, 38.24, 6.90)]
CTRL_L = [(-27.0, -34.0, 2.95), (-26.5, -24.0, 2.95), (-25.5, -16.0, 2.95),
          (-24.8, -8.0, 2.95), (-20.0, -2.0, 2.95), (-14.0, -0.5, 2.95),
          (-11.5, -1.0, 2.95), (-9.0, -3.5, 3.60), (-7.5, -7.0, 5.20),
          (-7.5, -12.0, 6.90), (-11.2, -6.0, 6.90), (-13.9, 2.0, 6.90),
          (-14.54, 30.21, 6.90), (-20.92, 38.24, 6.90)]

fpc_r = sheet(catmull(CTRL_R))
fpc_l = sheet(catmull(CTRL_L))
boxes_r = sheet_boxes(catmull(CTRL_R))
boxes_l = sheet_boxes(catmull(CTRL_L))

# ZIF envelopes (fixed, part of boards), each with the FPC entry slot cut out
zif_wr = box_at(27.0, -37.5, 3.70, 11, 7, 2.0)                    # Wing underside
zif_wr = zif_wr.cut(box_at(27.0, -34.2, 2.95, 10.4, 1.8, 0.5))
zif_mr = box_at(23.3, 40.8, 6.90, 11, 7, 2.0, yaw=-43.0)          # Main top, NW-facing
zif_mr = zif_mr.cut(box_at(21.19, 38.53, 6.90, 10.6, 2.6, 0.9, yaw=-43.0))
zif_wl = box_at(-27.0, -37.5, 3.70, 11, 7, 2.0)
zif_wl = zif_wl.cut(box_at(-27.0, -34.2, 2.95, 10.4, 1.8, 0.5))
zif_ml = box_at(-23.09, 40.97, 6.90, 11, 7, 2.0, yaw=38.0)
zif_ml = zif_ml.cut(box_at(-21.17, 38.55, 6.90, 10.6, 2.6, 0.9, yaw=38.0))
zifs = {'ZIF-wing-right': zif_wr, 'ZIF-main-right': zif_mr,
        'ZIF-wing-left': zif_wl, 'ZIF-main-left': zif_ml}

bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
          if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
bodies += list(zifs.items())

# Case delta (Stage-1 design): formed FPC channel in the tray along the
# WHOLE route — swept sheet footprint (width 11.4) relieved 0.225 below
# and 0.30 above the sheet at every station.
def channel_solid(ctrl):
    pts = catmull(ctrl)
    solids = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a; L = float(np.linalg.norm(d))
        if L < 1e-6: continue
        yaw = math.degrees(math.atan2(d[1], d[0]))
        pitch = math.degrees(math.asin(max(-1, min(1, d[2] / L))))
        mid = (a + b) / 2
        solids.append(Pos(mid[0], mid[1], mid[2] + 0.0375) * Rot(0, 0, yaw) * Rot(0, -pitch, 0) * Box(L + 1.2, 11.4, 0.775))
    s = solids[0]
    for x in solids[1:]:
        s = s.fuse(x)
    return s

chan_r = channel_solid(CTRL_R)
chan_l = channel_solid(CTRL_L)
cut_bodies = []
for n, s in bodies:
    if n in ('tray-right', 'tray-left'):
        s = s.cut(chan_r).cut(chan_l)
    cut_bodies.append((n, s))
bodies = cut_bodies
print('fixed bodies:', len(bodies), flush=True)

def audit(name, solid, body_list):
    hits = []
    bb = solid.bounding_box()
    for n, bs in body_list:
        b2 = bs.bounding_box()
        if (bb.max.X < b2.min.X - 1 or bb.min.X > b2.max.X + 1 or
            bb.max.Y < b2.min.Y - 1 or bb.min.Y > b2.max.Y + 1 or
            bb.max.Z < b2.min.Z - 1 or bb.min.Z > b2.max.Z + 1):
            continue
        v = R.vol_pair(solid, bs, F.bounds(solid), F.bounds(bs), repair=True)
        if v > F.HIT:
            hits.append((n, round(float(v), 4)))
    return hits

if __name__ == '__main__':
    res = {}
    res['fpc_right'] = audit('fpc_right', fpc_r, bodies)
    print('fpc_right hits:', res['fpc_right'], flush=True)
    res['fpc_left'] = audit('fpc_left', fpc_l, bodies)
    print('fpc_left hits:', res['fpc_left'], flush=True)
    res['fpc_vs_fpc'] = R.vol_pair(fpc_r, fpc_l, F.bounds(fpc_r), F.bounds(fpc_l), repair=True)
    print('fpc_vs_fpc vol:', res['fpc_vs_fpc'], flush=True)
    json.dump(res, open(f'{RT}/audit_static.json', 'w'), indent=1)
    print('DONE')
