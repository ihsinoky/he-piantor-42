"""Final GND taps for the 9 remaining pads, against geom_v13."""
import json, math
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
from pathlib import Path
E = Path('.').resolve()
G = json.loads((E/'geom_v13.json').read_text())
LAYERS = ['F', 'I2', 'B']
LOOP = [(64.1073, 134.4359), (66.1073, 137.9), (133.8927, 137.9), (135.8927, 134.4359),
        (131.926, 127.5657), (131.926, 96.8343), (135.8927, 90.9641), (135.8927, 87.5),
        (132.8927, 84.5), (67.1073, 84.5), (64.1073, 87.5), (64.1073, 90.9641),
        (68.074, 96.8343), (68.074, 127.5657)]
outline = Polygon(LOOP)
ANT = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])

def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])

shapes = {L: [] for L in LAYERS}
for p in G['pads']:
    if p['net'] == 'GND':
        continue
    poly = rect_poly(p['x'], p['y'], p['sx'], p['sy'], p['rot'])
    shapes['F'].append(poly)
    if p['pth']:
        for L in ('I2', 'B'):
            shapes[L].append(poly)
for t in G['tracks']:
    if t['net'] == 'GND':
        continue
    shapes[t['layer']].append(LineString([(t['x1'], t['y1']), (t['x2'], t['y2'])]).buffer(t['w'] / 2))
for v in G['vias']:
    if v['net'] == 'GND':
        continue
    for L in LAYERS:
        shapes[L].append(Point(v['x'], v['y']).buffer(v['d'] / 2))
trees = {L: STRtree(shapes[L]) for L in LAYERS}

def clear(L, shape, gap):
    tr, sh = trees[L], shapes[L]
    buf = shape.buffer(gap)
    for i in tr.query(buf):
        if sh[i].intersects(buf):
            return False
    return True

PADS = {'U1.7': (78.7, 124.525), 'U1.14': (77.375, 121.25), 'U1.16': (76.075, 121.25),
        'U1.18': (74.775, 121.25), 'U1.25': (71.5, 122.575), 'U1.31': (71.5, 126.475),
        'U3.2': (123.66, 128.8), 'U4.2': (118.16, 132.0), 'RVPD.2': (122.325, 130.2)}
out = []
for ref, (px, py) in PADS.items():
    found = None
    for vd in (0.6, 0.5):
        for r in (0.55, 0.7, 0.85, 1.0, 1.2, 1.45, 1.7, 2.0, 2.3):
            for k in range(24):
                a = 2 * math.pi * k / 24
                vx, vy = px + r * math.cos(a), py + r * math.sin(a)
                if not outline.contains(Point(vx, vy)) or ANT.contains(Point(vx, vy)):
                    continue
                stub = LineString([(px, py), (vx, vy)])
                if not clear('F', stub, 0.10 + 0.15):
                    continue
                via = Point(vx, vy).buffer(vd / 2)
                if all(clear(L, via, 0.10) for L in LAYERS):
                    found = {'ref': ref, 'px': px, 'py': py, 'vx': round(vx, 3), 'vy': round(vy, 3), 'vd': vd}
                    break
            if found: break
        if found: break
    print(ref, '->', found)
    if found:
        out.append(found)
        for L in LAYERS:
            shapes[L].append(Point(found['vx'], found['vy']).buffer(found['vd'] / 2))
        shapes['F'].append(LineString([(px, py), (found['vx'], found['vy'])]).buffer(0.15))
        trees = {L: STRtree(shapes[L]) for L in LAYERS}
json.dump(out, open(E/'taps_final.json', 'w'), indent=1)
print('planned', len(out), 'of', len(PADS))
