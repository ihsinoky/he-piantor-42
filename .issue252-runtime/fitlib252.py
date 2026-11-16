"""Issue #252 Candidate C fitted library.

Segments per side (right design frame; left = mirror x->-x, same
strand index convention as fitlib18):
  Wing segment: [B0, B1, COR, RISE, W1, W2, W3, AP_W, T_W]
  Main segment: [T_M, AP_M, N1, P, G, ep]
Carrier (right): board box X[4,28] Y[-8,27] Z[12.75,14.35];
header M on BOTTOM face (origin (15,14.45), row (-1,0,0), axis
(0,1,0), tails Z 10.65 at Y=20); header W on TOP face (origin
(13.55,8), row (0,1,0), axis (-1,0,0), tails Z 16.45 at X=8).
Header/plug solids = B1 dimensioned local bounds transformed.
Seat: 2 posts D7 at (8,4),(24,4), Z[0,12.75] (case delta)."""
import json, sys
import numpy as np
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, PB)
sys.path.insert(0, f'{PB}/sources/round18')
sys.path.insert(0, f'{PB}/sources/round14')
sys.path.insert(0, f'{PB}/sources/round15')
import fitlib18 as F
import repair18_lib as R
import design_r14 as dz
import design_r15 as dz15
import routes_round17 as rr
from build123d import Box, Cylinder, Pos, Plane

HIT = F.HIT
AX = dz.AX  # (0.8660254, -0.5, 0) Main connector axis (exit dir)

# ---------------- fixed stations (right) ----------------
def stations(i):
    ep, G, P = dz.stations(rr.B, rr.A, i)
    return ep, G, P

def wing_fixed(i):
    return [list(rr.B[i][0]), list(rr.B[i][1]),
            dz15.corridor(i).tolist(), dz15.rise_top(i).tolist()]

# ---------------- carrier geometry (right) ----------------
BOARD = {'x': (3.0, 32.0), 'y': (-8.0, 27.0), 'z': (12.75, 14.35)}
ORIG_M = np.array([15.0, 14.45]); ROW_M = np.array([-1.0, 0.0]); AX_M = np.array([0.0, 1.0])
FACE_M_Z = 12.75  # bottom face
ORIG_W = np.array([26.55, 8.0]); ROW_W = np.array([0.0, 1.0]); AX_W = np.array([-1.0, 0.0])
FACE_W_Z = 14.35  # top face
POSTS = [(4.5, -6.0), (28.3, -6.0)]

def _box_uv(origin, row, ax, face_z, bottom_face, uu, vv, zz):
    """Box from B1-style local bounds (uu along row, vv along axis,
    zz from mounting face outward). Returns build123d solid."""
    c = origin + 0.5 * (uu[0] + uu[1]) * row + 0.5 * (vv[0] + vv[1]) * ax
    lx = abs(uu[1] - uu[0]); ly = abs(vv[1] - vv[0]); lz = zz[1] - zz[0]
    # local frame: row->X or Y; build axis-aligned by cases used here
    if abs(row[0]) > 0.5:  # row along X, axis along Y
        cx, cy = c[0], c[1]; sx, sy = lx, ly
    else:                  # row along Y, axis along X
        cx, cy = c[0], c[1]; sx, sy = ly, lx
    zc = face_z - 0.5 * (zz[0] + zz[1]) if bottom_face else face_z + 0.5 * (zz[0] + zz[1])
    return Pos(cx, cy, zc) * Box(sx, sy, lz)

def carrier_bodies(side='right'):
    """[(name, solid)] carrier + seat bodies for one side (assembly frame)."""
    out = []
    bx = BOARD
    board = Pos(0.5 * (bx['x'][0] + bx['x'][1]), 0.5 * (bx['y'][0] + bx['y'][1]),
                0.5 * (bx['z'][0] + bx['z'][1])) * Box(bx['x'][1] - bx['x'][0],
                bx['y'][1] - bx['y'][0], bx['z'][1] - bx['z'][0])
    out.append((f'carrier-{side}-board', board))
    hdr = ([-10.375, 10.375], [-1.6, 2.45], [0.1, 4.35])
    plg = ([-9.375, 9.375], [-0.15, 5.55], [0.2, 4.35])
    out.append((f'carrier-{side}-hdrM', _box_uv(ORIG_M, ROW_M, AX_M, FACE_M_Z, True, *hdr)))
    out.append((f'carrier-{side}-plugM', _box_uv(ORIG_M, ROW_M, AX_M, FACE_M_Z, True, *plg)))
    out.append((f'carrier-{side}-hdrW', _box_uv(ORIG_W, ROW_W, AX_W, FACE_W_Z, False, *hdr)))
    out.append((f'carrier-{side}-plugW', _box_uv(ORIG_W, ROW_W, AX_W, FACE_W_Z, False, *plg)))
    for j, (px, py) in enumerate(POSTS):
        out.append((f'seat-{side}-post{j}', Pos(px, py, 12.75 / 2) * Cylinder(3.5, 12.75)))
    if side == 'left':
        out = [(n, s.mirror(Plane.YZ)) for n, s in out]
    return out

