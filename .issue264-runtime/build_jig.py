"""Issue 264 folding jig (RIGHT side; left = mirrored print). build123d.
Base plate with a path groove following the folded plan, R2 corner former
pins at the fixed folds, a sliding S1 former block on detents (one per
cable-length class), stack fences along the S-pair run, Wing-tail end stop.
Units mm. PETG."""
import sys, math
import numpy as np
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime')
from build123d import Box, Pos, Rot, Cylinder, export_step, export_stl
from build_audit264 import path_V, catmull, seg_box, box_at

V = path_V(0.0)
pts = catmull(V)
# base plate: x -4..38, y -48..50, z 0..6
jig = box_at(17, 1, 3, 42, 98, 6)
# path groove: width 10.0, z 3.2..6.05 (fuse cutters, single cut)
groove = None
for a, b in zip(pts[:-1], pts[1:]):
    s = seg_box((a[0], a[1], 0), (b[0], b[1], 0), 10.0, 2.85, zoff=4.62, extra_len=1.0)
    if s is not None: groove = s if groove is None else groove.fuse(s)
jig = jig.cut(groove)
# stack fences along the S-pair run (line (11.79,-13)->(13.81,30.6))
mid = np.array([13.45, 9.80]); perp = np.array([0.99892, -0.04643])
for sgn in (1, -1):
    c = mid + sgn * 6.1 * perp
    fence = Pos(c[0], c[1], 8.25) * Rot(0, 0, 87.34) * Box(46, 1.6, 4.5)
    jig = jig.fuse(fence)
# corner former pins R2 at fixed folds A, B, V7 and at S2
for (x, y) in [(25.2, -15.0), (11.37, -22.0), (14.41, 30.60), (13.00, 0.43)]:
    pin = Pos(x, y, 7.0) * Cylinder(radius=2.0, height=8.0)
    jig = jig.fuse(pin)
# S1 slider rail slot along the run through S1 detents y=22.4..26.4
s1s = [(14.41 - (30.6 - y) * 0.04643, y) for y in (21.8, 22.8, 23.8, 24.8, 25.8)]  # detents for cable 148/150/152/154/156
rail_a = (s1s[0][0], s1s[0][1] - 4, 0); rail_b = (s1s[-1][0], s1s[-1][1] + 4, 0)
rail = seg_box(rail_a, rail_b, 8.0, 3.0, zoff=4.5, extra_len=0.0)
for (x, y) in s1s:  # detent notches
    notch = Pos(x, y, 5.5) * Rot(0, 0, 87.34) * Box(1.2, 10.0, 1.0)
    rail = rail.fuse(notch)
jig = jig.cut(rail)
# Wing-tail end stop (tip registers at y=-38.5)
jig = jig.fuse(box_at(27.0, -39.9, 8.5, 13, 2.6, 5.0))
# Main-end tip target pocket at T1 (22.6, 40.0)
jig = jig.cut(box_at(22.6, 40.6, 5.7, 11.0, 3.4, 0.7, yaw=-43.0))
# slider block (separate part): base + R2 pin + pointer
slider = box_at(0, 0, 1.5, 12, 10, 3.0)
slider = slider.fuse(Pos(0, 0, 5.5) * Cylinder(radius=2.0, height=5.0))
slider = slider.fuse(box_at(0, 5.6, 1.0, 1.6, 2.4, 2.0))

bb = jig.bounding_box()
vol = jig.volume
print('jig bbox:', [round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)])
print('jig volume cm3:', round(vol / 1000, 1), ' PETG mass g:', round(vol / 1000 * 1.27, 0))
sb = slider.bounding_box()
print('slider bbox:', [round(v, 1) for v in (sb.min.X, sb.min.Y, sb.min.Z, sb.max.X, sb.max.Y, sb.max.Z)], ' vol cm3:', round(slider.volume / 1000, 1))
export_step(jig, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime/jig-right.step')
export_stl(jig, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime/jig-right.stl')
export_step(slider, '/home/hatch/workspace/projects/he-piantor-stockffc/.issue264-runtime/jig-slider.step')
print('DONE')
