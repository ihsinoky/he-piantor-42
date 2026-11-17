"""Reliable channel solid: segment boxes only (volumetric overlaps, no
coplanar patch/roll boxes). Segments near fold patches / rolls use the
taller profile. Fuse pattern proven on the jig groove."""
import sys, math
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
import build_audit264 as B1

def channel_solid_v6(w=9.6, t=0.32, patch_th=0.30, s1_dy=0.0, sx=1):
    V = B1.path_V(s1_dy, sx)
    pts = B1.catmull(V)
    # zone test: distance from a spline point to fold vertices / roll centres
    fold_xy = [V[i] for i, _, _ in B1.FOLDS]
    roll_xy = [(x, y) for (x, y), _, _, _ in B1.rolls(s1_dy, sx)]
    def zone_h(p):
        for (fx, fy, fz) in fold_xy:
            if math.hypot(p[0]-fx, p[1]-fy) < 8.0:
                return t + patch_th + 0.525, ((fz-t/2-patch_th-0.225) + (fz+t/2+0.30)) / 2 - fz
        for (rx, ry) in roll_xy:
            if math.hypot(p[0]-rx, p[1]-ry) < 4.0:
                return None, None  # handled by roll box below (single box, fused volumetrically)
        return t + 0.525, 0.0375
    solids = []
    for a, b in zip(pts[:-1], pts[1:]):
        mid = (np.array(a) + np.array(b)) / 2
        h, zo = zone_h(mid)
        if h is None: continue
        s = B1.seg_box(a, b, 11.4, h, zoff=zo, extra_len=1.2)
        if s is not None: solids.append(s)
    for (vx, vy), zb, zt, tag in B1.rolls(s1_dy, sx):
        solids.append(B1.box_at(vx, vy, (zb-0.225+zt+0.30)/2, 12.4, 6.2, (zt+0.30)-(zb-0.225)))
    acc = solids[0]
    for s in solids[1:]:
        acc = acc.fuse(s)
    return acc

if __name__ == '__main__':
    import fitlibF as FF
    chan = channel_solid_v6()
    print('channel vol:', round(chan.volume, 1), 'solids:', len(chan.solids()))
    B = dict((n, s) for n, s in FF.bodies_at(17, -2.65)
             if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND'))
    tray = B['tray-right']
    v0 = tray.volume
    cut = tray.cut(chan)
    print('tray vol:', round(v0, 1), '-> cut:', round(cut.volume, 1), 'delta:', round(v0 - cut.volume, 1))
