#!/usr/bin/env python3
"""Issue #278 local helpers: STEP-cache body loading + the same cable
construction / repaired-Common gate as route_audit.py, WITHOUT importing
audit_static/fitlibF (their module-level builds take ~10 min and die
with service restarts). catmull/sheet_boxes replicate audit_static's
exact construction (segment boxes L+0.35, yaw then -pitch)."""
import os, json, math
import numpy as np
from build123d import Box, Pos, Rot, import_step
from OCP.BRepExtrema import BRepExtrema_DistShapeShape

RT = os.path.dirname(os.path.abspath(__file__))
CACHE = os.path.join(RT, 'bodies_cache')
OWN = {'Main-study-J4', 'EZmate-Fly-plug', 'Fly-official-67-instance-67'}

def load_bodies(names=None):
    manifest = json.load(open(os.path.join(CACHE, 'manifest.json')))
    out = {}
    for n, fn in manifest.items():
        if names is not None and n not in names:
            continue
        out[n] = import_step(os.path.join(CACHE, fn))
    return out

def catmull(P, n_per=14):
    P = [P[0]] + list(P) + [P[-1]]
    out = []
    for i in range(len(P) - 3):
        p0, p1, p2, p3 = [np.array(x, float) for x in P[i:i + 4]]
        for j in range(n_per):
            t = j / n_per
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t +
                              (2 * p0 - 5 * p1 + 4 * p2 - p3) * t * t +
                              (-p0 + 3 * p1 - 3 * p2 + p3) * t * t * t))
    out.append(np.array(P[-2], float))
    return out

def sheet_boxes(pts, w=10.2, t=0.25):
    solids = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = b - a; L = float(np.linalg.norm(d))
        if L < 1e-6: continue
        yaw = math.degrees(math.atan2(d[1], d[0]))
        pitch = math.degrees(math.asin(max(-1, min(1, d[2] / L))))
        mid = (a + b) / 2
        solids.append(Pos(mid[0], mid[1], mid[2]) * Rot(0, 0, yaw)
                      * Rot(0, -pitch, 0) * Box(L + 0.35, w, t))
    return solids

def box_at(cx, cy, cz, dx, dy, dz, yaw=0.0):
    return Pos(cx, cy, cz) * Rot(0, 0, yaw) * Box(dx, dy, dz)

def fuse_all(shapes):
    acc = shapes[0]
    for s in shapes[1:]:
        acc = acc.fuse(s)
    return acc

def cable_solid(ctrl):
    pts = catmull(ctrl)
    length = sum(float(np.linalg.norm(np.array(pts[i + 1]) - np.array(pts[i])))
                 for i in range(len(pts) - 1))
    boxes = sheet_boxes(pts, w=4.5, t=1.2)
    boxes.append(box_at(0, 19.18, 3.45, 5.0, 3.5, 1.30))
    boxes.append(box_at(0, -49.02, 3.45, 5.0, 3.5, 1.30))
    return fuse_all(boxes), round(length, 2)

def vol(s):
    if s is None: return 0.0
    try: return float(s.volume)
    except AttributeError: return sum(float(x.volume) for x in s)

def common_vol(a, b):
    return vol(a.intersect(b))

def extrema(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return float(d.Value()) if d.IsDone() else -1.0

def gate(cable, bodies, own=OWN):
    cb = cable.bounding_box()
    hits, eng = {}, {}
    for n, s in bodies.items():
        bb = s.bounding_box()
        if (bb.max.X < cb.min.X - 0.01 or bb.min.X > cb.max.X + 0.01 or
            bb.max.Y < cb.min.Y - 0.01 or bb.min.Y > cb.max.Y + 0.01 or
            bb.max.Z < cb.min.Z - 0.01 or bb.min.Z > cb.max.Z + 0.01):
            continue
        v = common_vol(cable, s)
        if n in own:
            if v > 0.005: eng[n] = round(v, 3)
        elif v > 0.005:
            hits[n] = round(v, 3)
    return hits, eng

A1F = [(0,19.18,3.45),(0,22.5,2.9),(1.5,25.5,2.2),(4,28,1.95),
       (11,32,1.9),(16.5,38,1.9),(17,44,1.9),(14.5,50,1.9),(9,48,1.9),
       (6.5,41,1.9),(6.5,30,1.9),(7.5,22,1.9),(10.5,14,1.9),(10.5,5,1.9),
       (20,-3,1.9),(20,-9,1.9),(10.5,-15,1.9),
       (2,-21,1.9),(2,-27,1.9),(10.5,-33,1.9),
       (8,-39,1.9),(5.5,-44.5,1.95),(1,-46.6,2.3),(0,-48,2.85),
       (0,-49.02,3.45)]
