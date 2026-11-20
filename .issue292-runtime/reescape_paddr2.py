"""Re-escape PAD_DR: rip its field escape (F tracks in the field box
+ via at (76.0,119.35)), then A* a fresh 0.05-class escape from pad
50 against the CURRENT board (all other routing = obstacles), goal
= via-legal(0.10) point on the +-5.5mm box edge."""
import pcbnew as p, math, heapq, json
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
BPATH = TREE/'wmain.kicad_pcb'
b = p.LoadBoard(str(BPATH))
net = 'PAD_DR'
# --- no rip this time: ADD a second escape to the west-ring
# south slot (69.6, 128.2); the north escape stays. ---
GOAL_VIA = (69.6, 128.2)
print('adding second escape to', GOAL_VIA)
# --- rebuild obstacle universe from current board ---
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx*c - dy*s, cy + dx*s + dy*c) for dx, dy in
                    ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])
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
        c = Point(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2)
        for L in raw: raw[L].append((t.GetNetname(), c))
    else:
        L = LAYN.get(t.GetLayer())
        if L:
            s, e2 = t.GetStart(), t.GetEnd()
            raw[L].append((t.GetNetname(), LineString([(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e2.x), p.ToMM(e2.y))]).buffer(p.ToMM(t.GetWidth())/2)))
ANT = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
PADTREE = STRtree(ALL_PADS)
def idx_for(layer, inflate):
    shapes = [s.buffer(inflate) for n, s in raw[layer] if n != net]
    if layer in ('F', 'B'): shapes.append(ANT.buffer(inflate))
    return STRtree(shapes), shapes
def hit(idx, geom):
    tree, shapes = idx
    return any(shapes[i].intersects(geom) for i in tree.query(geom))
def via_legal(x, y, clr):
    vc = Point(x, y).buffer(0.3)
    if any(ALL_PADS[i].intersects(vc) for i in PADTREE.query(vc)): return False
    return not any(hit(idx_for(L, clr), vc) for L in ('F', 'I1', 'I2', 'B'))
CX, CY, STEP, BOX = 75.1, 124.85, 0.05, 5.5
idx = idx_for('F', 0.075)
x0, x1, y0, y1 = CX - BOX, CX + BOX, CY - BOX, CY + BOX
sx, sy = 76.42, 124.0
start = (round((sx - x0)/STEP), round((sy - y0)/STEP))
openh = [(0.0, 0.0, start)]; came, cost = {}, {start: 0.0}; goal = None
def on_edge(x, y): return abs(x - CX) >= BOX - 0.01 or abs(y - CY) >= BOX - 0.01
while openh:
    f, g, cur = heapq.heappop(openh)
    if g > cost.get(cur, 1e18): continue
    cx, cy = x0 + cur[0]*STEP, y0 + cur[1]*STEP
    if cur != start and on_edge(cx, cy) and via_legal(cx, cy, 0.10) and math.hypot(cx - 76.0, cy - 119.35) > 1.0:
        goal = cur; break
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx == 0 and dy == 0: continue
            nk = (cur[0] + dx, cur[1] + dy)
            nx, ny = x0 + nk[0]*STEP, y0 + nk[1]*STEP
            if not (x0 <= nx <= x1 and y0 <= ny <= y1): continue
            if hit(idx, Point(nx, ny)): continue
            ng = g + math.hypot(dx, dy)*STEP
            if ng < cost.get(nk, 1e18):
                cost[nk] = ng; came[nk] = cur
                heapq.heappush(openh, (ng, ng, nk))
if goal is None:
    print('RE-ESCAPE FAILED'); raise SystemExit(1)
path = []; cur = goal
while cur != start:
    path.append((round(x0 + cur[0]*STEP, 2), round(y0 + cur[1]*STEP, 2))); cur = came[cur]
path.append((sx, sy)); path.reverse()
print('new escape via:', path[-1], 'path pts:', len(path))
# simplify + draw
out = [path[0]]
for i in range(1, len(path) - 1):
    ax, ay = out[-1]; bx, by = path[i]; cx2, cy2 = path[i + 1]
    if abs((bx-ax)*(cy2-by) - (by-ay)*(cx2-bx)) > 1e-9: out.append(path[i])
out.append(path[-1])
for i in range(len(out) - 1):
    t = p.PCB_TRACK(b); t.SetNet(b.FindNet(net))
    t.SetStart(p.VECTOR2I(round(out[i][0]*1e6), round(out[i][1]*1e6)))
    t.SetEnd(p.VECTOR2I(round(out[i+1][0]*1e6), round(out[i+1][1]*1e6)))
    t.SetWidth(int(0.05*1e6)); t.SetLayer(p.F_Cu); b.Add(t)
v = p.PCB_VIA(b); v.SetNet(b.FindNet(net))
v.SetPosition(p.VECTOR2I(round(path[-1][0]*1e6), round(path[-1][1]*1e6)))
v.SetWidth(int(0.6*1e6)); v.SetDrill(int(0.3*1e6)); v.SetViaType(p.VIATYPE_THROUGH); b.Add(v)
b.Save(str(BPATH))
print('saved')
