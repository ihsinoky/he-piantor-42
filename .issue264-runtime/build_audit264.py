"""Issue 264 fitted audit: stock FFC (Molex 152660149, 152 mm Type A) folded
onto the #261 route at plate 10.90 (s=-2.65), pitch 17. Machinery inherited
from #261 audit_static.py / audit_service.py (build123d + fitlibF bodies +
repair18_lib repaired vol_pair). Differences vs #261: sheet width 9.6 /
thickness 0.32 (stock cable 0.27 + allowance), fold patches + roll boxes,
stacked S-pair legs at raised z, channel follows the folded path incl.
stack/patch/roll relief. Wing ZIF entry slot cut deepened to full envelope
depth (the real FH12 slot runs the connector depth; #261's sheet stopped at
the slot face so its 1.8 mm cut sufficed)."""
import json, sys, math
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
import fitlib18 as F
import repair18_lib as R
from build123d import Box, Pos, Rot, export_step

RT = '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime'

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

def seg_box(a, b, w, t, zoff=0.0, extra_len=0.35):
    d = np.array(b, float) - np.array(a, float); L = float(np.linalg.norm(d))
    if L < 1e-6: return None
    yaw = math.degrees(math.atan2(d[1], d[0]))
    pitch = math.degrees(math.asin(max(-1, min(1, d[2] / L))))
    mid = (np.array(a, float) + np.array(b, float)) / 2
    return Pos(mid[0], mid[1], mid[2] + zoff) * Rot(0, 0, yaw) * Rot(0, -pitch, 0) * Box(L + extra_len, w, t)

def fuse_all(solids):
    s = solids[0]
    for x in solids[1:]:
        s = s.fuse(x)
    return s

def sheet_from_pts(pts, w, t):
    return fuse_all([s for a, b in zip(pts[:-1], pts[1:]) if (s := seg_box(a, b, w, t)) is not None])

def box_at(cx, cy, cz, dx, dy, dz, yaw=0.0):
    return Pos(cx, cy, cz) * Rot(0, 0, yaw) * Box(dx, dy, dz)

# ---------------- folded path (RIGHT) ----------------
def path_V(s1_dy=0.0, sx=1):
    din = (0.04643, 0.99892)
    s1 = (14.08, 24.4 + s1_dy)
    S2X = 13.00
    V = [(27.0, -38.5, 2.95), (25.2, -15.0, 2.95), (11.37, -22.0, 2.95),
         (11.44, -19.0, 2.95), (12.29, -15.0, 4.93), (12.48, -11.0, 6.90),
         (s1[0]-3*din[0], s1[1]-3*din[1], 6.90), (s1[0], s1[1], 7.06),
         (s1[0]-3*0.0464, s1[1]-3*0.9989, 7.22),
         (S2X+3*0.0464, 0.43+3*0.9989, 7.22), (S2X, 0.43, 7.38),
         (S2X+3*din[0], 0.43+3*din[1], 7.54), (14.41, 30.60, 7.54),
         (14.41+3*0.6474, 30.60+3*0.7622, 7.22), (20.92, 38.24, 6.90),
         (22.6, 40.0, 6.90)]
    return [(sx * x, y, z) for x, y, z in V]

FOLDS = [(1, 6.0, 'F_A'), (2, 6.0, 'F_B'), (12, 14.0, 'F_V7')]  # (V index, patch total len, tag)

def rolls(s1_dy=0.0, sx=1):
    return [((sx * 14.08, 24.4 + s1_dy), 6.90, 7.43, 'roll-S1'),
            ((sx * 13.00, 0.43), 7.22, 7.75, 'roll-S2')]

def build_cable(w=9.6, t=0.32, patch_th=0.30, s1_dy=0.0, sx=1):
    V = path_V(s1_dy, sx)
    solids = [s for a, b in zip(catmull(V)[:-1], catmull(V)[1:]) if (s := seg_box(a, b, w, t)) is not None]
    for idx, Lp, tag in FOLDS:
        c = np.array(V[idx], float)
        for j in (idx-1, idx):
            a, b = np.array(V[j], float), np.array(V[j+1], float)
            d = b - a; u = d / np.linalg.norm(d)
            p0 = c - u * (Lp/2) if j == idx-1 else c
            p1 = c if j == idx-1 else c + u * (Lp/2)
            s = seg_box(p0, p1, w, patch_th, zoff=-(t/2 + patch_th/2))
            if s is not None: solids.append(s)
    for (vx, vy), zb, zt, tag in rolls(s1_dy, sx):
        solids.append(box_at(vx, vy, (zb+zt)/2, w, 4.4, zt-zb))
    return fuse_all(solids)

