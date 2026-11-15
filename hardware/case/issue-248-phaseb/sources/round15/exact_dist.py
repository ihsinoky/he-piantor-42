"""Exact signed point-to-solid distances (round 15).

Method: distance to a solid = min over its boundary faces of the exact
BRep point-to-face distance (BRepExtrema_DistShapeShape per face),
with faces pruned by their AABB lower bounds (pruning never changes
the minimum, so the result is the exact BRep boundary distance).
Sign: negative when the point is inside the solid (BRepClass3d
classifier, invoked only when the point is inside the solid's AABB).
"""
import numpy as np
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN

def _aabb(shape):
    bb = shape.bounding_box()
    return (np.array([bb.min.X, bb.min.Y, bb.min.Z]),
            np.array([bb.max.X, bb.max.Y, bb.max.Z]))

def _box_lb(p, lo, hi):
    d = np.maximum(np.maximum(lo - p, p - hi), 0.0)
    return float(np.linalg.norm(d))

class Body:
    def __init__(self, name, shape):
        self.name = name
        self.shape = shape
        self.lo, self.hi = _aabb(shape)
        self.faces = []
        for f in shape.faces():
            lo, hi = _aabb(f)
            self.faces.append((f.wrapped, lo, hi))
        self._cls = None
    def _boundary_dist(self, p):
        order = sorted(range(len(self.faces)),
                       key=lambda k: _box_lb(p, self.faces[k][1], self.faces[k][2]))
        v = BRepBuilderAPI_MakeVertex(gp_Pnt(float(p[0]), float(p[1]), float(p[2]))).Vertex()
        best = float('inf'); bestq = None
        for k in order:
            fw, lo, hi = self.faces[k]
            if _box_lb(p, lo, hi) > best:
                break
            dss = BRepExtrema_DistShapeShape(v, fw)
            dss.Perform()
            d = float(dss.Value())
            if d < best:
                best = d
                q = dss.PointOnShape2(1)
                bestq = np.array([q.X(), q.Y(), q.Z()])
                if best <= 1e-12:
                    break
        return best, bestq
    def dist(self, p):
        """Signed exact distance + closest boundary point."""
        p = np.asarray(p, float)
        d, q = self._boundary_dist(p)
        if d <= 1e-12:
            return 0.0, q
        if np.all(p >= self.lo) and np.all(p <= self.hi):
            if self._cls is None:
                self._cls = BRepClass3d_SolidClassifier(self.shape.wrapped)
            self._cls.Perform(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), 1e-7)
            if self._cls.State() == TopAbs_IN:
                return -d, q
        return d, q

def dist_batch(body, pts):
    d = np.empty(len(pts)); Q = np.empty((len(pts), 3))
    for k, p in enumerate(pts):
        d[k], Q[k] = body.dist(p)
    return d, Q
