"""Issue 264 fitted audit v4 (definitive) - cable as a Compound of its
segment/patch/roll boxes (no fuse anywhere on the cable; Common over a
compound is exact). Bodies + channel-cut trays + ZIF envelopes as v3.
Classification: contacts vs 'underside-*-J_WING' are the cable's OWN
termination at its connector site (project classification since #248:
'own GH termination, nominal bounded outlet') - reported separately,
not gate-1 failures. Gate 1 = all other unexpected contacts."""
import json, sys
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

def assemble_v4(s1_dy=0.0, w=9.6, t=0.32, patch_th=0.30):
    zifs = B1.make_zifs()
    bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
              if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
    bodies += list(zifs.items())
    chan_r = B1.build_channel(w, t, patch_th, s1_dy, sx=1)
    chan_l = mirror(chan_r, about=Plane.YZ)
    print('channel vols R/L:', round(chan_r.volume, 1), round(chan_l.volume, 1), flush=True)
    out = []
    for n, s in bodies:
        if n == 'tray-right': s = s.cut(chan_r)
        elif n == 'tray-left': s = s.cut(chan_l)
        out.append((n, s))
    boxes_r = V2.cable_boxes(w, t, patch_th, s1_dy, sx=1)
    cable_r = Compound(children=boxes_r)
    cable_l = mirror(cable_r, about=Plane.YZ)
    return out, cable_r, cable_l, zifs

def audit_classified(name, solid, body_list):
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
        bodies, cable_r, cable_l, zifs = assemble_v4(**kw)
        for side, cable in (('right', cable_r), ('left', cable_l)):
            h, o = audit_classified(f'cable_{side}', cable, bodies)
            res[f'gate1_{tag}_{side}'] = h
            res[f'ownterm_{tag}_{side}'] = o
            print(f'{tag} {side}: gate1={h} own-termination={o}', flush=True)
        if tag == 'base':
            res['cable_vs_cable'] = float(R.vol_pair(cable_r, cable_l, F.bounds(cable_r), F.bounds(cable_l), repair=True))
            print('cable_vs_cable:', res['cable_vs_cable'], flush=True)
            export_step(Compound(children=[cable_r, cable_l] + list(zifs.values())), f'{RT}/preview264.step')
    json.dump(res, open(f'{RT}/audit264_v4.json', 'w'), indent=1)
    print('DONE', flush=True)