def build_channel(w=9.6, t=0.32, patch_th=0.30, s1_dy=0.0, sx=1):
    V = path_V(s1_dy, sx)
    pts = catmull(V)
    solids = [s for a, b in zip(pts[:-1], pts[1:]) if (s := seg_box(a, b, 11.4, t + 0.525, zoff=0.0375, extra_len=1.2)) is not None]
    for idx, Lp, tag in FOLDS:
        c = np.array(V[idx], float)
        hh = t + patch_th + 0.525
        zoff = ((c[2]-t/2-patch_th-0.225) + (c[2]+t/2+0.30)) / 2 - c[2]
        for j in (idx-1, idx):
            a, b = np.array(V[j], float), np.array(V[j+1], float)
            d = b - a; u = d / np.linalg.norm(d)
            p0 = c - u * (Lp/2) if j == idx-1 else c
            p1 = c if j == idx-1 else c + u * (Lp/2)
            s = seg_box(p0, p1, 11.4, hh, zoff=zoff, extra_len=1.2)
            if s is not None: solids.append(s)
    for (vx, vy), zb, zt, tag in rolls(s1_dy, sx):
        solids.append(box_at(vx, vy, (zb-0.225+zt+0.30)/2, 11.4, 5.2, (zt+0.30)-(zb-0.225)))
    return fuse_all(solids)

# ---------------- ZIF envelopes (from #261, Wing slot deepened) ----------------
def make_zifs():
    zif_wr = box_at(27.0, -37.5, 3.70, 11, 7, 2.0)
    zif_wr = zif_wr.cut(box_at(27.0, -37.3, 2.95, 10.4, 7.4, 0.5))
    zif_mr = box_at(23.3, 40.8, 6.90, 11, 7, 2.0, yaw=-43.0)
    zif_mr = zif_mr.cut(box_at(23.3, 40.8, 6.90, 10.6, 7.0, 0.9, yaw=-43.0))
    zif_wl = box_at(-27.0, -37.5, 3.70, 11, 7, 2.0)
    zif_wl = zif_wl.cut(box_at(-27.0, -37.3, 2.95, 10.4, 7.4, 0.5))
    zif_ml = box_at(-23.09, 40.97, 6.90, 11, 7, 2.0, yaw=38.0)
    zif_ml = zif_ml.cut(box_at(-23.09, 40.97, 6.90, 10.6, 7.0, 0.9, yaw=38.0))
    return {'ZIF-wing-right': zif_wr, 'ZIF-main-right': zif_mr,
            'ZIF-wing-left': zif_wl, 'ZIF-main-left': zif_ml}

def assemble(s1_dy=0.0, w=9.6, t=0.32, patch_th=0.30):
    zifs = make_zifs()
    bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
              if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
    bodies += list(zifs.items())
    chan_r = build_channel(w, t, patch_th, s1_dy, sx=1)
    chan_l = build_channel(w, t, patch_th, s1_dy, sx=-1)
    chan = chan_r.fuse(chan_l)
    out = []
    for n, s in bodies:
        if n in ('tray-right', 'tray-left'):
            s = s.cut(chan)
        out.append((n, s))
    cable_r = build_cable(w, t, patch_th, s1_dy, sx=1)
    cable_l = build_cable(w, t, patch_th, s1_dy, sx=-1)
    return out, cable_r, cable_l, zifs

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
    bodies, cable_r, cable_l, zifs = assemble()
    print('fixed bodies:', len(bodies), flush=True)
    res['gate1_base_right'] = audit('cable_r', cable_r, bodies)
    print('BASE right hits:', res['gate1_base_right'], flush=True)
    res['gate1_base_left'] = audit('cable_l', cable_l, bodies)
    print('BASE left hits:', res['gate1_base_left'], flush=True)
    res['cable_vs_cable'] = float(R.vol_pair(cable_r, cable_l, F.bounds(cable_r), F.bounds(cable_l), repair=True))
    print('cable_vs_cable:', res['cable_vs_cable'], flush=True)
    bodies2, cable2_r, cable2_l, _ = assemble(s1_dy=2.0, w=10.4, patch_th=0.35)
    res['gate1_sens_right'] = audit('cable2_r', cable2_r, bodies2)
    print('SENS right hits:', res['gate1_sens_right'], flush=True)
    res['gate1_sens_left'] = audit('cable2_l', cable2_l, bodies2)
    print('SENS left hits:', res['gate1_sens_left'], flush=True)
    export_step(cable_r, f'{RT}/preview264-cable-r.step')
    json.dump(res, open(f'{RT}/audit264.json', 'w'), indent=1)
    print('DONE', flush=True)
