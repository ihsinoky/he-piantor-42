"""Final verification bundle:
(1) Containment: every cable box's 8 corners + centre inside (tol 0.06)
    some channel box, for base/sensN/sensS, right side (left = mirror).
(2) Sensitivity non-tray gate 1: compound cable vs all bodies EXCEPT
    trays (tray pairs closed by containment), J_WING classified as own
    termination. Base non-tray already proven by v4 compound run.
(3) Service tray classification: drape boxes at static/B+2.5/B+5.0 and
    tip at A5.0 - overlap vs uncut tray-right; overlapping boxes get the
    overlap-bbox corner containment test vs the fixed channel."""
import json, sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B1
import build_audit264_v2 as V2
import build_audit264_v5 as V5
import fitlibF as FF
import fitlib18 as F
import repair18_lib as R
import audit_repair as AR
from build123d import mirror, Plane, Compound, Shape, Pos
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.gp import gp_Pnt
from OCP.TopAbs import TopAbs_IN, TopAbs_ON

RT = '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime'

def point_in_solid(p, solid, tol=0.06):
    cl = BRepClass3d_SolidClassifier(solid.wrapped, gp_Pnt(p[0], p[1], p[2]), tol)
    return cl.State() in (TopAbs_IN, TopAbs_ON)

def box_points(bb):
    xs = [bb.min.X, bb.max.X]; ys = [bb.min.Y, bb.max.Y]; zs = [bb.min.Z, bb.max.Z]
    pts = [(x, y, z) for x in xs for y in ys for z in zs]
    c = bb.center(); pts.append((c.X, c.Y, c.Z))
    return pts

def containment(cable_boxes, chan_boxes):
    chan_bb = [(s, s.bounding_box()) for s in chan_boxes]
    fails = []
    for i, box in enumerate(cable_boxes):
        bb = box.bounding_box()
        cands = [s for s, b2 in chan_bb if not (bb.max.X < b2.min.X - 0.5 or bb.min.X > b2.max.X + 0.5 or
                 bb.max.Y < b2.min.Y - 0.5 or bb.min.Y > b2.max.Y + 0.5 or
                 bb.max.Z < b2.min.Z - 0.5 or bb.min.Z > b2.max.Z + 0.5)]
        for p in box_points(bb):
            if not any(point_in_solid(p, s) for s in cands):
                fails.append((i, tuple(round(v, 1) for v in p)))
                break
    return fails

res = {}
configs = (('base', {}), ('sensN', dict(s1_dy=2.0, w=10.4, patch_th=0.35)),
           ('sensS', dict(s1_dy=-2.6, w=10.4, patch_th=0.35)))
for tag, kw in configs:
    w = kw.get('w', 9.6); t = kw.get('t', 0.32); pt = kw.get('patch_th', 0.30); dy = kw.get('s1_dy', 0.0)
    cb = V2.cable_boxes(w, t, pt, dy, sx=1)
    chb = V5.channel_boxes(w, t, pt, dy, sx=1)
    fails = containment(cb, chb)
    res[f'containment_{tag}'] = fails
    print(f'containment {tag}: {len(cb)} cable boxes, fails={fails}', flush=True)

# (2) sensitivity non-tray audit
bodies_all = [(n, s) for n, s in FF.bodies_at(17, -2.65)
              if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
zifs = B1.make_zifs()
bodies_all += list(zifs.items())
bodies_nt = [(n, s) for n, s in bodies_all if not n.startswith('tray')]
for tag, kw in configs[1:]:
    w = kw.get('w', 9.6); t = kw.get('t', 0.32); pt = kw.get('patch_th', 0.30); dy = kw.get('s1_dy', 0.0)
    cable_r = Compound(children=V2.cable_boxes(w, t, pt, dy, sx=1))
    cable_l = mirror(cable_r, about=Plane.YZ)
    for side, cable in (('right', cable_r), ('left', cable_l)):
        h, o = V5.audit_classified(cable, bodies_nt)
        res[f'gate1nt_{tag}_{side}'] = h
        res[f'ownterm_{tag}_{side}'] = o
        print(f'{tag} {side} non-tray: gate1={h} own={o}', flush=True)

# (3) service tray classification
B = dict(bodies_all)
tray = B['tray-right']
chan_boxes = V5.channel_boxes(9.6, 0.32, 0.30, 0.0, sx=1)
chan_bb = [(s, s.bounding_box()) for s in chan_boxes]
V = B1.path_V(0.0)
drapeV = V[:13] + [(17.47, 33.89, 6.24), (20.47, 36.89, 5.99)]
pts = B1.catmull(drapeV)
dboxes = [s for a, b in zip(pts[:-1], pts[1:]) if (s := B1.seg_box(a, b, 9.6, 0.32)) is not None]
tipV = [(14.41, 30.60, 7.54), (16.35, 32.89, 7.22), (20.92, 38.24, 6.90), (22.6, 40.0, 6.90)]
tpts = B1.catmull(tipV)
tip_boxes = [s for a, b in zip(tpts[:-1], tpts[1:]) if (s := B1.seg_box(a, b, 9.6, 0.32)) is not None]
poses = [('drape-static', dboxes, (0, 0, 0)), ('drape-B+2.5', dboxes, (0, 0, 2.5)),
         ('drape-B+5.0', dboxes, (0, 0, 5.0)), ('tip-A5.0', tip_boxes, (-0.68 * 5.0, -0.73 * 5.0, 0))]
for tag, boxes, (dx, dy, dz) in poses:
    moved = [Pos(dx, dy, dz) * s for s in boxes] if (dx, dy, dz) != (0, 0, 0) else boxes
    tb = tray.bounding_box()
    real, relieved = [], []
    for i, box in enumerate(moved):
        bb = box.bounding_box()
        if (bb.max.X < tb.min.X - 0.5 or bb.min.X > tb.max.X + 0.5 or bb.max.Y < tb.min.Y - 0.5 or
            bb.min.Y > tb.max.Y + 0.5 or bb.max.Z < tb.min.Z - 0.5 or bb.min.Z > tb.max.Z + 0.5):
            continue
        v = R.vol_pair(box, tray, F.bounds(box), F.bounds(tray), repair=True)
        if v <= 0: continue
        inter = AR.common_shape(box, tray)
        ib = Shape.cast(inter).bounding_box()
        cands = [s for s, b2 in chan_bb if not (ib.max.X < b2.min.X - 0.5 or ib.min.X > b2.max.X + 0.5 or
                 ib.max.Y < b2.min.Y - 0.5 or ib.min.Y > b2.max.Y + 0.5 or
                 ib.max.Z < b2.min.Z - 0.5 or ib.min.Z > b2.max.Z + 0.5)]
        inside = all(any(point_in_solid(p, s) for s in cands) for p in box_points(ib))
        (relieved if inside else real).append((i, round(float(v), 3)))
    res[f'service_tray_{tag}'] = {'real': real, 'relieved_by_channel': relieved}
    print(f'service tray {tag}: real={real} relieved={relieved}', flush=True)
json.dump(res, open(f'{RT}/final_eval.json', 'w'), indent=1, default=str)
print('DONE', flush=True)
