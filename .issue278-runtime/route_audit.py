#!/usr/bin/env python3
"""Issue #278: route-family audits in the flipped fitted body set.
Method = #275 bundle construction + repaired Common (ShapeList-aware
Shape.intersect, volume-validated solids, positive self-test)."""
import sys, os, json, math, time
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, f'{PB}/sources/frontier')
sys.path.insert(0, PB)
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-flipusb/hardware/case/issue-261-lowdeck-full/sources')
from build123d import Box, Pos, Rot, Shape, Plane, mirror
from OCP.BRepExtrema import BRepExtrema_DistShapeShape
import numpy as np
import audit_static as AS
import fitlibF as FF

RT = os.path.dirname(os.path.abspath(__file__))
POCKET_A = (-6, 13, 28, 48)
OWN = {'Main-study-J4', 'EZmate-Fly-plug', 'Fly-official-67-instance-67'}
OUT = {}

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def vol(s):
    try: return float(s.volume)
    except AttributeError: return sum(float(x.volume) for x in s)

def common_vol(a, b):
    c = a.intersect(b)
    if c is None: return 0.0
    return vol(c)

def extrema(a, b):
    d = BRepExtrema_DistShapeShape(a.wrapped, b.wrapped)
    d.Perform()
    return float(d.Value()) if d.IsDone() else -1.0

def box_at(cx, cy, cz, dx, dy, dz, yaw=0.0):
    return Pos(cx, cy, cz) * Rot(0, 0, yaw) * Box(dx, dy, dz)

def flip_shape(s):
    return mirror(mirror(s, Plane.YZ), Plane(origin=(0, 0, 5.30)))

FLIP_PREFIX = ('Main-study-', 'cover-Main-spacer-', 'screw-main-')

def build_bodies(extra_tray_cuts=()):
    bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
              if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND',
                           'Fly-170mm')]
    CTRL_R = AS.CTRL_R
    FLAT_R = [(x, y, 2.95) for x, y, z in CTRL_R]
    FLAT_L = [(-x, y, 2.95) for x, y, z in CTRL_R]
    chan_r = AS.channel_solid(FLAT_R)
    chan_l = AS.channel_solid(FLAT_L)
    out = {}
    for n, s in bodies:
        if n in ('tray-right', 'tray-left'):
            s2 = s.cut(chan_r).cut(chan_l)
            x0, x1, y0, y1 = POCKET_A
            s2 = s2.cut(box_at((x0+x1)/2, (y0+y1)/2, 1.10, x1-x0, y1-y0, 1.0))
            for c in extra_tray_cuts:
                s2 = s2.cut(c)
            out[n] = s2
        elif n == 'main' or n.startswith(FLIP_PREFIX):
            out[n] = flip_shape(s)
        elif n == 'EZmate-Main-plug':
            continue
        else:
            out[n] = s
    for side, cx, yaw in (('right', 23.3, -43.0), ('left', -23.3, 43.0)):
        body = box_at(cx, 40.8, 3.70, 11, 7, 2.0, yaw=yaw)
        mx = cx + 3.10 * math.sin(math.radians(yaw))
        my = 40.8 - 3.10 * math.cos(math.radians(yaw))
        body = body.cut(box_at(mx, my, 2.95, 10.4, 1.8, 0.5, yaw=yaw))
        out[f'ZIF-main-{side}'] = body
    for side, cx in (('right', 27.0), ('left', -27.0)):
        out[f'ZIF-wing-{side}'] = box_at(cx, -37.5, 3.70, 11, 7, 2.0).cut(
            box_at(cx, -34.2, 2.95, 10.4, 1.8, 0.5))
    sheets = {}
    for side, ctrl in (('right', FLAT_R), ('left', FLAT_L)):
        boxes = AS.sheet_boxes(AS.catmull(ctrl))
        acc = boxes[0]
        for b in boxes[1:]:
            acc = acc.fuse(b)
        sheets[side] = acc
        out[f'FFC-sheet-{side}'] = acc
    return out, sheets

def fuse_all(shapes):
    acc = shapes[0]
    for s in shapes[1:]:
        acc = acc.fuse(s)
    return acc

