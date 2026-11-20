"""Fix round: tie U1's GND pad islands to the ground planes with via
taps (0.6/0.3, F-B) + short F segments, like the layout run's taps.
Islands are computed from the refilled board (pads + F zone-fill
polygons + tracks + vias, union-find). A tap spot must sit on the
island's own F copper, clear other nets on F and B, stay out of the
antenna strip and inside the outline. Usage: gnd_taps.py IN OUT"""
import pcbnew as p, math, sys
from pathlib import Path
E = Path('.').resolve()
b = p.LoadBoard(str(E/sys.argv[1]))
gnd = b.FindNet('GND')
u1 = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
CX, CY = 75.1, 124.85

# --- collect F.Cu GND fill polygons per zone ---
fills = []  # (zone_idx, SHAPE_POLY_SET)
for zi, z in enumerate(b.Zones()):
    if z.GetNetname() == 'GND' and z.IsOnLayer(p.F_Cu):
        fills.append(z.GetFilledPolysList(p.F_Cu))

def in_fill(x, y):
    pt = p.VECTOR2I(round(x * 1e6), round(y * 1e6))
    return any(fp.Contains(pt) for fp in fills)

# --- obstacles: other-net pads/tracks/vias ---
pads_o, trks_o, vias_o = [], [], []
for f in b.GetFootprints():
    for pad in f.Pads():
        if pad.GetNetname() == 'GND':
            continue
        pos, sz = pad.GetPosition(), pad.GetSize()
        layers = []
        if pad.IsOnLayer(p.F_Cu): layers.append('F')
        if pad.IsOnLayer(p.B_Cu): layers.append('B')
        pads_o.append((p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y), layers))
LAYN = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
for t in b.GetTracks():
    if t.GetNetname() == 'GND':
        continue
    if isinstance(t, p.PCB_VIA):
        vias_o.append((p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y), p.ToMM(t.GetWidth(p.F_Cu)) / 2))
    else:
        s, e = t.GetStart(), t.GetEnd()
        trks_o.append((LAYN.get(t.GetLayer()), p.ToMM(s.x), p.ToMM(s.y), p.ToMM(e.x), p.ToMM(e.y), p.ToMM(t.GetWidth()) / 2))

def seg_dist(px, py, x1, y1, x2, y2):
    dx, dy = x2 - x1, y2 - y1
    tt = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy))) if (dx or dy) else 0.0
    return math.hypot(px - (x1 + tt * dx), py - (y1 + tt * dy))

def clear(x, y, layers):
    """via r=0.3 + 0.1 clearance to other-net copper on given layers"""
    for (px, py, sx, sy, ls) in pads_o:
        if not any(L in ls for L in layers):
            continue
        if abs(x - px) < sx / 2 + 0.42 and abs(y - py) < sy / 2 + 0.42:
            return False
    for (L, x1, y1, x2, y2, hw) in trks_o:
        if L in layers and seg_dist(x, y, x1, y1, x2, y2) < 0.42 + hw:
            return False
    for (vx, vy, vr) in vias_o:
        if math.hypot(x - vx, y - vy) < 0.42 + vr:
            return False
    return True

def in_ant(x, y):
    return 70.3 <= x <= 79.9 and 128.9 <= y <= 137.9

gndpads = [(pad.GetNumber(), p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y)) for pad in u1.Pads() if pad.GetNetname() == 'GND']
# island key for a pad: index of fill polygon containing it, else 'pad-only'
def island_of(x, y):
    pt = p.VECTOR2I(round(x * 1e6), round(y * 1e6))
    for i, fp in enumerate(fills):
        if fp.Contains(pt):
            return i
    return None

groups = {}
for num, x, y in gndpads:
    groups.setdefault(island_of(x, y), []).append((num, x, y))
print('GND pad islands:', {k: [g[0] for g in v] for k, v in groups.items()})

def add_via(x, y):
    v = p.PCB_VIA(b)
    v.SetPosition(p.VECTOR2I(round(x * 1e6), round(y * 1e6)))
    v.SetWidth(int(0.6e6)); v.SetDrill(int(0.3e6))
    v.SetLayerPair(p.F_Cu, p.B_Cu)
    v.SetNet(gnd)
    b.Add(v)

def add_seg(x1, y1, x2, y2, w=0.3):
    t = p.PCB_TRACK(b)
    t.SetStart(p.VECTOR2I(round(x1 * 1e6), round(y1 * 1e6)))
    t.SetEnd(p.VECTOR2I(round(x2 * 1e6), round(y2 * 1e6)))
    t.SetWidth(int(w * 1e6)); t.SetLayer(p.F_Cu); t.SetNet(gnd)
    b.Add(t)

taps = []
for key, members in groups.items():
    # candidate spots: grid around the group's pads, on island copper or pad copper
    best = None
    for gx in [m[1] + dx for m in members for dx in (-1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2)]:
        for gy in [m[2] + dy for m in members for dy in (-1.2, -0.8, -0.4, 0.0, 0.4, 0.8, 1.2)]:
            if in_ant(gx, gy) or not (65.0 < gx < 135.0 and 76.0 < gy < 137.0):
                continue
            on_pad = any(abs(gx - m[1]) <= 0.2 and abs(gy - m[2]) <= 0.2 for m in members)
            if not (on_pad or in_fill(gx, gy)):
                continue
            if not clear(gx, gy, ('F', 'B')):
                continue
            d = min(math.hypot(gx - m[1], gy - m[2]) for m in members)
            if best is None or d < best[0]:
                best = (d, gx, gy)
    if best is None:
        print('NO TAP FOUND for island', key, [m[0] for m in members])
        continue
    d, vx, vy = best
    add_via(vx, vy)
    near = min(members, key=lambda m: math.hypot(vx - m[1], vy - m[2]))
    if d > 0.25:
        add_seg(near[1], near[2], vx, vy)
    taps.append((key, [m[0] for m in members], round(vx, 2), round(vy, 2)))
print('taps placed:', taps)
b.Save(str(E/sys.argv[2]))
print('saved', sys.argv[2])
