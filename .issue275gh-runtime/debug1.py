import sys, traceback
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-raise/.issue248-runtime/caddeps')
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-ghcheck/hardware/case/issue-232-final')
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb/sources/frontier")
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb")
from geometry import tube
from build123d import Box, Pos
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

pts = [(27.0, -34.5, 5.15), (27.0, -27.0, 4.30), (26.0, -13.0, 2.60), (26.0, 16.0, 2.60)]
w1, p1 = tube([list(p) for p in pts], 0.5)
pts2 = [(28.25, -34.5, 5.15), (28.25, -27.0, 4.30), (27.05, -13.0, 2.60), (27.05, 16.0, 2.60)]
w2, p2 = tube([list(p) for p in pts2], 0.5)
print('type w1:', type(w1), 'vol:', float(w1.volume), 'len:', float(p1.length))
print('bbox w1:', w1.bounding_box().min, w1.bounding_box().max)
d = BRepExtrema_DistShapeShape(w1.wrapped, w2.wrapped); d.Perform()
print('extrema w1-w2 (expect ~0.05):', d.IsDone(), float(d.Value()))
try:
    c = w1.intersect(w2)
    print('intersect type:', type(c), 'vol:', None if c is None else float(c.volume))
except Exception:
    traceback.print_exc()
box = Pos(26, 0, 0.75) * Box(20, 40, 2.5)
try:
    c2 = w1.intersect(box)
    print('wire-box intersect vol (expect 0):', None if c2 is None else float(c2.volume))
except Exception:
    traceback.print_exc()
