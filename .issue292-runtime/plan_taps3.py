"""FH12 GND pads: fine search (5 deg steps, radius to 3.2 mm, via 0.5,
stub 0.2 wide). Appends to taps.json."""
import json, math
from shapely.geometry import Polygon, Point, LineString, box
from shapely.affinity import rotate, translate

G = json.loads(open('geom.json').read())
T = json.loads(open('taps.json').read())
LOOP = [(64.1073, 134.4359), (66.1073, 137.9), (133.8927, 137.9), (135.8927, 134.4359),
        (128.9362, 122.3869), (132.9488, 115.4381), (119.8213, 103.1964),
        (117.8562, 103.1958), (102.0, 75.7321), (98.0, 75.7321), (82.1438, 103.1958),
        (80.1787, 103.1964), (67.0512, 115.4381), (71.0638, 122.3869)]
outline = Polygon(LOOP)
CLR = 0.10

def pad_poly(pd):
    r = box(-pd['sx'] / 2, -pd['sy'] / 2, pd['sx'] / 2, pd['sy'] / 2)
    r = rotate(r, pd['rot'], origin=(0, 0))
    return translate(r, pd['x'], pd['y'])

pads = []
for pd in G['pads']:
    pd = dict(pd); pd['poly'] = pad_poly(pd); pads.append(pd)
tracks = []
for t in G['tracks']:
    t = dict(t)
    t['poly'] = LineString([(t['x1'], t['y1']), (t['x2'], t['y2'])]).buffer(t['w'] / 2, cap_style=1)
    tracks.append(t)
vias = []
for v in G['vias']:
    v = dict(v); v['poly'] = Point(v['x'], v['y']).buffer(v['d'] / 2); vias.append(v)
for tp in T['taps']:
    vd = tp.get('vd', 0.6)
    vias.append({'net': 'GND', 'x': tp['vx'], 'y': tp['vy'], 'd': vd,
                 'poly': Point(tp['vx'], tp['vy']).buffer(vd / 2)})
    tracks.append({'net': 'GND', 'layer': 'F', 'x1': tp['px'], 'y1': tp['py'],
                   'x2': tp['vx'], 'y2': tp['vy'], 'w': 0.3,
                   'poly': LineString([(tp['px'], tp['py']), (tp['vx'], tp['vy'])]).buffer(0.15, cap_style=1)})
for ch in T.get('chains', []):
    pts = ch['path']
    for i in range(len(pts) - 1):
        tracks.append({'net': 'GND', 'layer': 'F', 'x1': pts[i][0], 'y1': pts[i][1],
                       'x2': pts[i + 1][0], 'y2': pts[i + 1][1], 'w': 0.25,
                       'poly': LineString([pts[i], pts[i + 1]]).buffer(0.125, cap_style=1)})

def clear_of(shape, layers, extra=CLR):
    for pd in pads:
        if pd['net'] == 'GND':
            continue
        if not set(pd['layers']) & set(layers) and not pd['pth']:
            continue
        if shape.distance(pd['poly']) < extra:
            return False
    for t in tracks:
        if t['net'] == 'GND' or t['layer'] not in layers:
            continue
        if shape.distance(t['poly']) < extra:
            return False
    for v in vias:
        if v['net'] == 'GND':
            continue
        if shape.distance(v['poly']) < extra:
            return False
    return True

padmap = {pd['ref']: pd for pd in pads}
new_taps, still = [], []
for ref in T['failed']:
    pd = padmap[ref]
    cx, cy = pd['x'], pd['y']
    done = False
    for radius in [0.8 + 0.15 * i for i in range(17)]:
        for adeg in range(0, 360, 5):
            a = math.radians(adeg)
            vx, vy = cx + radius * math.cos(a), cy + radius * math.sin(a)
            via = Point(vx, vy).buffer(0.25)
            if not outline.contains(via.buffer(0.12)):
                continue
            stub = LineString([(cx, cy), (vx, vy)]).buffer(0.10, cap_style=1)
            if clear_of(via, ('F', 'I2', 'B')) and clear_of(stub, ('F',)):
                new_taps.append({'pad': ref, 'vx': round(vx, 3), 'vy': round(vy, 3),
                                 'px': cx, 'py': cy, 'vd': 0.5, 'sw': 0.2})
                vias.append({'net': 'GND', 'x': vx, 'y': vy, 'd': 0.5, 'poly': via})
                done = True
                break
        if done:
            break
    if not done:
        still.append(ref)
print('fh12 taps:', len(new_taps), 'still:', still)
T['taps'] += new_taps
T['failed'] = still
json.dump(T, open('taps.json', 'w'), indent=1)
