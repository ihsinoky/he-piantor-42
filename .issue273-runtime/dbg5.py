import sys, math
from pathlib import Path
import numpy as np
import pcbnew as p
from shapely.geometry import Polygon, Point
from shapely.affinity import rotate as shp_rotate, translate as shp_translate
MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
from notchain import wing_xf_factory
Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])
b5 = p.LoadBoard(str(Q263 / "wing-rev5-17mm-left/main.kicad_pcb"))
fwd, inv, jw = wing_xf_factory(b5, "left")
def to_case(poly):
    q = shp_translate(poly, xoff=-jw[0], yoff=-jw[1])
    q = shp_rotate(q, 30.5, origin=(0, 0))
    return shp_translate(q, xoff=-27.0, yoff=-37.5)
ring = [tuple(c) for c in to_case(outline_kicad(b5)).exterior.coords]
Tb = (-30.790, 51.622)
for i, c in enumerate(ring):
    if math.dist(c, (-29.93, 50.161)) < 0.01:
        for j in range(i - 2, i + 4):
            print(j, tuple(round(v, 3) for v in ring[j % len(ring)]))
        break
import math
best = []
for i in range(len(ring) - 1):
    a, b = np.array(ring[i]), np.array(ring[i + 1])
    ab = b - a
    t = float(np.clip(np.dot(np.array(Tb) - a, ab) / np.dot(ab, ab), 0, 1))
    q = a + ab * t
    best.append((float(np.linalg.norm(np.array(Tb) - q)), i, tuple(np.round(q, 3))))
best.sort()
print("nearest ring segs to Tb:", best[:3])
