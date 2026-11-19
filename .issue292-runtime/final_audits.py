import pcbnew as p, math, json
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
import importlib.util
spec = importlib.util.spec_from_file_location('cc', 'hardware/kicad/qualification/issue-292-wmain/checks/copper_containment.py')
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)
def mm(v): return v / 1e6
import sys; b = p.LoadBoard(sys.argv[1])

# --- outline delta vs Rev.10 ---
rev = p.LoadBoard('hardware/kicad/qualification/issue-275-main-rev10/main-rev10/main.kicad_pcb')
o1 = cc.outline_poly(b); o2 = cc.outline_poly(rev)
c1 = list(o1.exterior.coords); c2 = list(o2.exterior.coords)
print('outline: work verts', len(c1), 'rev10 verts', len(c2), 'identical:', c1 == c2,
      'symdiff area:', round(o1.symmetric_difference(o2).area, 6))

# --- collect shapes ---
pads = []   # (ref, num, net, polyF)
for f in b.GetFootprints():
    ref = f.GetReference()
    for pad in f.Pads():
        pos = pad.GetPosition(); c = (mm(pos.x), mm(pos.y))
        sz = pad.GetSize(); w, h = mm(sz.x), mm(sz.y)
        if pad.GetShape() == p.PAD_SHAPE_CIRCLE:
            poly = Point(c).buffer(w / 2, quad_segs=16)
        else:
            rot = math.radians(pad.GetOrientationDegrees()); cs, sn = math.cos(rot), math.sin(rot)
            poly = Polygon([(c[0] + dx * cs - dy * sn, c[1] + dx * sn + dy * cs)
                            for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
        pads.append((ref, pad.GetNumber(), pad.GetNetname(), poly, c))
vias = []
tracks = {0: [], 2: [], 31: [], 4: []}
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition(); c = (mm(pos.x), mm(pos.y))
        vias.append((t.GetNetname(), c, Point(c).buffer(0.3, quad_segs=16)))
    else:
        s, e = t.GetStart(), t.GetEnd()
        a, bb = (mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))
        tracks.setdefault(t.GetLayer(), []).append(
            (t.GetNetname(), LineString([a, bb]).buffer(mm(t.GetWidth()) / 2, quad_segs=8), a, bb, mm(t.GetWidth())))

# --- via-pad audit: min clearance via -> foreign pad (F layer shapes; pads are F or thru) ---
worst = []
for net, c, vpoly in vias:
    for ref, num, pnet, ppoly, pc in pads:
        if pnet == net: continue
        if abs(pc[0] - c[0]) > 3 or abs(pc[1] - c[1]) > 3: continue
        d = vpoly.distance(ppoly)
        if d < 0.16: worst.append((round(d, 4), net, c, ref, num, pnet))
worst.sort()
print('via-pad min clearances (<0.16):', worst[:6])

# --- antenna strip + trackpad circle keep-outs (copper-free zones for signal; GND plane excluded by design on In1) ---
ant = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
tp = Point(100, 118).buffer(20, quad_segs=48)
bad_ant, bad_tp = [], []
for lay, lst in tracks.items():
    for net, poly, a, bb, w in lst:
        if poly.intersects(ant) and poly.intersection(ant).area > 1e-6: bad_ant.append((net, lay))
        if lay in (0, 31) and poly.intersects(tp) and poly.intersection(tp).area > 1e-6: bad_tp.append((net, lay))
for net, c, vpoly in vias:
    if vpoly.intersects(ant): bad_ant.append((net, 'via'))
    if vpoly.intersects(tp): bad_tp.append((net, 'via'))
for ref, num, pnet, ppoly, pc in pads:
    if ppoly.intersects(ant) and ppoly.intersection(ant).area > 1e-6: bad_ant.append((pnet, ref))
    if ppoly.intersects(tp) and ppoly.intersection(tp).area > 1e-6: bad_tp.append((pnet, ref))
print('antenna strip violations:', bad_ant[:5], 'count', len(bad_ant))
print('trackpad circle F/B violations:', bad_tp[:5], 'count', len(bad_tp))

# --- Wing census J2/J3 ---
for refname in ('J2', 'J3'):
    got = {}
    for ref, num, pnet, ppoly, pc in pads:
        if ref == refname and num: got[int(num)] = pnet
    print(refname, [got.get(i) for i in range(1, 15)])

# --- D-057 field minima: min clearance between different-net copper inside field rect ---
from shapely.geometry import box as sbox
field = sbox(69.3, 119.05, 80.9, 128.9)
shapes = []
for lay, lst in tracks.items():
    for net, poly, a, bb, w in lst:
        if poly.intersects(field): shapes.append((net, poly))
for net, c, vpoly in vias:
    if vpoly.intersects(field): shapes.append((net, vpoly))
for ref, num, pnet, ppoly, pc in pads:
    if ppoly.intersects(field): shapes.append((pnet, ppoly))
best = (9, None)
import itertools
for (n1, g1), (n2, g2) in itertools.combinations(shapes, 2):
    if n1 == n2: continue
    if g1.bounds[2] < g2.bounds[0] - 0.2 or g2.bounds[2] < g1.bounds[0] - 0.2: continue
    if g1.bounds[3] < g2.bounds[1] - 0.2 or g2.bounds[3] < g1.bounds[1] - 0.2: continue
    d = g1.distance(g2)
    if d < best[0]: best = (d, (n1, n2))
print('in-field min different-net clearance:', round(best[0], 4), best[1], f'({len(shapes)} shapes)')
