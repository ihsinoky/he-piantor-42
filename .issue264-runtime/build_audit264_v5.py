"""Issue 264 fitted audit v5 (definitive). NO fuse operations anywhere:
- cable = Compound of segment/patch/roll boxes (v2 cable_boxes)
- channel = Compound of channel boxes; trays cut with the compound tool
  (v1/v3/v4's fused channel collapsed - tray pairs from those runs are
  superseded by this run; non-tray pairs are unaffected by the channel)
- left = build123d mirror of the right compound
Classification as v4: 'underside-*-J_WING' contacts = own termination."""
import json, sys
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B1
import build_audit264_v2 as V2
import fitlibF as FF
import fitlib18 as F
import repair18_lib as R
from build123d import mirror, Plane, Compound, export_step

RT = '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime'

def channel_boxes(w=9.6, t=0.32, patch_th=0.30, s1_dy=0.0, sx=1):
    V = B1.path_V(s1_dy, sx)
    pts = B1.catmull(V)
    boxes = [s for a, b in zip(pts[:-1], pts[1:])
             if (s := B1.seg_box(a, b, 11.4, t + 0.525, zoff=0.0375, extra_len=1.2)) is not None]
    for idx, Lp, tag in B1.FOLDS:
        c = np.array(V[idx], float)
        hh = t + patch_th + 0.525
        zoff = ((c[2]-t/2-patch_th-0.225) + (c[2]+t/2+0.30)) / 2 - c[2]
        for j in (idx-1, idx):
            a, b = np.array(V[j], float), np.array(V[j+1], float)
            d = b - a; u = d / np.linalg.norm(d)
            p0 = c - u * (Lp/2) if j == idx-1 else c
            p1 = c if j == idx-1 else c + u * (Lp/2)
            s = B1.seg_box(p0, p1, 11.4, hh, zoff=zoff, extra_len=1.2)
            if s is not None: boxes.append(s)
    for (vx, vy), zb, zt, tag in B1.rolls(s1_dy, sx):
        boxes.append(B1.box_at(vx, vy, (zb-0.225+zt+0.30)/2, 11.4, 5.2, (zt+0.30)-(zb-0.225)))
    return boxes

def assemble_v5(s1_dy=0.0, w=9.6, t=0.32, patch_th=0.30):
    zifs = B1.make_zifs()
    bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
              if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
    bodies += list(zifs.items())
    chan_r = Compound(children=channel_boxes(w, t, patch_th, s1_dy, sx=1))
    chan_l = mirror(chan_r, about=Plane.YZ)
    out = []
    for n, s in bodies:
        if n == 'tray-right':
            v0 = s.volume; s = s.cut(chan_r)
            print('tray-right cut delta:', round(v0 - s.volume, 1), flush=True)
        elif n == 'tray-left':
            v0 = s.volume; s = s.cut(chan_l)
            print('tray-left cut delta:', round(v0 - s.volume, 1), flush=True)
        out.append((n, s))
    cable_r = Compound(children=V2.cable_boxes(w, t, patch_th, s1_dy, sx=1))
    cable_l = mirror(cable_r, about=Plane.YZ)
    return out, cable_r, cable_l, zifs

def audit_classified(solid, body_list):
    hits, own = [], []
    bb = solid.bounding_box()
    for n, bs in body_list:
        b2 = bs.bounding_box()
        if (bb.max.X < b2.min.X - 1 or bb.min.X > b2.max.X + 1 or
            bb.max.Y < b2.min.Y - 1 or bb.min.Y > b2.max.Y + 1 or
            bb.max.Z < b2.min.Z - 1 or bb.min.Z > b2.max.Z + 1):
            continue
        v = R.vol_pair(solid, bs, F.bounds(solid), F.bounds(bs), repair=True)
        if v > F.HIT:
            (own if 'J_WING' in n else hits).append((n, round(float(v), 4)))
    return hits, own

if __name__ == '__main__':
    res = {}
    for tag, kw in (('base', {}), ('sensN', dict(s1_dy=2.0, w=10.4, patch_th=0.35)),
                    ('sensS', dict(s1_dy=-2.6, w=10.4, patch_th=0.35))):
        bodies, cable_r, cable_l, zifs = assemble_v5(**kw)
        for side, cable in (('right', cable_r), ('left', cable_l)):
            h, o = audit_classified(cable, bodies)
            res[f'gate1_{tag}_{side}'] = h
            res[f'ownterm_{tag}_{side}'] = o
            print(f'{tag} {side}: gate1={h} own-termination={o}', flush=True)
        if tag == 'base':
            res['cable_vs_cable'] = float(R.vol_pair(cable_r, cable_l, F.bounds(cable_r), F.bounds(cable_l), repair=True))
            print('cable_vs_cable:', res['cable_vs_cable'], flush=True)
            export_step(Compound(children=[cable_r, cable_l] + list(zifs.values())), f'{RT}/preview264.step')
    json.dump(res, open(f'{RT}/audit264_v5.json', 'w'), indent=1)
    print('DONE', flush=True)
