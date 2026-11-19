"""Fallback taps for the pads plan_taps.py could not serve:
(a) smaller via 0.5/0.3, (b) straight chain track to a tapped GND point,
(c) one-bend chain. Reads/writes taps.json (appends)."""
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
antenna = box(70.3, 128.9, 79.9, 137.9)
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
# register round-1 taps as obstacles/targets
targets = []
for tp in T['taps']:
    vias.append({'net': 'GND', 'x': tp['vx'], 'y': tp['vy'], 'd': 0.6,
                 'poly': Point(tp['vx'], tp['vy']).buffer(0.3)})
    tracks.append({'net': 'GND', 'layer': 'F', 'x1': tp['px'], 'y1': tp['py'],
                   'x2': tp['vx'], 'y2': tp['vy'], 'w': 0.3,
                   'poly': LineString([(tp['px'], tp['py']), (tp['vx'], tp['vy'])]).buffer(0.15, cap_style=1)})
    targets.append((tp['vx'], tp['vy']))
for pd in pads:
    if pd['net'] == 'GND' and 'F' in pd['layers']:
        targets.append((pd['x'], pd['y']))

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
new_taps, new_chains, still = [], [], []
for ref in T['failed']:
    pd = padmap[ref]
    cx, cy = pd['x'], pd['y']
    done = False
    # (a) 0.5 via
    for radius in (0.85, 1.05, 1.3, 1.6, 2.0):
        for adeg in range(0, 360, 15):
            a = math.radians(adeg)
            vx, vy = cx + radius * math.cos(a), cy + radius * math.sin(a)
            via = Point(vx, vy).buffer(0.25)
            if not outline.contains(via.buffer(0.12)) or antenna.intersects(via):
                continue
            stub = LineString([(cx, cy), (vx, vy)]).buffer(0.15, cap_style=1)
            if clear_of(via, ('F', 'I2', 'B')) and clear_of(stub, ('F',)):
                new_taps.append({'pad': ref, 'vx': round(vx, 3), 'vy': round(vy, 3),
                                 'px': cx, 'py': cy, 'vd': 0.5})
                vias.append({'net': 'GND', 'x': vx, 'y': vy, 'd': 0.5, 'poly': via})
                targets.append((vx, vy))
                done = True
                break
        if done:
            break
    if done:
        continue
    # (b) straight chain to nearest target
    cands = sorted(targets, key=lambda q: math.hypot(q[0] - cx, q[1] - cy))
    for (tx, ty) in cands[:14]:
        if math.hypot(tx - cx, ty - cy) < 0.4 or math.hypot(tx - cx, ty - cy) > 9:
            continue
        seg = LineString([(cx, cy), (tx, ty)]).buffer(0.125, cap_style=1)
        if clear_of(seg, ('F',)) and outline.contains(seg):
            new_chains.append({'pad': ref, 'path': [[cx, cy], [round(tx, 3), round(ty, 3)]]})
            tracks.append({'net': 'GND', 'layer': 'F', 'x1': cx, 'y1': cy, 'x2': tx, 'y2': ty,
                           'w': 0.25, 'poly': seg})
            done = True
            break
    if done:
        continue
    # (c) one-bend chain via midpoint offsets
    for (tx, ty) in cands[:8]:
        if math.hypot(tx - cx, ty - cy) > 10:
            continue
        for (mx, my) in [(tx, cy), (cx, ty), ((cx + tx) / 2 + 0.8, (cy + ty) / 2),
                         ((cx + tx) / 2 - 0.8, (cy + ty) / 2), ((cx + tx) / 2, (cy + ty) / 2 + 0.8),
                         ((cx + tx) / 2, (cy + ty) / 2 - 0.8)]:
            s1 = LineString([(cx, cy), (mx, my)]).buffer(0.125, cap_style=1)
            s2 = LineString([(mx, my), (tx, ty)]).buffer(0.125, cap_style=1)
            if clear_of(s1, ('F',)) and clear_of(s2, ('F',)) and outline.contains(s1) and outline.contains(s2):
                new_chains.append({'pad': ref, 'path': [[cx, cy], [round(mx, 3), round(my, 3)], [round(tx, 3), round(ty, 3)]]})
                done = True
                break
        if done:
            break
    if not done:
        still.append(ref)

print('small-via taps:', len(new_taps), 'chains:', len(new_chains), 'still failed:', still)
T['taps'] += new_taps
T['chains'] = new_chains
T['failed'] = still
json.dump(T, open('taps.json', 'w'), indent=1)
