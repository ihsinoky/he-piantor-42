"""FH12 GND: edge-band chain per Rev.10 precedent - a GND track parallel
to the pad row on the outline side (offset 1.05 mm from pad centres),
short stubs from each GND pad, one via per connector at the band end."""
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

def clear_of(shape, layers, extra=CLR, skip_refs=()):
    for pd in pads:
        if pd['net'] == 'GND' or pd['ref'] in skip_refs:
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
results = {}
for conn, outward in (('J2', (0.681, 0.732)), ('J3', (-0.681, 0.732))):
    grefs = [r for r in T['failed'] if r.startswith(conn + '.')]
    grefs.sort(key=lambda r: int(r.split('.')[1]))
    pts = []
    for r in grefs:
        pd = padmap[r]
        pts.append((pd['x'] + outward[0] * 1.05, pd['y'] + outward[1] * 1.05))
    band = LineString(pts).buffer(0.125, cap_style=1)
    stubs = []
    ok = True
    for r, (bx, by) in zip(grefs, pts):
        pd = padmap[r]
        stub = LineString([(pd['x'], pd['y']), (bx, by)]).buffer(0.125, cap_style=1)
        stubs.append(stub)
        if not clear_of(stub, ('F',), skip_refs=(r,)):
            ok = False
    band_ok = clear_of(band, ('F',))
    # via at band extension beyond last point
    (lx, ly) = pts[-1]
    (fx, fy) = pts[0]
    dx, dy = lx - fx, ly - fy
    L = math.hypot(dx, dy)
    vx, vy = lx + dx / L * 1.3, ly + dy / L * 1.3
    via = Point(vx, vy).buffer(0.25)
    via_ok = outline.contains(via.buffer(0.12)) and clear_of(via, ('F', 'I2', 'B'))
    results[conn] = {'band_clear': band_ok, 'stubs_ok': ok, 'via': (round(vx, 2), round(vy, 2)), 'via_ok': via_ok,
                     'band_pts': [[round(x, 3), round(y, 3)] for (x, y) in pts], 'refs': grefs}
    print(conn, results[conn])
json.dump(results, open('fh12_bands.json', 'w'), indent=1)
