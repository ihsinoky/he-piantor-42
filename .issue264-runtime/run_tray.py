"""Tray-pair evaluation without Cut/Fuse: residual = vol(cable n tray_uncut)
- vol((cable n tray_uncut) n channel). All Common-based (audit_repair).
Configs: base, sensN, sensS x both sides; plus service drape poses
(static, B+2.5, B+5.0) at base geometry."""
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

def tray_residual(cable, tray, chan):
    v1 = R.vol_pair(cable, tray, F.bounds(cable), F.bounds(tray), repair=True)
    if v1 <= F.HIT:
        return float(v1), float(v1), 0.0
    inter = AR.common_shape(cable, tray)
    vi = AR.shape_volume(inter)
    inter_b = Shape.cast(inter)
    v2 = AR.shape_volume(AR.common_shape(inter_b, chan))
    return float(v1), vi, max(0.0, vi - v2)

def bodies_uncut():
    bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
              if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
    return dict(bodies)

res = {}
B = bodies_uncut()
for tag, kw in (('base', {}), ('sensN', dict(s1_dy=2.0, w=10.4, patch_th=0.35)),
                ('sensS', dict(s1_dy=-2.6, w=10.4, patch_th=0.35))):
    w = kw.get('w', 9.6); t = kw.get('t', 0.32); pt = kw.get('patch_th', 0.30); dy = kw.get('s1_dy', 0.0)
    chan_r = Compound(children=V5.channel_boxes(w, t, pt, dy, sx=1))
    chan_l = mirror(chan_r, about=Plane.YZ)
    cable_r = Compound(children=V2.cable_boxes(w, t, pt, dy, sx=1))
    cable_l = mirror(cable_r, about=Plane.YZ)
    for side, cable, tray, chan in (('right', cable_r, B['tray-right'], chan_r),
                                    ('left', cable_l, B['tray-left'], chan_l)):
        v1, vi, resid = tray_residual(cable, tray, chan)
        res[f'tray_{tag}_{side}'] = {'overlap_uncut': round(v1, 3), 'inter_vol': round(vi, 3), 'residual_after_channel': round(resid, 4)}
        print(f'{tag} {side}: overlap={v1:.3f} inter={vi:.3f} residual={resid:.4f}', flush=True)
# service drape poses (base geometry)
w, t, pt = 9.6, 0.32, 0.30
chan_r = Compound(children=V5.channel_boxes(w, t, pt, 0.0, sx=1))
V = B1.path_V(0.0)
drapeV = V[:13] + [(17.47, 33.89, 6.24), (20.47, 36.89, 5.99)]
pts = B1.catmull(drapeV)
drape = Compound(children=[s for a, b in zip(pts[:-1], pts[1:]) if (s := B1.seg_box(a, b, w, t)) is not None])
for tag, dx, dy, dz in (('drape-static', 0, 0, 0), ('B0,0,2.5', 0, 0, 2.5), ('B0,0,5.0', 0, 0, 5.0)):
    moved = Pos(dx, dy, dz) * drape if (dx, dy, dz) != (0, 0, 0) else drape
    chan_m = Pos(dx, dy, dz) * chan_r if (dx, dy, dz) != (0, 0, 0) else chan_r
    # NOTE: the channel is in the TRAY (fixed); it does NOT move with the cable.
    v1, vi, resid = tray_residual(moved, B['tray-right'], chan_r)
    res[f'tray_service_{tag}'] = {'overlap_uncut': round(v1, 3), 'inter_vol': round(vi, 3), 'residual_after_channel': round(resid, 4)}
    print(f'service {tag}: overlap={v1:.3f} inter={vi:.3f} residual={resid:.4f}', flush=True)
json.dump(res, open(f'{RT}/tray_eval.json', 'w'), indent=1)
print('DONE', flush=True)
