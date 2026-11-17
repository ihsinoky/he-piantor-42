import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
import fitlib18 as F
import repair18_lib as R
from build123d import Pos, Solid

B = dict((n, s) for n, s in FF.bodies_at(17, -2.65)
         if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND'))
tray = B['tray-right']
bb = tray.bounding_box()
print('tray-right bbox', [round(v, 1) for v in (bb.min.X, bb.min.Y, bb.min.Z, bb.max.X, bb.max.Y, bb.max.Z)], 'vol', round(tray.volume, 0))
for (x, y) in [(14, 0), (14, 15), (14, 25), (12, -20), (25, -16), (18, 35), (27, -36)]:
    zs = []
    for zi in range(0, 52):
        z = zi * 0.25
        probe = Pos(x, y, z) * Solid.make_box(1.2, 1.2, 0.25)
        v = R.vol_pair(probe, tray, F.bounds(probe), F.bounds(tray), repair=False)
        if v > 0.01: zs.append(round(z, 2))
    # compress to intervals
    iv = []
    for z in zs:
        if iv and abs(z - iv[-1][1] - 0.25) < 0.01: iv[-1][1] = z
        else: iv.append([z, z])
    print(f'({x},{y}): tray material z intervals:', [(a, round(b + 0.25, 2)) for a, b in iv], flush=True)
print('DONE')
