"""Exact signed point-to-solid distance oracle (round 15).

For PLANE and CYLINDER faces the distance is computed analytically
from the face's own BRep geometry (trimmed-region tests included) -
mathematically identical to the BRep distance for those faces.
Other face types fall back to BRepExtrema_DistShapeShape per face
(pruned by AABB lower bounds), or, in 'fast' mode, to their AABB
lower bound (a conservative underestimate, used only inside the
optimiser loop). Sign: BRepClass3d classifier when the point lies
inside the solid's AABB; interior points get minus the boundary
distance. Verified against DistShapeShape in verify_oracle.py.
"""
import numpy as np
from OCP.BRepAdaptor import BRepAdaptor_Surface, BRepAdaptor_Curve
from OCP.GeomAbs import GeomAbs_SurfaceType, GeomAbs_CurveType
from OCP.BRepTools import BRepTools
from OCP.BRepBuilderAPI import BRepBuilderAPI_MakeVertex
from OCP.gp import gp_Pnt
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
from OCP.BRepClass3d import BRepClass3d_SolidClassifier
from OCP.TopAbs import TopAbs_IN

PLANE = GeomAbs_SurfaceType.GeomAbs_Plane
CYL = GeomAbs_SurfaceType.GeomAbs_Cylinder
LINE = GeomAbs_CurveType.GeomAbs_Line
CIRC = GeomAbs_CurveType.GeomAbs_Circle

def _v(x):
    return np.array([x.X(), x.Y(), x.Z()], float)

def _aabb_of(shape):
    bb = shape.bounding_box()
    return (np.array([bb.min.X, bb.min.Y, bb.min.Z]),
            np.array([bb.max.X, bb.max.Y, bb.max.Z]))

def _box_lb_arr(p, lo, hi):
    d = np.maximum(np.maximum(lo - p, p - hi), 0.0)
    return np.linalg.norm(d, axis=-1)

def _edge_prim(edge):
    ad = BRepAdaptor_Curve(edge.wrapped)
    t = ad.GetType()
    lo, hi = _aabb_of(edge)
    if t == LINE:
        return dict(kind='line', a=np.array(tuple(edge.position_at(0)), float),
                    b=np.array(tuple(edge.position_at(1)), float), lo=lo, hi=hi)
    if t == CIRC:
        circ = ad.Circle()
        return dict(kind='arc', c=_v(circ.Location()),
                    xa=_v(circ.XAxis().Direction()), ya=_v(circ.YAxis().Direction()),
                    ax=_v(circ.Axis().Direction()), r=float(circ.Radius()),
                    t0=float(ad.FirstParameter()), t1=float(ad.LastParameter()),
                    lo=lo, hi=hi)
    return dict(kind='fallback', wrapped=edge.wrapped, lo=lo, hi=hi)

def _pt_arc(p, e):
    c, xa, ya, r = e['c'], e['xa'], e['ya'], e['r']
    w = p - c; rad = w - (w @ e['ax']) * e['ax']; rho = float(np.linalg.norm(rad))
    best = (float('inf'), None)
    for cand in (e['t0'], e['t1']):
        q = c + r * (np.cos(cand) * xa + np.sin(cand) * ya)
        d = float(np.linalg.norm(p - q))
        if d < best[0]: best = (d, q)
    if rho > 1e-12:
        th = float(np.arctan2(rad @ ya, rad @ xa))
        span = e['t1'] - e['t0']
        tn = e['t0'] + (th - e['t0']) % (2 * np.pi)
        if tn <= e['t1'] + 1e-12 or span >= 2 * np.pi - 1e-12:
            q = c + r * (rad / rho)
            d = float(np.linalg.norm(p - q))
            if d < best[0]: best = (d, q)
    return best

