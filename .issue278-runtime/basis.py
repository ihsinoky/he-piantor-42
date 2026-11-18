#!/usr/bin/env python3
"""Issue #278 Stage 0: measured basis from the flipped body set.
Reuses the #275 audit bundle construction (audit275.py) verbatim in
method; audit Common = repaired ShapeList-aware intersect."""
import sys, os, json, math, time
PB = '/home/hatch/workspace/projects/he-piantor-raise/hardware/case/issue-248-phaseb'
sys.path.insert(0, f'{PB}/sources/frontier')
sys.path.insert(0, PB)
sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-flipusb/hardware/case/issue-261-lowdeck-full/sources')
from build123d import Box, Pos, Rot, Shape, Plane, mirror
import audit_static as AS
import fitlibF as FF

RT = os.path.dirname(os.path.abspath(__file__))
POCKET_A = (-6, 13, 28, 48)

def log(*a): print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)

def bb(s):
    b = s.bounding_box()
    return [round(b.min.X,3), round(b.min.Y,3), round(b.min.Z,3),
            round(b.max.X,3), round(b.max.Y,3), round(b.max.Z,3)]

def vol(s):
    try: return float(s.volume)
    except AttributeError: return sum(float(x.volume) for x in s)

def common_vol(a, b):
    c = a.intersect(b)
    if c is None: return 0.0
    return vol(c)

def box_at(cx, cy, cz, dx, dy, dz, yaw=0.0):
    return Pos(cx, cy, cz) * Rot(0, 0, yaw) * Box(dx, dy, dz)

def flip_shape(s):
    return mirror(mirror(s, Plane.YZ), Plane(origin=(0, 0, 5.30)))

FLIP_PREFIX = ('Main-study-', 'cover-Main-spacer-', 'screw-main-')

bodies = [(n, s) for n, s in FF.bodies_at(17, -2.65)
          if n not in ('Main-GH-left-DRAWING-BOUND', 'Main-GH-right-DRAWING-BOUND')]
log(f"bodies_at: {len(bodies)}")

CTRL_R = AS.CTRL_R
CTRL_L = [(-x, y, z) for (x, y, z) in CTRL_R]
FLAT_R = [(x, y, 2.95) for x, y, z in CTRL_R]
FLAT_L = [(-x, y, 2.95) for x, y, z in CTRL_R]
chan_r = AS.channel_solid(FLAT_R)
chan_l = AS.channel_solid(FLAT_L)

out = {}
flipped = []
for n, s in bodies:
    if n in ('tray-right', 'tray-left'):
        s2 = s.cut(chan_r).cut(chan_l)
        x0, x1, y0, y1 = POCKET_A
        s2 = s2.cut(box_at((x0+x1)/2, (y0+y1)/2, 1.10, x1-x0, y1-y0, 1.0))
        out[n] = s2
    elif n == 'main' or n.startswith(FLIP_PREFIX):
        out[n] = flip_shape(s); flipped.append(n)
    elif n == 'EZmate-Main-plug':
        continue
    else:
        out[n] = s

# flipped Main ZIF envelopes (audit275 construction)
for side, cx, yaw in (('right', 23.3, -43.0), ('left', -23.3, 43.0)):
    body = box_at(cx, 40.8, 3.70, 11, 7, 2.0, yaw=yaw)
    mx = cx + 3.10 * math.sin(math.radians(yaw))
    my = 40.8 - 3.10 * math.cos(math.radians(yaw))
    body = body.cut(box_at(mx, my, 2.95, 10.4, 1.8, 0.5, yaw=yaw))
    out[f'ZIF-main-{side}'] = body
for side, cx in (('right', 27.0), ('left', -27.0)):
    body = box_at(cx, -37.5, 3.70, 11, 7, 2.0).cut(box_at(cx, -34.2, 2.95, 10.4, 1.8, 0.5))
    out[f'ZIF-wing-{side}'] = body

# Type D sheets as fused solids
sheets = {}
for side, ctrl in (('right', FLAT_R), ('left', FLAT_L)):
    boxes = AS.sheet_boxes(AS.catmull(ctrl))
    acc = boxes[0]
    for b in boxes[1:]:
        acc = acc.fuse(b)
    sheets[side] = acc
    out[f'FFC-sheet-{side}'] = acc

# J4 flipped plug (Stage B model)
plug = box_at(0, 19.18, 3.45, 5.0, 3.5, 1.30)
out['J4-plug-flipped'] = plug

# volume validation of every solid
validity = {}
for n, s in out.items():
    v = vol(s)
    validity[n] = dict(volume=round(v, 3), positive=bool(v > 0))
bad = [n for n, d in validity.items() if not d['positive']]
log(f"volume validation: {len(out)} solids, non-positive: {bad}")

# self-test: plug translated down 1.0 must intersect tray-left or floor bodies
test = plug.translate((0, 0, -1.6))
st = {n: round(common_vol(test, s), 3) for n, s in out.items()
      if n.startswith('tray') }
log(f"self-test plug-vs-trays (must have >0): {st}")

dump = {}
want_prefix = ('Fly-', 'EZmate-', 'USB-', 'tray-', 'Main-study-', 'screw-main-',
               'cover-Main-', 'FFC-', 'ZIF-', 'shell-', 'strip-', 'plate-', 'post-',
               'joint-', 'splice-', 'POM-', 'washer-', 'underside-', 'switch-')
for n, s in out.items():
    if n == 'main' or n == 'J4-plug-flipped' or n.startswith(want_prefix):
        dump[n] = bb(s)
# under-board obstruction map: flipped Main-attached bodies hanging below 4.70
under = {n: dump[n] for n in flipped if n in dump and dump[n][2] < 4.699}
res = dict(bboxes=dump, under_board_flipped=under,
           validity_bad=bad, self_test=st,
           sheet_ctrl_R=CTRL_R)
json.dump(res, open(os.path.join(RT, 'basis.json'), 'w'), indent=1)
log("basis.json written")
for n in sorted(dump):
    print(n, dump[n])
