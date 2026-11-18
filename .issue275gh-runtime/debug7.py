import sys
P248 = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, P248 + '/sources/frontier')
sys.path.insert(0, P248)
import common  # noqa
import fitlibF as FF

raw = dict(FF.bodies_at(17, -0.60))
for name in sorted(raw):
    if 'GH' in name or name in ('main', 'wing_right', 'wing_left') or 'EZmate' in name:
        b = raw[name].bounding_box()
        print(f'{name}: X {b.min.X:.2f}..{b.max.X:.2f}  Y {b.min.Y:.2f}..{b.max.Y:.2f}  Z {b.min.Z:.2f}..{b.max.Z:.2f}')
print('Rev.10 J3 site case: (24.255, 41.824); J2 site case: (-24.255, 41.824)')