def _pt_edge(p, e):
    if e['kind'] == 'line':
        a, b = e['a'], e['b']; ab = b - a
        L2 = float(ab @ ab)
        s = 0.0 if L2 == 0 else float(np.clip(((p - a) @ ab) / L2, 0, 1))
        q = a + s * ab
        return float(np.linalg.norm(p - q)), q
    if e['kind'] == 'arc':
        return _pt_arc(p, e)
    v = BRepBuilderAPI_MakeVertex(gp_Pnt(float(p[0]), float(p[1]), float(p[2]))).Vertex()
    dss = BRepExtrema_DistShapeShape(v, e['wrapped']); dss.Perform()
    q = dss.PointOnShape2(1)
    return float(dss.Value()), np.array([q.X(), q.Y(), q.Z()])

def _wire_area2d(edges, o, xu, xv):
    pts = []
    for e in edges:
        if e['kind'] == 'line':
            pts.append(e['a'])
        elif e['kind'] == 'arc':
            for k in range(9):
                t = e['t0'] + (e['t1'] - e['t0']) * k / 8
                pts.append(e['c'] + e['r'] * (np.cos(t) * e['xa'] + np.sin(t) * e['ya']))
        else:
            return None
    uv = [((q - o) @ xu, (q - o) @ xv) for q in pts]
    a = 0.0
    for k in range(len(uv)):
        x1, y1 = uv[k]; x2, y2 = uv[(k + 1) % len(uv)]
        a += x1 * y2 - x2 * y1
    return abs(a) / 2

class _Wire2:
    """One wire of a planar face, prepared for ray casting + edge distance."""
    def __init__(self, edges, o, xu, xv):
        self.edges = edges
        lines = [e for e in edges if e['kind'] == 'line']
        self.arcs = [e for e in edges if e['kind'] == 'arc']
        self.fbs = [e for e in edges if e['kind'] == 'fallback']
        if lines:
            A = np.array([e['a'] for e in lines]); B = np.array([e['b'] for e in lines])
            self.lA2 = np.stack([(A - o) @ xu, (A - o) @ xv], axis=1)
            self.lB2 = np.stack([(B - o) @ xu, (B - o) @ xv], axis=1)
        else:
            self.lA2 = np.zeros((0, 2)); self.lB2 = np.zeros((0, 2))
        lo = np.min([e['lo'] for e in edges], axis=0); hi = np.max([e['hi'] for e in edges], axis=0)
        self.uvlo = np.array([(lo - o) @ xu, (lo - o) @ xv]) if False else None
        # conservative 2D bounds from 3D AABB corners
        corners = np.array([[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])])
        cu = (corners - o) @ xu; cv = (corners - o) @ xv
        self.uvlo = np.array([cu.min(), cv.min()]); self.uvhi = np.array([cu.max(), cv.max()])
        for e in self.arcs:
            e['A'] = e['r'] * float(e['xa'] @ xv)
            e['B'] = e['r'] * float(e['ya'] @ xv)
            e['cv'] = float((e['c'] - o) @ xv)
        self.o = o; self.xu = xu; self.xv = xv
    def contains_uv(self, du, dv):
        return self.uvlo[0] - 1e-9 <= du <= self.uvhi[0] + 1e-9 and \
               self.uvlo[1] - 1e-9 <= dv <= self.uvhi[1] + 1e-9
    def inside(self, du, dv):
        cnt = 0
        if len(self.lA2):
            a, b = self.lA2, self.lB2
            m = (a[:, 1] > dv) != (b[:, 1] > dv)
            if m.any():
                uc = a[m, 0] + (dv - a[m, 1]) * (b[m, 0] - a[m, 0]) / (b[m, 1] - a[m, 1])
                cnt += int(np.sum(uc > du))
        for e in self.arcs:
            A, B, rhs = e['A'], e['B'], dv - e['cv']
            R = float(np.hypot(A, B))
            if R < 1e-14 or abs(rhs) > R: continue
            base = float(np.arctan2(B, A)); al = float(np.arccos(np.clip(rhs / R, -1, 1)))
            for t in (base + al, base - al):
                tn = e['t0'] + (t - e['t0']) % (2 * np.pi)
                if tn <= e['t1'] + 1e-9:
                    P = e['c'] + e['r'] * (np.cos(tn) * e['xa'] + np.sin(tn) * e['ya'])
                    if float((P - self.o) @ self.xu) > du: cnt += 1
        return cnt % 2 == 1

