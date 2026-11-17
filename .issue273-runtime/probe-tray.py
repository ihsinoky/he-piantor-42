import sys
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/round18')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-wingnotch/.issue273-runtime')
import fitlibF as FF
import audit_repair as AR
from build123d import Shape

def vol(s):
    try: return float(s.volume)
    except Exception: return sum(float(x.volume) for x in s.solids())

def bb(s):
    b = s.bounding_box()
    return (round(b.min.X,2), round(b.min.Y,2), round(b.min.Z,2), round(b.max.X,2), round(b.max.Y,2), round(b.max.Z,2))

bodies = dict(FF.bodies_at(17, -2.65))
for n in ('tray-left','tray-right','wing_left','wing_right'):
    print(n, 'bbox', bb(bodies[n]), 'vol', round(vol(bodies[n]),1))
for a,b in (('tray-left','wing_right'),('tray-left','wing_left'),('tray-right','wing_right'),('tray-right','wing_left'),('tray-left','tray-right')):
    inter = AR.common_shape(bodies[a], bodies[b])
    v = vol(Shape.cast(inter)) if inter is not None else 0.0
    print(f'{a} x {b}: {v:.3f} mm3', ('bbox '+str(bb(Shape.cast(inter)))) if v>0.005 else '')
