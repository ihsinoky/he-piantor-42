import sys, math
sys.path.insert(0, ".issue270-runtime")
import pcbnew as p
from geom2b import xy
from shapely.geometry import LineString
from shapely.ops import unary_union, polygonize
MM = 1e6
b = p.LoadBoard("hardware/kicad/qualification/issue-270-main-rev9/main-rev9/main.kicad_pcb")
segs = []
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts and d.GetShape() == p.SHAPE_T_ARC:
        c = d.GetCenter(); r = d.GetRadius() / MM
        a0 = math.atan2(d.GetStart().y - c.y, d.GetStart().x - c.x)
        m = d.GetArcMid(); a1 = math.atan2(m.y - c.y, m.x - c.x)
        a2 = math.atan2(d.GetEnd().y - c.y, d.GetEnd().x - c.x)
        def norm(a):
            while a < a0 - 1e-9: a += 2 * math.pi
            while a > a0 + 2 * math.pi: a -= 2 * math.pi
            return a
        a1n, a2n = norm(a1), norm(a2)
        print("a0,a1n,a2n:", round(a0,3), round(a1n,3), round(a2n,3), "sweep:", round(a2n-a0,3))
        if abs((a2n - a0) - 2 * ((a1n - a0))) > 0.2 and (a2n - a0) > math.pi:
            a2n -= 2 * math.pi
            print("flipped, sweep:", round(a2n-a0,3))
        n = max(4, int(abs(a2n - a0) / 0.05))
        pts = [(c.x / MM + r * math.cos(a0 + (a2n - a0) * i / n),
                c.y / MM + r * math.sin(a0 + (a2n - a0) * i / n)) for i in range(n + 1)]
        print("arc sample first/last:", pts[0], pts[-1])
        print("arc start/end actual:", xy(d.GetStart()), xy(d.GetEnd()))