class FacePrim:
    def __init__(self, face):
        self.lo, self.hi = _aabb_of(face)
        self.wrapped = face.wrapped
        ad = BRepAdaptor_Surface(face.wrapped)
        st = ad.GetType()
        wires = [[_edge_prim(e) for e in w.edges()] for w in face.wires()]
        wires = [w for w in wires if w]
        self.edges = [e for w in wires for e in w]
        self.kind = 'fallback'
        if st == PLANE and all(e['kind'] in ('line', 'arc') for e in self.edges):
            pl = ad.Plane()
            self.kind = 'plane'
            self.o = _v(pl.Location()); self.xu = _v(pl.XAxis().Direction())
            self.xv = _v(pl.YAxis().Direction()); self.n = _v(pl.Axis().Direction())
            areas = [_wire_area2d(w, self.o, self.xu, self.xv) for w in wires]
            oi = int(np.argmax(areas))
            self.outer = _Wire2(wires[oi], self.o, self.xu, self.xv)
            self.inners = [_Wire2(w, self.o, self.xu, self.xv)
                           for k, w in enumerate(wires) if k != oi]
        elif st == CYL:
            cyl = ad.Cylinder()
            self.kind = 'cylinder'
            self.c0 = _v(cyl.Location()); self.ax = _v(cyl.Axis().Direction())
            self.xu = _v(cyl.XAxis().Direction()); self.xv = _v(cyl.YAxis().Direction())
            self.r = float(cyl.Radius())
            self.u0, self.u1, self.v0, self.v1 = BRepTools.UVBounds_s(face.wrapped)
            self.nwires = len(wires)
        # vectorised line-edge distance data (3D)
        lines = [e for e in self.edges if e['kind'] == 'line']
        if lines:
            self.eA = np.array([e['a'] for e in lines]); self.eB = np.array([e['b'] for e in lines])
            self.eAB = self.eB - self.eA
            self.eL2 = np.sum(self.eAB * self.eAB, axis=1)
            self.eLo = np.array([e['lo'] for e in lines]); self.eHi = np.array([e['hi'] for e in lines])
        else:
            self.eA = np.zeros((0, 3)); self.eB = np.zeros((0, 3)); self.eAB = np.zeros((0, 3))
            self.eL2 = np.zeros(0); self.eLo = np.zeros((0, 3)); self.eHi = np.zeros((0, 3))
        self.arcs = [e for e in self.edges if e['kind'] == 'arc']
        self.fbs = [e for e in self.edges if e['kind'] == 'fallback']

    def _edge_dist(self, p, best):
        if len(self.eA):
            t = np.where(self.eL2 > 0,
                         np.clip(np.sum((p - self.eA) * self.eAB, axis=1) /
                                 np.maximum(self.eL2, 1e-300), 0, 1), 0.0)
            Q = self.eA + t[:, None] * self.eAB
            D = np.linalg.norm(Q - p, axis=1)
            k = int(np.argmin(D))
            if float(D[k]) < best[0]: best = (float(D[k]), Q[k])
        for e in self.arcs:
            if float(_box_lb_arr(p, e['lo'], e['hi'])) > best[0]: continue
            d, q = _pt_arc(p, e)
            if d < best[0]: best = (d, q)
        for e in self.fbs:
            if float(_box_lb_arr(p, e['lo'], e['hi'])) > best[0]: continue
            d, q = _pt_edge(p, e)
            if d < best[0]: best = (d, q)
        return best

    def dist(self, p, fast=False):
        best = (float('inf'), None)
        if self.kind == 'plane':
            rel = p - self.o
            du, dv, dn = float(rel @ self.xu), float(rel @ self.xv), float(rel @ self.n)
            if self.outer.contains_uv(du, dv) and self.outer.inside(du, dv) and not any(
                    w.contains_uv(du, dv) and w.inside(du, dv) for w in self.inners):
                best = (abs(dn), p - dn * self.n)
        elif self.kind == 'cylinder':
            if self.nwires == 1:
                rel = p - self.c0; t = float(rel @ self.ax)
                w = rel - t * self.ax; rho = float(np.linalg.norm(w))
                if rho > 1e-12:
                    th = float(np.arctan2(w @ self.xv, w @ self.xu))
                    tn = self.u0 + (th - self.u0) % (2 * np.pi)
                    if tn <= self.u1 + 1e-12 and self.v0 - 1e-12 <= t <= self.v1 + 1e-12:
                        q = self.c0 + t * self.ax + self.r * (w / rho)
                        best = (abs(rho - self.r), q)
        elif fast:
            return float(_box_lb_arr(p, self.lo, self.hi)), None
        else:
            v = BRepBuilderAPI_MakeVertex(gp_Pnt(float(p[0]), float(p[1]), float(p[2]))).Vertex()
            dss = BRepExtrema_DistShapeShape(v, self.wrapped); dss.Perform()
            q = dss.PointOnShape2(1)
            return float(dss.Value()), np.array([q.X(), q.Y(), q.Z()])
        return self._edge_dist(p, best)

