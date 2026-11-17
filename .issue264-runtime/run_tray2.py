"""Tray-pair evaluation v2: per-box. For each cable box: overlap with the
UNCUT tray (repaired vol_pair), minus the part of that overlap lying inside
the channel compound (exact Commons via audit_repair). Sum = upper-bound
residual (joint double-counts inflate both terms consistently)."""
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

RT = '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime'
B = dict((n, s) for n, s in FF.bodies_at(17, -2.65)
         if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND'))

def box_residual(box, tray, chan):
    v = R.vol_pair(box, tray, F.bounds(box), F.bounds(tray), repair=True)
    if v <= 0:
        return 0.0, 0.0
    inter = AR.common_shape(box, tray)
    vi = AR.shape_volume(inter)
    if vi <= 0:
        return 0.0, float(v)
    relieved = AR.shape_volume(AR.common_shape(Shape.cast(inter), chan))
    return max(0.0, vi - relieved), vi

def eval_side(boxes, tray, chan, tag):
    tb = tray.bounding_box()
    tot_r, tot_o, hits = 0.0, 0.0, []
    for i, box in enumerate(boxes):
        bb = box.bounding_box()
        if (bb.max.X < tb.min.X - 0.5 or bb.min.X > tb.max.X + 0.5 or
            bb.max.Y < tb.min.Y - 0.5 or bb.min.Y > tb.max.Y + 0.5 or
            bb.max.Z < tb.min.Z - 0.5 or bb.min.Z > tb.max.Z + 0.5):
            continue
        r, o = box_residual(box, tray, chan)
        tot_r += r; tot_o += o
        if r > 0.001:
            c = bb.center()
            hits.append((i, round(float(c.X), 1), round(float(c.Y), 1), round(float(c.Z), 2), round(o, 3), round(r, 4)))
    print(f'{tag}: overlap_sum={tot_o:.3f} residual_sum={tot_r:.4f} residual_boxes={hits}', flush=True)
    return {'overlap_sum': round(tot_o, 3), 'residual_sum': round(tot_r, 4), 'residual_boxes': hits}

res = {}
for tag, kw in (('base', {}), ('sensN', dict(s1_dy=2.0, w=10.4, patch_th=0.35)),
                ('sensS', dict(s1_dy=-2.6, w=10.4, patch_th=0.35))):
    w = kw.get('w', 9.6); t = kw.get('t', 0.32); pt = kw.get('patch_th', 0.30); dy = kw.get('s1_dy', 0.0)
    chan_r = Compound(children=V5.channel_boxes(w, t, pt, dy, sx=1))
    chan_l = mirror(chan_r, about=Plane.YZ)
    boxes_r = V2.cable_boxes(w, t, pt, dy, sx=1)
    boxes_l = V2.cable_boxes(w, t, pt, dy, sx=-1)
    res[f'tray_{tag}_right'] = eval_side(boxes_r, B['tray-right'], chan_r, f'{tag} right')
    res[f'tray_{tag}_left'] = eval_side(boxes_l, B['tray-left'], chan_l, f'{tag} left')
# service drape poses vs tray-right (channel fixed in tray)
w, t, pt = 9.6, 0.32, 0.30
chan_r = Compound(children=V5.channel_boxes(w, t, pt, 0.0, sx=1))
V = B1.path_V(0.0)
drapeV = V[:13] + [(17.47, 33.89, 6.24), (20.47, 36.89, 5.99)]
pts = B1.catmull(drapeV)
dboxes = [s for a, b in zip(pts[:-1], pts[1:]) if (s := B1.seg_box(a, b, w, t)) is not None]
for tag, dz in (('drape-static', 0), ('B+2.5', 2.5), ('B+5.0', 5.0)):
    moved = [Pos(0, 0, dz) * s for s in dboxes] if dz else dboxes
    res[f'tray_service_{tag}'] = eval_side(moved, B['tray-right'], chan_r, f'service {tag}')
json.dump(res, open(f'{RT}/tray_eval2.json', 'w'), indent=1)
print('DONE', flush=True)
