"""S3a-final: unified escapes, order = caged-perimeter trio first
(ADC_C/MUX_A1/SWDCLK, whose corridors the interior escapes seal),
then the 12 interior nets (proven feasible set), then the other
perimeter nets. Per-net fallback chain:
  T1: F-escape at design width (clr design->0.05) to edge via
  T1b: F-escape at w=0.05/clr=0.05 to edge via (perimeter only)
  T2: F stub (design width, clr 0.05) -> drop via -> B run to edge
  T3: F stub (0.05, clr 0.05) -> drop via -> B run to edge
One obstacle universe, grown after every net.
Output: escapes_final.json"""
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

raw = {'F': [], 'I1': [], 'I2': [], 'B': []}
LAYN = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
ALL_PADS = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y), pad.GetOrientationDegrees())
        ALL_PADS.append(poly)
        if pad.IsOnLayer(p.F_Cu): raw['F'].append((pad.GetNetname(), poly))
        if pad.GetAttribute() == p.PAD_ATTRIB_PTH:
            for L in ('I1', 'I2', 'B'): raw[L].append((pad.GetNetname(), poly))
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        c = Point(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth(p.F_Cu)) / 2)
        for L in raw: raw[L].append((t.GetNetname(), c))
    else:
        L = LAYN.get(t.GetLayer())
        if L:
            s, e = t.GetStart(), t.GetEnd()
            raw[L].append((t.GetNetname(), LineString([(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))]).buffer(p.ToMM(t.GetWidth()) / 2)))
ANT = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
CIRC = Point(100, 118).buffer(20.0)
PADTREE = STRtree(ALL_PADS)

def index_for(net, layer, inflate):
    shapes = [s.buffer(inflate) for n, s in raw[layer] if n != net]
    if layer in ('F', 'B'): shapes += [ANT.buffer(inflate), CIRC.buffer(inflate)]
    return STRtree(shapes), shapes
def blocked(idx, x, y, r=0.0):
    pt = Point(x, y).buffer(r) if r else Point(x, y)
    tree, shapes = idx
    return any(shapes[i].intersects(pt) for i in tree.query(pt))
def via_legal(net, x, y, clr):
    vc = Point(x, y).buffer(0.3)
    if any(ALL_PADS[i].intersects(vc) for i in PADTREE.query(vc)): return False
    for L in ('F', 'I1', 'I2', 'B'):
        if blocked(index_for(net, L, clr), x, y, 0.3): return False
    return True

u1 = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
pad_of = {}
for pad in u1.Pads():
    if pad.GetNetname(): pad_of.setdefault(pad.GetNetname(), []).append(pad)

def astar(net, layer, sx, sy, w, clr, goal_fn, box=BOX):
    idx = index_for(net, layer, clr + w / 2)
    x0, x1, y0, y1 = CX - box, CX + box, CY - box, CY + box
    def hfun(x, y): return min(x - x0, x1 - x, y - y0, y1 - y)
    start = (round((sx - x0) / STEP), round((sy - y0) / STEP))
    openh = [(0.0, 0.0, start)]; came, cost = {}, {start: 0.0}; goal = None
    while openh:
        f, g, cur = heapq.heappop(openh)
        if g > cost.get(cur, 1e18): continue
        cx, cy = x0 + cur[0] * STEP, y0 + cur[1] * STEP
        if cur != start and goal_fn(cx, cy):
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
    if goal is None: return None
    path = []; cur = goal
    while cur != start:
        path.append((round(x0 + cur[0] * STEP, 2), round(y0 + cur[1] * STEP, 2)))
        cur = came[cur]
    path.append((round(sx, 2), round(sy, 2))); path.reverse()
    return path

def on_edge(x, y, box=BOX):
    return abs(x - CX) >= box - 0.01 or abs(y - CY) >= box - 0.01

def grow_f(net, path, w):
    for i in range(len(path) - 1):
        raw['F'].append((net, LineString([path[i], path[i + 1]]).buffer(w / 2)))