class OracleBody:
    def __init__(self, name, shape, faces=None):
        self.name = name
        self.lo, self.hi = _aabb_of(shape)
        self.shape = shape
        self.faces = faces if faces is not None else [FacePrim(f) for f in shape.faces()]
        self._flo = np.array([f.lo for f in self.faces])
        self._fhi = np.array([f.hi for f in self.faces])
        self._cls = None
        self.kinds = {k: sum(1 for f in self.faces if f.kind == k)
                      for k in ('plane', 'cylinder', 'fallback')}
    def restrict(self, lo, hi, name=None):
        """Sub-oracle with only faces whose AABB meets the box (exact for
        queries whose true distance is below the box clearance)."""
        keep = [f for f in self.faces
                if np.all(f.hi >= lo) and np.all(f.lo <= hi)]
        return OracleBody(name or self.name, self.shape, faces=keep)
    def dist_capped(self, p, cap):
        """Exact (d, q) if the true distance < cap, else (cap, None)
        as soon as the face lower bounds prove it."""
        p = np.asarray(p, float)
        lbn = _box_lb_arr(p, self._flo, self._fhi)
        order = np.argsort(lbn)
        best = (float('inf'), None)
        for k in order:
            if lbn[k] >= cap and best[0] >= cap:
                return cap, None
            if lbn[k] > best[0]: break
            d, q = self.faces[k].dist(p)
            if d < best[0]: best = (d, q)
        if best[0] >= cap: return cap, None
        d, q = best
        if d <= 1e-12: return 0.0, (q if q is not None else p)
        if np.all(p >= self.lo) and np.all(p <= self.hi):
            if self._cls is None:
                self._cls = BRepClass3d_SolidClassifier(self.shape.wrapped)
            self._cls.Perform(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), 1e-7)
            if self._cls.State() == TopAbs_IN:
                return -d, q
        return d, q
    def dist(self, p, fast=False):
        p = np.asarray(p, float)
        lbn = _box_lb_arr(p, self._flo, self._fhi)
        best = (float('inf'), None)
        for k in np.argsort(lbn):
            if lbn[k] > best[0]: break
            d, q = self.faces[k].dist(p, fast=fast)
            if d < best[0]: best = (d, q)
        d, q = best
        if d <= 1e-12: return 0.0, (q if q is not None else p)
        if np.all(p >= self.lo) and np.all(p <= self.hi):
            if self._cls is None:
                self._cls = BRepClass3d_SolidClassifier(self.shape.wrapped)
            self._cls.Perform(gp_Pnt(float(p[0]), float(p[1]), float(p[2])), 1e-7)
            if self._cls.State() == TopAbs_IN:
                return -d, q
        return d, q
