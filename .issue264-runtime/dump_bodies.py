import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
import fitlibF as FF
out = []
for n, s in FF.bodies_at(17, -2.65):
    bb = s.bounding_box()
    out.append((n, round(bb.min.X,2), round(bb.max.X,2), round(bb.min.Y,2), round(bb.max.Y,2), round(bb.min.Z,2), round(bb.max.Z,2)))
for row in sorted(out, key=lambda r: r[0]):
    print(row)
