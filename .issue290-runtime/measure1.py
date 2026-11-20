import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
import fitlibF as FF
bodies = dict(FF.bodies_at(17, -2.65))
for n in ('tray-left','tray-right','plate-left','plate-right','shell-central'):
    bb = bodies[n].bounding_box()
    print(f'{n:16s} X {bb.min.X:8.2f}..{bb.max.X:8.2f}  Y {bb.min.Y:8.2f}..{bb.max.Y:8.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}')
for side in ('L','R'):
    for t in ('T0','T1','T2'):
        n = f'switch-envelope-{side}_{t}'
        bb = bodies[n].bounding_box()
        print(f'{n:16s} X {bb.min.X:8.2f}..{bb.max.X:8.2f}  Y {bb.min.Y:8.2f}..{bb.max.Y:8.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}')
for n in ('switch-envelope-L_R2_C0','switch-envelope-R_R2_C0','switch-envelope-L_R0_C0','switch-envelope-R_R0_C0'):
    bb = bodies[n].bounding_box()
    print(f'{n:24s} X {bb.min.X:8.2f}..{bb.max.X:8.2f}  Y {bb.min.Y:8.2f}..{bb.max.Y:8.2f}  Z {bb.min.Z:6.2f}..{bb.max.Z:6.2f}')
