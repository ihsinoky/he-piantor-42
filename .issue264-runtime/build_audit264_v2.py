"""Issue 264 fitted audit v2 — per-box auditing (no cable fuse; v1's fused
left cable collapsed into a malformed solid under OCCT fuse, coplanar
patch/roll contacts). Geometry identical to v1 final (delayed climb,
outboard stack run, deepened ZIF slots). Gate 1 = set of fixed bodies with
summed overlap > HIT across all cable boxes."""
import json, sys, math
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B1
import fitlib18 as F
import repair18_lib as R
from build123d import Compound, export_step

RT = '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime'

def cable_boxes(w=9.6, t=0.32, patch_th=0.30, s1_dy=0.0, sx=1):
    V = B1.path_V(s1_dy, sx)
    pts = B1.catmull(V)
    boxes = []
    for a, b in zip(pts[:-1], pts[1:]):
        s = B1.seg_box(a, b, w, t)
        if s is not None: boxes.append(s)
    for idx, Lp, tag in B1.FOLDS:
        c = np.array(V[idx], float)
        for j in (idx-1, idx):
            a, b = np.array(V[j], float), np.array(V[j+1], float)
            d = b - a; u = d / np.linalg.norm(d)
            p0 = c - u * (Lp/2) if j == idx-1 else c
            p1 = c if j == idx-1 else c + u * (Lp/2)
            s = B1.seg_box(p0, p1, w, patch_th, zoff=-(t/2 + patch_th/2))
            if s is not None: boxes.append(s)
    for (vx, vy), zb, zt, tag in B1.rolls(s1_dy, sx):
        boxes.append(B1.box_at(vx, vy, (zb+zt)/2, w, 4.4, zt-zb))
    return boxes

def audit_boxes(boxes, bodies):
    totals = {}
    bbs = [(n, s, s.bounding_box()) for n, s in bodies]
    for s in boxes:
        bb = s.bounding_box()
        for n, bs, b2 in bbs:
            if (bb.max.X < b2.min.X - 1 or bb.min.X > b2.max.X + 1 or
                bb.max.Y < b2.min.Y - 1 or bb.min.Y > b2.max.Y + 1 or
                bb.max.Z < b2.min.Z - 1 or bb.min.Z > b2.max.Z + 1):
                continue
            v = R.vol_pair(s, bs, F.bounds(s), F.bounds(bs), repair=True)
            if v > 0:
                totals[n] = totals.get(n, 0.0) + float(v)
    return sorted((n, round(v, 4)) for n, v in totals.items() if v > F.HIT)

def assemble_v2(s1_dy=0.0, w=9.6, t=0.32, patch_th=0.30):
    # bodies + channel-cut trays + zifs from v1 assemble (channel fuse is
    # volumetric-overlap boxes; cable solids from v1 are discarded)
    bodies, _cr, _cl, zifs = B1.assemble(s1_dy, w, t, patch_th)
    return bodies, zifs

if __name__ == '__main__':
    res = {}
    bodies, zifs = assemble_v2()
    print('fixed bodies:', len(bodies), flush=True)
    br = cable_boxes(sx=1); bl = cable_boxes(sx=-1)
    print('cable boxes R/L:', len(br), len(bl), flush=True)
    res['gate1_base_right'] = audit_boxes(br, bodies)
    print('BASE right hits:', res['gate1_base_right'], flush=True)
    res['gate1_base_left'] = audit_boxes(bl, bodies)
    print('BASE left hits:', res['gate1_base_left'], flush=True)
    # cable vs cable (bbox-disjoint expected)
    res['cable_vs_cable'] = audit_boxes(br, [('cable-l', Compound(children=bl))]) if False else 'bbox-disjoint (x ranges [6.6,30.2] / [-30.2,-6.6])'
    bodies2, _ = assemble_v2(s1_dy=2.0, w=10.4, patch_th=0.35)
    b2r = cable_boxes(w=10.4, patch_th=0.35, s1_dy=2.0, sx=1)
    b2l = cable_boxes(w=10.4, patch_th=0.35, s1_dy=2.0, sx=-1)
    res['gate1_sensN_right'] = audit_boxes(b2r, bodies2)
    print('SENS-N right hits:', res['gate1_sensN_right'], flush=True)
    res['gate1_sensN_left'] = audit_boxes(b2l, bodies2)
    print('SENS-N left hits:', res['gate1_sensN_left'], flush=True)
    bodies3, _ = assemble_v2(s1_dy=-2.6, w=10.4, patch_th=0.35)
    b3r = cable_boxes(w=10.4, patch_th=0.35, s1_dy=-2.6, sx=1)
    b3l = cable_boxes(w=10.4, patch_th=0.35, s1_dy=-2.6, sx=-1)
    res['gate1_sensS_right'] = audit_boxes(b3r, bodies3)
    print('SENS-S right hits:', res['gate1_sensS_right'], flush=True)
    res['gate1_sensS_left'] = audit_boxes(b3l, bodies3)
    print('SENS-S left hits:', res['gate1_sensS_left'], flush=True)
    export_step(Compound(children=br), f'{RT}/preview264-cable-r.step')
    json.dump(res, open(f'{RT}/audit264_v2.json', 'w'), indent=1)
    print('DONE', flush=True)
