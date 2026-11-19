"""S3a-redo: UNIFIED micro-A* escapes for ALL 24 routed U1 nets from
the tree board (official FP, field ripped). Interior 12 first at
w=0.05/clr=0.05 (proven set), then perimeter 12 at their design
widths (0.1 signal, 0.3 power) with clr 0.10 falling back to 0.05.
Every escape grows the obstacle set for the next (the fix for the
s3a collision). Goal = via-legal point (0.6/0.3 via, 0.10 clearance
on F/I2/B) on the +-5.5mm box edge. ANT_LINK excluded (straight
segment at apply time). Output: escapes_unified.json"""
import pcbnew as p, math, json, heapq
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
CX, CY = 75.1, 124.85
STEP = 0.05
BOX = 5.5

def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])

raw = {'F': [], 'I2': [], 'B': []}
LAYN = {p.F_Cu: 'F', p.In2_Cu: 'I2', p.B_Cu: 'B'}
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y), pad.GetOrientationDegrees())
        if pad.IsOnLayer(p.F_Cu):
            raw['F'].append((pad.GetNetname(), poly))
        if pad.GetAttribute() == p.PAD_ATTRIB_PTH:
            for L in ('I2', 'B'):
                raw[L].append((pad.GetNetname(), poly))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        c = Point(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth(p.F_Cu)) / 2)
        for L in ('F', 'I2', 'B'):
            raw[L].append((t.GetNetname(), c))
    else:
        L = LAYN.get(t.GetLayer())
        if L:
            s, e = t.GetStart(), t.GetEnd()
            raw[L].append((t.GetNetname(), LineString([(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))]).buffer(p.ToMM(t.GetWidth()) / 2)))
ANT = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
CIRC = Point(100, 118).buffer(20.0)

def index_for(net, layer, inflate):
    shapes = [s.buffer(inflate) for n, s in raw[layer] if n != net]
    if layer == 'F':
        shapes += [ANT.buffer(inflate), CIRC.buffer(inflate)]
    return STRtree(shapes), shapes
def blocked(idx, x, y, r=0.0):
    pt = Point(x, y).buffer(r) if r else Point(x, y)
    tree, shapes = idx
    return any(shapes[i].intersects(pt) for i in tree.query(pt))
def via_legal(net, x, y):
    for L in ('F', 'I2', 'B'):
        if blocked(index_for(net, L, 0.1), x, y, 0.3):
            return False
    return True

u1 = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
pad_of = {}
for pad in u1.Pads():
    if pad.GetNetname():
        pad_of.setdefault(pad.GetNetname(), []).append(pad)
INTERIOR = ['PAD_SCL', 'BTN', 'PAD_EN', 'LED_DRV', 'PAD_DR', 'MUX_A0',
            'MUX_EN1', 'MUX_A2', 'RESET_N', 'MUX_EN0', 'HALL_PWR_EN', 'VBAT_GATE_M']
PERIM = [('ADC_A', 0.1), ('ADC_B', 0.1), ('ADC_C', 0.1), ('VBAT_SENSE', 0.1),
         ('PAD_SDA', 0.1), ('MUX_A1', 0.1), ('USB_DP', 0.1), ('USB_DM', 0.1),
         ('VBUS', 0.3), ('SWDIO', 0.1), ('SWDCLK', 0.1), ('SYS_3V3', 0.3)]
JOBS = [(n, 0.05, 0.05) for n in INTERIOR] + [(n, w, 0.10) for n, w in PERIM]
out = {}
x0, x1, y0, y1 = CX - BOX, CX + BOX, CY - BOX, CY + BOX
for net, w, clr in JOBS:
    pad = pad_of[net][0]
    sx, sy = p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y)
    path = None
    for clr_try in ([clr] if clr == 0.05 else [clr, 0.05]):
        idx = index_for(net, 'F', clr_try + w / 2)
        def hfun(x, y):
            return min(x - x0, x1 - x, y - y0, y1 - y)
        start = (round((sx - x0) / STEP), round((sy - y0) / STEP))
        openh = [(0.0, 0.0, start)]
        came, cost = {}, {start: 0.0}
        goal = None
        while openh:
            f, g, cur = heapq.heappop(openh)
            if g > cost.get(cur, 1e18): continue
            cx, cy = x0 + cur[0] * STEP, y0 + cur[1] * STEP
            if (abs(cx - CX) >= BOX - 0.01 or abs(cy - CY) >= BOX - 0.01) and via_legal(net, cx, cy):
                goal = cur; break
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    nk = (cur[0] + dx, cur[1] + dy)
                    nx, ny = x0 + nk[0] * STEP, y0 + nk[1] * STEP
                    if not (x0 <= nx <= x1 and y0 <= ny <= y1): continue
                    if blocked(idx, nx, ny): continue
                    ng = g + math.hypot(dx, dy) * STEP
                    if ng < cost.get(nk, 1e18):
                        cost[nk] = ng; came[nk] = cur
                        heapq.heappush(openh, (ng - hfun(nx, ny), ng, nk))
        if goal is None: continue
        path = []; cur = goal
        while cur != start:
            path.append((round(x0 + cur[0] * STEP, 2), round(y0 + cur[1] * STEP, 2)))
            cur = came[cur]
        path.append((round(sx, 2), round(sy, 2))); path.reverse()
        used_clr = clr_try; break
    if path is None:
        print(net, 'ESCAPE FAILED'); continue
    out[net] = {'path': path, 'via': list(path[-1]), 'width': w, 'clr': used_clr}
    for i in range(len(path) - 1):
        raw['F'].append((net, LineString([path[i], path[i + 1]]).buffer(w / 2)))
    vc = Point(path[-1][0], path[-1][1]).buffer(0.3)
    for L in ('F', 'I2', 'B'):
        raw[L].append((net, vc))
    print(net, 'w', w, 'clr', used_clr, 'pts', len(path), 'via', path[-1])
(E/'escapes_unified.json').write_text(json.dumps(out, indent=1))
print('done', len(out), 'of', len(JOBS))