def grow_b(net, path, w):
    for i in range(len(path) - 1):
        raw['B'].append((net, LineString([path[i], path[i + 1]]).buffer(w / 2)))
def grow_via(net, pt):
    vc = Point(*pt).buffer(0.3)
    for L in raw: raw[L].append((net, vc))

out = {}
def route_net(net, wdesign, clrdesign):
    pad = pad_of[net][0]
    sx, sy = p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y)
    # T1: F escape at design width
    for clr in ([clrdesign] if clrdesign == 0.05 else [clrdesign, 0.05]):
        path = astar(net, 'F', sx, sy, wdesign, clr,
                     lambda x, y: on_edge(x, y) and via_legal(net, x, y, 0.10))
        if path:
            out[net] = {'path': path, 'via': list(path[-1]), 'width': wdesign, 'clr': clr, 'tier': '1'}
            grow_f(net, path, wdesign); grow_via(net, path[-1])
            print(net, 'T1 w', wdesign, 'clr', clr, 'via', path[-1]); return True
    # T1b: F escape at 0.05
    path = astar(net, 'F', sx, sy, 0.05, 0.05,
                 lambda x, y: on_edge(x, y) and via_legal(net, x, y, 0.10))
    if path:
        out[net] = {'path': path, 'via': list(path[-1]), 'width': 0.05, 'clr': 0.05, 'tier': '1b'}
        grow_f(net, path, 0.05); grow_via(net, path[-1])
        print(net, 'T1b via', path[-1]); return True
    # T2/T3: stub -> drop via -> B run
    for tier, sw in (('2', wdesign), ('3', 0.05)):
        stub = astar(net, 'F', sx, sy, sw, 0.05, lambda x, y: via_legal(net, x, y, 0.05))
        if not stub: continue
        dv = stub[-1]
        brun = None
        for bclr in (0.10, 0.05):
            brun = astar(net, 'B', dv[0], dv[1], wdesign, bclr, lambda x, y: on_edge(x, y))
            if brun: break
        if not brun: continue
        out[net] = {'tier': tier, 'width': wdesign,
                    'parts': [{'layer': 'F', 'path': stub, 'width': sw},
                              {'layer': 'B', 'path': brun, 'width': wdesign}],
                    'drop_via': list(dv), 'via': None, 'end': list(brun[-1]), 'end_layer': 'B'}
        grow_f(net, stub, sw); grow_via(net, dv); grow_b(net, brun, wdesign)
        print(net, 'T' + tier, 'drop', dv, 'B-end', brun[-1]); return True
    print(net, 'ALL TIERS FAILED'); return False

PHASE_A = [('ADC_C', 0.1, 0.10), ('MUX_A1', 0.1, 0.10), ('SWDCLK', 0.1, 0.10),
           ('USB_DP', 0.1, 0.10), ('USB_DM', 0.1, 0.10), ('VBUS', 0.3, 0.10)]
INTERIOR = ['PAD_SCL', 'BTN', 'PAD_EN', 'LED_DRV', 'PAD_DR', 'MUX_A0',
            'MUX_EN1', 'MUX_A2', 'RESET_N', 'MUX_EN0', 'HALL_PWR_EN', 'VBAT_GATE_M']
PHASE_C = [('ADC_A', 0.1, 0.10), ('ADC_B', 0.1, 0.10), ('VBAT_SENSE', 0.1, 0.10),
           ('PAD_SDA', 0.1, 0.10), ('SWDIO', 0.1, 0.10), ('SYS_3V3', 0.3, 0.10)]
for net, w, c in PHASE_A: route_net(net, w, c)
for net in INTERIOR: route_net(net, 0.05, 0.05)
for net, w, c in PHASE_C: route_net(net, w, c)
(E/'escapes_final.json').write_text(json.dumps(out, indent=1))
print('total escapes:', len(out), 'of 24')
