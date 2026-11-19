"""S3a-redo phase 2: the 6 nets that failed the unified F-escape
(ADC_B, ADC_C, VBAT_SENSE, MUX_A1, SWDCLK, SYS_3V3).
Tier 1b: F-escape at w=0.05/clr=0.05 (same as interior nets).
Tier 2: short F stub to a drop via (via-legal at 0.05, no pad
overlap), then B.Cu run (clr 0.10, fallback 0.05) to the box edge;
escape end is a B point, no end via.
Obstacles include the 18 unified escapes already found.
Merges results into escapes_unified.json (tier2 entries carry
'parts' + 'drop_via' + 'end_layer')."""
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
    if layer == 'F': shapes += [ANT.buffer(inflate), CIRC.buffer(inflate)]
    if layer == 'B': shapes += [ANT.buffer(inflate), CIRC.buffer(inflate)]
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

out = json.loads((E/'escapes_unified.json').read_text())
# grow obstacles with the 18 found escapes
for net, e in out.items():
    path = [tuple(q) for q in e['path']]
    for i in range(len(path) - 1):
        raw['F'].append((net, LineString([path[i], path[i + 1]]).buffer(e['width'] / 2)))
    vc = Point(*e['via']).buffer(0.3)
    for L in ('F', 'I1', 'I2', 'B'): raw[L].append((net, vc))

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

FAILED = [('ADC_B', 0.1), ('ADC_C', 0.1), ('VBAT_SENSE', 0.1),
          ('MUX_A1', 0.1), ('SWDCLK', 0.1), ('SYS_3V3', 0.3)]
for net, wdesign in FAILED:
    pad = pad_of[net][0]
    sx, sy = p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y)
    # Tier 1b: F escape at 0.05
    path = astar(net, 'F', sx, sy, 0.05, 0.05,
                 lambda x, y: on_edge(x, y) and via_legal(net, x, y, 0.10))
    if path:
        out[net] = {'path': path, 'via': list(path[-1]), 'width': 0.05, 'clr': 0.05, 'tier': '1b'}
        for i in range(len(path) - 1):
            raw['F'].append((net, LineString([path[i], path[i + 1]]).buffer(0.025)))
        vc = Point(*path[-1]).buffer(0.3)
        for L in ('F', 'I1', 'I2', 'B'): raw[L].append((net, vc))
        print(net, 'tier1b via', path[-1]); continue
    # Tier 2: F stub (design width) to drop via, then B run to edge
    stub = astar(net, 'F', sx, sy, wdesign, 0.05,
                 lambda x, y: via_legal(net, x, y, 0.05))
    if not stub:
        print(net, 'TIER2 STUB FAILED'); continue
    dv = stub[-1]
    brun = None
    for bclr in (0.10, 0.05):
        brun = astar(net, 'B', dv[0], dv[1], wdesign, bclr, lambda x, y: on_edge(x, y))
        if brun: break
    if not brun:
        print(net, 'TIER2 B-RUN FAILED'); continue
    out[net] = {'tier': '2', 'width': wdesign,
                'parts': [{'layer': 'F', 'path': stub, 'width': wdesign},
                          {'layer': 'B', 'path': brun, 'width': wdesign}],
                'drop_via': list(dv), 'via': None, 'end': list(brun[-1]), 'end_layer': 'B'}
    for i in range(len(stub) - 1):
        raw['F'].append((net, LineString([stub[i], stub[i + 1]]).buffer(wdesign / 2)))
    vc = Point(*dv).buffer(0.3)
    for L in ('F', 'I1', 'I2', 'B'): raw[L].append((net, vc))
    for i in range(len(brun) - 1):
        raw['B'].append((net, LineString([brun[i], brun[i + 1]]).buffer(wdesign / 2)))
    print(net, 'tier2 drop', dv, 'B-end', brun[-1], 'bclr', bclr)
(E/'escapes_unified.json').write_text(json.dumps(out, indent=1))
print('total escapes:', len(out))
