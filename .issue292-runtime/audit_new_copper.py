"""Minimum clearance of this round's NEW copper (from route-*.json)
to other-net copper on the final board, per layer, split by
inside/outside MODULE_FIELD_FINE. Also checks new vias."""
import pcbnew as p, json, math
from pathlib import Path
from shapely.geometry import Polygon, LineString, Point
from shapely.strtree import STRtree
E = Path('.').resolve()
b = p.LoadBoard(str(E.parent/'hardware/kicad/qualification/issue-292-wmain/wmain.kicad_pcb'))
FIELD = Polygon([(69.3, 119.05), (80.9, 119.05), (80.9, 128.9), (69.3, 128.9)])
def mm(v): return p.ToMM(v)
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
LAYID = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
obs = {L: [] for L in ('F', 'I1', 'I2', 'B')}
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y), pad.GetOrientationDegrees())
        pth = pad.GetAttribute() == p.PAD_ATTRIB_PTH
        lays = ['F', 'I1', 'I2', 'B'] if pth else [LAYID[l] for l in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu) if pad.IsOnLayer(l)]
        for L in lays: obs[L].append((pad.GetNetname(), poly))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition()
        poly = Point(mm(pos.x), mm(pos.y)).buffer(mm(t.GetWidth(p.F_Cu)) / 2, resolution=12)
        for L in ('F', 'I1', 'I2', 'B'): obs[L].append((t.GetNetname(), poly))
    else:
        s, e = t.GetStart(), t.GetEnd()
        poly = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, resolution=4, cap_style=1)
        obs[LAYID[t.GetLayer()]].append((t.GetNetname(), poly))
trees = {L: STRtree([g for _, g in obs[L]]) for L in obs}
nets_of = {L: [n for n, _ in obs[L]] for L in obs}
jobs = [('VBAT_SENSE', 'route-vbat.json'), ('GND', 'route-gnd-via.json'), ('PAD_EN', 'route-paden.json'),
        ('SYS_3V3', 'route-sys1.json'), ('SYS_3V3', 'route-sys2.json'), ('VBUS', 'route-vbus.json')]
worst = {'in': (9, ''), 'out': (9, '')}
for net, fn in jobs:
    r = json.load(open(E/fn))
    for t in r['tracks']:
        seg = LineString([(t['x1'], t['y1']), (t['x2'], t['y2'])]).buffer(t['w'] / 2, resolution=4, cap_style=1)
        L = t['layer']
        for j in trees[L].query(seg.buffer(0.35)):
            n2, g2 = obs[L][j]
            if n2 == net: continue
            d = seg.distance(g2)
            key = 'in' if seg.intersects(FIELD) else 'out'
            if d < worst[key][0]: worst[key] = (round(d, 4), f"{net} {L} seg ({t['x1']},{t['y1']}) vs {n2}")
    for v in r['vias']:
        disc = Point(v['x'], v['y']).buffer(0.30, resolution=16)
        for L in ('F', 'I2', 'B'):
            for j in trees[L].query(disc.buffer(0.35)):
                n2, g2 = obs[L][j]
                if n2 == net: continue
                d = disc.distance(g2)
                key = 'in' if disc.intersects(FIELD) else 'out'
                if d < worst[key][0]: worst[key] = (round(d, 4), f"{net} via ({v['x']},{v['y']}) on {L} vs {n2}")
print('worst clearance of NEW copper INSIDE field :', worst['in'])
print('worst clearance of NEW copper OUTSIDE field:', worst['out'])
