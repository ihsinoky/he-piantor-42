import sys, traceback
P248 = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, P248 + '/sources/frontier')
sys.path.insert(0, P248)
import common
print('common ROOT:', common.ROOT)
import geometry
print('geometry module:', geometry.__file__)
import fitlibF as FF
from geometry import tube
from build123d import Box, Pos

raw = dict(FF.bodies_at(17, -0.60))
plug = raw['underside-right-J_WING']
print('plug type:', type(plug).__name__, 'vol:', round(float(plug.volume), 2))
b = plug.bounding_box()
print('plug bbox Z:', round(b.min.Z, 2), round(b.max.Z, 2))
floor = Pos(0, 0, 0.55) * Box(120, 112, 2.1)  # top 1.60
try:
    c = plug.intersect(floor)
    print('plug(12.95)-floor intersect (expect 0/None):', None if c is None else float(c.volume))
except Exception:
    traceback.print_exc()
plug2 = Pos(0, 0, -2.65) * plug
try:
    c2 = plug2.intersect(floor)
    print('plug@10.90-floor intersect (must be >0):', None if c2 is None else round(float(c2.volume), 2))
except Exception:
    traceback.print_exc()
w1, _ = tube([[27.0, -34.5, 5.15], [27.0, -27.0, 4.30], [26.0, -13.0, 2.60], [26.0, 16.0, 2.60]], 0.5)
w1d = Pos(0, 0, -3.0) * w1
try:
    c3 = w1d.intersect(floor)
    print('shifted wire-floor intersect (must be >0):', None if c3 is None else round(float(c3.volume), 2))
except Exception:
    traceback.print_exc()
try:
    c4 = w1.intersect(floor)
    print('wire-floor intersect (expect 0/None):', None if c4 is None else float(c4.volume))
except Exception:
    traceback.print_exc()