def cable_solid(ctrl):
    pts = AS.catmull(ctrl)
    length = sum(float(np.linalg.norm(np.array(pts[i+1]) - np.array(pts[i])))
                 for i in range(len(pts) - 1))
    boxes = AS.sheet_boxes(pts, w=4.5, t=1.2)
    boxes.append(box_at(0, 19.18, 3.45, 5.0, 3.5, 1.30))
    boxes.append(box_at(0, -49.02, 3.45, 5.0, 3.5, 1.30))
    c = fuse_all(boxes)
    return c, round(length, 2)

def gate(cable, bodies, label):
    cb = cable.bounding_box()
    hits, eng, near = {}, {}, []
    for n, s in bodies.items():
        bb = s.bounding_box()
        if (bb.max.X < cb.min.X - 0.01 or bb.min.X > cb.max.X + 0.01 or
            bb.max.Y < cb.min.Y - 0.01 or bb.min.Y > cb.max.Y + 0.01 or
            bb.max.Z < cb.min.Z - 0.01 or bb.min.Z > cb.max.Z + 0.01):
            continue
        v = common_vol(cable, s)
        if n in OWN:
            if v > 0.005: eng[n] = round(v, 3)
            continue
        if v > 0.005:
            hits[n] = round(v, 3)
    log(f"{label}: hits={hits} engagement={eng}")
    return hits, eng

def save():
    json.dump(OUT, open(os.path.join(RT, 'audit278.json'), 'w'), indent=1)

# ---------------- routes ----------------
A0 = [(0,19.18,3.45),(0,22.5,3.0),(1.5,25.5,2.5),(4,28,2.2),
      (11,32,2.2),(16.5,38,2.2),(17,44,2.2),(14.5,49.5,2.2),(9,48,2.2),
      (6.5,41,2.2),(6.5,30,2.2),(7.5,22,2.2),(10.5,14,2.2),(10.5,4,2.2),
      (13,-4,2.2),(10.5,-13,2.2),(13,-22,2.2),(10.5,-31,2.2),
      (8,-39,2.2),(4,-44,2.25),(1,-46.6,2.6),(0,-48,3.0),(0,-49.02,3.45)]

A1 = [(x, y, (1.90 if z == 2.2 else z)) for (x, y, z) in A0]
A1[2] = (1.5, 25.5, 2.2); A1[3] = (4, 28, 1.95)
A1[-3] = (1, -46.6, 2.3); A1[-2] = (0, -48, 2.85)

FLY_FLIP = [(0.0,19.0,3.45),(0.0,22.5,2.90),(-2.0,25.5,2.20),
            (-6.0,27.5,1.85),(-9.5,25.0,1.85),(-10.0,18.0,1.85),
            (-10.0,4.0,1.85),(-10.0,1.0,3.85),(-10.0,-5.0,3.85),
            (-10.0,-9.0,1.85),(-10.0,-30.0,1.85),(-7.0,-40.0,2.10),
            (-2.5,-46.0,2.80),(0.0,-48.6,3.45)]
B = [(-x, y, z) for (x, y, z) in FLY_FLIP]

D = [(0,19.18,3.45),(0,22.5,3.0),(1.5,25.5,2.5),(4,30,2.2),(6,40,2.2),
     (6.5,55,2.2),(7,66,2.2),(10,72,2.2),(14,74.5,2.2),(17,71,2.2),
     (17.5,62,2.2),(15,55,2.2),(14.5,45,2.2),(14.5,30,2.2),(14.5,10,2.2),
     (14.5,-15,2.2),(14.5,-31,2.2),(11,-39,2.2),(6,-43.5,2.25),
     (1,-46.6,2.6),(0,-48,3.0),(0,-49.02,3.45)]

C_SEG = [(-2,-6,2.2),(16,-6,2.2)]       # straight under-crossing, floor level
C_SEG_CH = [(-2,-6,1.9),(16,-6,1.9)]    # same, channel level

