import sys, traceback
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/caddeps')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-ghcheck/hardware/case/issue-232-final')
import geometry
print('geometry module:', geometry.__file__)
import fitlibF as FF
print('fitlibF:', FF.__file__)
from geometry import tube
from build123d import Box, Pos

raw = dict(FF.bodies_at(17, -0.60))
plug = raw['underside-right-J_WING']
print('plug type:', type(plug), 'vol:', float(plug.volume))
floor = Pos(0, 0, 0.55) * Box(120, 112, 2.1)  # top 1.60
try:
    c = plug.intersect(floor)
    print('plug-floor intersect:', None if c is None else float(c.volume))
except Exception:
    traceback.print_exc()
# shifted-down plug (s=-2.65 -> plate 10.90): translate Z by -2.65
plug2 = Pos(0, 0, -2.65) * plug
try:
    c2 = plug2.intersect(floor)
    print('plug@10.90-floor intersect (must be >0):', None if c2 is None else float(c2.volume))
except Exception:
    traceback.print_exc()
# tube vs tube known case
w1, _ = tube([[27.0, -34.5, 5.15], [27.0, -27.0, 4.30], [26.0, -13.0, 2.60], [26.0, 16.0, 2.60]], 0.5)
w1d = Pos(0, 0, -3.0) * w1
try:
    c3 = w1d.intersect(floor)
    print('shifted wire-floor intersect (must be >0):', None if c3 is None else float(c3.volume))
except Exception:
    traceback.print_exc()
