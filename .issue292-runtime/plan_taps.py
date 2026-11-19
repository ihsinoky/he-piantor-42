"""GND tap planner (shapely, exact rotated geometry).
For every F.Cu GND pad not already touching GND copper, find a via
(0.6/0.3) + stub (0.3 wide) position with >=0.10 mm clearance to all
other-net copper, inside the outline, outside the antenna shadow.
Falls back to chaining the pad to the nearest tapped GND point."""
import json, math
from shapely.geometry import Polygon, Point, LineString, box
from shapely.affinity import rotate, translate

G = json.loads(open('geom.json').read())
LOOP = [(64.1073, 134.4359), (66.1073, 137.9), (133.8927, 137.9), (135.8927, 134.4359),
        (128.9362, 122.3869), (132.9488, 115.4381), (119.8213, 103.1964),
        (117.8562, 103.1958), (102.0, 75.7321), (98.0, 75.7321), (82.1438, 103.1958),
        (80.1787, 103.1964), (67.0512, 115.4381), (71.0638, 122.3869)]
outline = Polygon(LOOP)
antenna = box(70.3, 128.9, 79.9, 137.9)
CLR = 0.10

def pad_poly(pd):
    r = box(-pd['sx'] / 2, -pd['sy'] / 2, pd['sx'] / 2, pd['sy'] / 2)
    r = rotate(r, pd['rot'], origin=(0, 0))
    return translate(r, pd['x'], pd['y'])

pads = []
for pd in G['pads']:
    pd = dict(pd)
    pd['poly'] = pad_poly(pd)
    pads.append(pd)
tracks = []
for t in G['tracks']:
    t = dict(t)
    t['poly'] = LineString([(t['x1'], t['y1']), (t['x2'], t['y2'])]).buffer(t['w'] / 2, cap_style=1)
    tracks.append(t)
vias = []
for v in G['vias']:
    v = dict(v)
    v['poly'] = Point(v['x'], v['y']).buffer(v['d'] / 2)
    vias.append(v)

def clear_of(shape, net, layers=('F',), extra=CLR):
    """True if shape keeps >= extra clearance from other-net copper."""
    for pd in pads:
        if pd['net'] == net:
            continue
        if not set(pd['layers']) & set(layers) and not pd['pth']:
            continue
        if shape.distance(pd['poly']) < extra:
            return False
    for t in tracks:
        if t['net'] == net:
            continue
        if t['layer'] not in layers:
            continue
        if shape.distance(t['poly']) < extra:
            return False
    for v in vias:
        if v['net'] == net:
            continue
        if shape.distance(v['poly']) < extra:
            return False
    return True

# which GND pads already touch GND copper on F?
def pad_connected(pd):
    for t in tracks:
        if t['net'] == 'GND' and t['layer'] == 'F' and t['poly'].distance(pd['poly']) < 0.01:
            return True
    for v in vias:
        if v['net'] == 'GND' and v['poly'].distance(pd['poly']) < 0.01:
            return True
    return False

gnd_pads = [pd for pd in pads if pd['net'] == 'GND' and 'F' in pd['layers']]
taps = []       # {'pad': ref, 'vx':, 'vy':, 'sx': stub from (x,y) to via}
tapped_pts = [] # (x, y) of placed GND vias (chain targets)
failed = []
for pd in sorted(gnd_pads, key=lambda z: z['ref']):
    if pad_connected(pd):
        continue
    cx, cy = pd['x'], pd['y']
    placed = None
    for radius in (0.95, 1.15, 1.4, 1.7, 2.1):
        for adeg in range(0, 360, 15):
            a = math.radians(adeg)
            vx, vy = cx + radius * math.cos(a), cy + radius * math.sin(a)
            via = Point(vx, vy).buffer(0.3)
            if not outline.contains(via.buffer(0.12)):
                continue
            if antenna.intersects(via):
                continue
            stub = LineString([(cx, cy), (vx, vy)]).buffer(0.15, cap_style=1)
            if not clear_of(via, 'GND', layers=('F', 'I2', 'B')):
                continue
            if not clear_of(stub, 'GND', layers=('F',)):
                continue
            # via-to-via same-net spacing (avoid clustering on other GND vias)
            if any(math.hypot(vx - tx, vy - ty) < 0.75 for (tx, ty) in tapped_pts):
                continue
            placed = (vx, vy)
            break
        if placed:
            break
    if placed:
        vx, vy = placed
        taps.append({'pad': pd['ref'], 'vx': round(vx, 3), 'vy': round(vy, 3),
                     'px': cx, 'py': cy})
        tapped_pts.append((vx, vy))
        vias.append({'net': 'GND', 'x': vx, 'y': vy, 'd': 0.6,
                     'poly': Point(vx, vy).buffer(0.3)})
        tracks.append({'net': 'GND', 'layer': 'F', 'x1': cx, 'y1': cy, 'x2': vx, 'y2': vy,
                       'w': 0.3, 'poly': LineString([(cx, cy), (vx, vy)]).buffer(0.15, cap_style=1)})
    else:
        failed.append(pd['ref'])

print('taps planned:', len(taps), 'failed:', failed)
json.dump({'taps': taps, 'failed': failed}, open('taps.json', 'w'), indent=1)
