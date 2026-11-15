"""Manual path builder: polyline vertices with R5 fillet arcs at
corners, plus optional true arc edges (three-point) for designated
segments (hairpin). Arc endpoints must be tangent-continuous with
their neighbours (deflection ~0), so no fillet is applied there.
Returns (Wire path, length)."""
import numpy as np
from build123d import Edge, Wire, Vector

def _fillet(prev_p, corner, next_p, R):
    u = prev_p - corner; u = u / np.linalg.norm(u)
    v = next_p - corner; v = v / np.linalg.norm(v)
    theta = np.arccos(np.clip(float(u @ v), -1, 1))
    d = R / np.tan(theta / 2)
    a = corner + u * d; b = corner + v * d
    cen = corner + (u + v) / np.linalg.norm(u + v) * R / np.sin(theta / 2)
    mid = cen + (corner - cen) / np.linalg.norm(corner - cen) * R
    return a, mid, b, d

def build_path(verts, arcs=None, R=5.0, no_fillet=()):
    """verts: list of np.array points. arcs: {i: mid_point} meaning
    edge i (verts[i] -> verts[i+1]) is a three-point arc through
    mid_point. no_fillet: vertex indices to skip filleting."""
    arcs = arcs or {}
    n = len(verts)
    # trim distances at each interior vertex
    trims = {}
    for i in range(1, n - 1):
        if i in no_fillet:
            continue
        a, mid, b, d = _fillet(verts[i - 1], verts[i], verts[i + 1], R)
        trims[i] = (a, mid, b, d)
    # check segment lengths vs trims (arc edges need no trim room)
    for i in range(n - 1):
        if i in arcs:
            continue
        need = (trims[i][3] if i in trims else 0.0) + (trims[i + 1][3] if i + 1 in trims else 0.0)
        seg = float(np.linalg.norm(verts[i + 1] - verts[i]))
        assert need < seg - 1e-6, ('straight too short', i, need, seg)
    edges = []
    cur = verts[0]
    for i in range(n - 1):
        start = cur
        end_trim = trims[i + 1][0] if (i + 1) in trims else verts[i + 1]
        if i in arcs:
            edges.append(Edge.make_three_point_arc(
                Vector(*map(float, start)), Vector(*map(float, arcs[i])),
                Vector(*map(float, end_trim))))
        else:
            edges.append(Edge.make_line(Vector(*map(float, start)),
                                        Vector(*map(float, end_trim))))
        if (i + 1) in trims:
            a, mid, b, d = trims[i + 1]
            edges.append(Edge.make_three_point_arc(
                Vector(*map(float, a)), Vector(*map(float, mid)),
                Vector(*map(float, b))))
            cur = b
        else:
            cur = verts[i + 1]
    path = Wire(edges)
    return path, path.length