def main():
    log("building bodies (pocket A only)")
    bodies, sheets = build_bodies()
    bad = [n for n, s in bodies.items() if vol(s) <= 0]
    log(f"bodies: {len(bodies)}, non-positive: {bad}")
    plug = box_at(0, 19.18, 3.45, 5.0, 3.5, 1.30)
    st = round(common_vol(plug.translate((0, 0, -1.6)), bodies['tray-left']), 3)
    log(f"self-test plug-vs-tray-left (must be >0): {st}")
    OUT['self_test'] = st
    OUT['n_bodies'] = len(bodies)

    for label, ctrl in (('A0', A0), ('D', D)):
        c, L = cable_solid(ctrl)
        hits, eng = gate(c, bodies, label)
        OUT[label] = dict(length_mm=L, hits=hits, engagement=eng,
                          cable_volume=round(vol(c), 2))
        # min clearance to sheets for A0
        if label == 'A0':
            OUT[label]['sheet_clearance'] = {
                s: round(extrema(c, sheets[s]), 3) for s in ('left', 'right')}
        save()

    # Family C: local crossing segments vs sheets only
    for label, seg in (('C_floor', C_SEG), ('C_channel', C_SEG_CH)):
        boxes = AS.sheet_boxes(AS.catmull(seg), w=4.5, t=1.2)
        c = fuse_all(boxes)
        res = {s: dict(vol=round(common_vol(c, sheets[s]), 3),
                       dist=round(extrema(c, sheets[s]), 3))
               for s in ('left', 'right')}
        OUT[label] = res
        log(f"{label}: {res}")
        save()

    # service sweeps for A0 plugs
    sw = {}
    for nm, pb in (('J4', box_at(0, 19.18, 3.45, 5.0, 3.5, 1.30)),
                   ('Fly', box_at(0, -49.02, 3.45, 5.0, 3.5, 1.30))):
        moved = pb.translate((0, 0, -2.0))
        h = {}
        for n, s in bodies.items():
            if n in OWN: continue
            bb = s.bounding_box(); mb = moved.bounding_box()
            if (bb.max.X < mb.min.X - 0.01 or bb.min.X > mb.max.X + 0.01 or
                bb.max.Y < mb.min.Y - 0.01 or bb.min.Y > mb.max.Y + 0.01 or
                bb.max.Z < mb.min.Z - 0.01 or bb.min.Z > mb.max.Z + 0.01):
                continue
            v = common_vol(moved, s)
            if v > 0.005: h[n] = round(v, 3)
        sw[nm] = h
        log(f"sweep {nm} -2.0z: {h}")
    OUT['service_sweep_down2'] = sw
    save()

    # Family B: mirrored Stage B hop route, trays + mirrored channel E
    chanE = box_at(10.0, -9.0, 1.10, 5.0, 56.0, 1.0)
    log("building bodies (B: + channel E)")
    bodiesB, _ = build_bodies(extra_tray_cuts=(chanE,))
    c, L = cable_solid(B)
    hits, eng = gate(c, bodiesB, 'B')
    OUT['B'] = dict(length_mm=L, hits=hits, engagement=eng)
    save()

    # Family A1: channel-cut trays following A1 centreline plan
    pts = AS.catmull(A1)
    cutters = []
    for a, b in zip(pts[:-1], pts[1:]):
        d = np.array(b) - np.array(a); Ln = float(np.linalg.norm(d))
        if Ln < 1e-6: continue
        yaw = math.degrees(math.atan2(d[1], d[0]))
        mid = (np.array(a) + np.array(b)) / 2
        cutters.append(Pos(float(mid[0]), float(mid[1]), 1.42) * Rot(0, 0, yaw)
                       * Box(Ln + 1.2, 7.5, 0.40))
    chanA1 = fuse_all(cutters)
    log("building bodies (A1: + route channel)")
    bodiesA, _ = build_bodies(extra_tray_cuts=(chanA1,))
    c, L = cable_solid(A1)
    hits, eng = gate(c, bodiesA, 'A1')
    OUT['A1'] = dict(length_mm=L, hits=hits, engagement=eng,
                     channel_cut_volume_mm3=round(vol(chanA1), 1))
    OUT['A1']['sheet_clearance'] = {
        s: round(extrema(c, bodiesA[f'FFC-sheet-{s}']), 3) for s in ('left', 'right')}
    save()
    log("DONE")

if __name__ == '__main__':
    main()