def tail_M(i):
    uk = -8.125 + 1.25 * i
    p = ORIG_M + uk * ROW_M + 5.55 * AX_M
    return [float(p[0]), float(p[1]), 10.65]

def tail_W(i):
    uk = -8.125 + 1.25 * i
    p = ORIG_W + uk * ROW_W + 5.55 * AX_W
    return [float(p[0]), float(p[1]), 16.45]

# ---------------- segment points ----------------
def seg_points(D, i, side):
    """Returns (wing_pts, main_pts) in the requested side's frame."""
    d = D[str(i + 1)]
    wf = wing_fixed(i)
    ep, G, P = stations(i)
    TW = tail_W(i); TM = tail_M(i)
    apW = [TW[0] + 6.0 * AX_W[0], TW[1] + 6.0 * AX_W[1], TW[2]]
    apM = [TM[0] + 6.0 * AX_M[0], TM[1] + 6.0 * AX_M[1], TM[2]]
    wpts = wf + [[float(x) for x in p] for p in d['W']] + [apW, TW]
    mpts = [TM, apM] + [[float(x) for x in p] for p in d['N']] + \
           [P.tolist(), G.tolist(), ep.tolist()]
    if side == 'left':
        wpts = [[-p[0], p[1], p[2]] for p in wpts]
        mpts = [[-p[0], p[1], p[2]] for p in mpts]
    return wpts, mpts

def wire_name(seg, side, i):
    return f'{seg}-{side}-{i + 1:02d}'

def build_all(D):
    """{name: (solid, samples)}, {name: finished_len}, [failed]"""
    wires, lens, failed = {}, {}, []
    for side in ('right', 'left'):
        for i in range(14):
            wp, mp = seg_points(D, i, side)
            for seg, pts, un in (('SegW', wp, 7.30), ('SegM', mp, 6.80)):
                nm = wire_name(seg, side, i)
                pts = rr.split_corners(pts)
                r, why = R.build_s(pts)
                if r is None:
                    failed.append((nm, why)); continue
                w, L = F.build_wire(pts)
                wires[nm] = r
                lens[nm] = round(L + un, 2)
    return wires, lens, failed

def all_bodies():
    bodies = {}
    for p in (17, 16):
        bl = list(F.bodies_of(p))
        bl += carrier_bodies('right') + carrier_bodies('left')
        bodies[p] = bl
    return bodies

def full_score(D, bodies):
    wires, lens, failed = build_all(D)
    if failed:
        return {'failed': failed}
    solids = {n: r[0] for n, r in wires.items()}
    sc = F.Scorer(solids, bodies)
    ww = sc.ww_pairs()
    wf = {p: sc.wf_pairs(p) for p in bodies}
    return {'ww': ww, 'wf': {str(p): wf[p] for p in wf},
            'gate1_17': len(ww) + len(wf[17]), 'gate1_16': len(ww) + len(wf[16]),
            'ww_count': len(ww), 'wf_17': len(wf[17]), 'wf_16': len(wf[16]),
            'lens': lens, 'longest_seg': max(lens.values())}

def seed_design():
    """Seed free points from the incumbent round-18/frontier M chain."""
    M = json.load(open('/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/frontier/state_z1355.json'))['M']
    D = {}
    for i in range(14):
        m = M[str(i + 1)]
        W = []
        for k in ('M1', 'M2', 'M3'):
            if k in m: W.append([float(x) for x in m[k]])
        while len(W) < 3:
            W.append(list(W[-1]))
        W[2] = [W[2][0], W[2][1], W[2][2] + 2.5]
        ep, G, P = stations(i)
        TM = np.array(tail_M(i)); apM = TM + np.array([0.0, 6.0, 0.0])
        N1 = ((apM + np.array(P)) / 2 + np.array([0.0, 0.0, 0.3])).tolist()
        D[str(i + 1)] = {'W': W, 'N': [N1]}
    return D
