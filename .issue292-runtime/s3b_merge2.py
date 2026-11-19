"""S3b v2: multi-island merger with CACHED obstacle indices.
Indices built once per (layer, inflate); new routes are appended
(buffered once) and only that layer's trees rebuilt.
Rules: w=0.10 (0.30 SYS_3V3/VBUS), clr 0.10; ANT strip = all-layer
obstacle (zero pre-existing tracks); trackpad circle NOT an obstacle
(190 pre-existing tracks inside)."""
import pcbnew as p, math, heapq
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
BPATH = TREE/'wmain.kicad_pcb'
b = p.LoadBoard(str(BPATH))
LAYN = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}
LAYI = {'F': p.F_Cu, 'I1': p.In1_Cu, 'I2': p.In2_Cu, 'B': p.B_Cu}
ANT = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
WIDE = {'SYS_3V3': 0.3, 'VBUS': 0.3}
INFLATES = (0.10, 0.15, 0.25)

def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx*c - dy*s, cy + dx*s + dy*c) for dx, dy in
                    ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])

items = {}
def add_item(net, kind, layers, shape, pts):
    items.setdefault(net, []).append({'kind': kind, 'layers': layers, 'shape': shape, 'pts': pts})
ALL_PADS = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        cx, cy = p.ToMM(pos.x), p.ToMM(pos.y)
        poly = rect_poly(cx, cy, p.ToMM(sz.x), p.ToMM(sz.y), pad.GetOrientationDegrees())
        ALL_PADS.append(poly)
        layers = {'F', 'I1', 'I2', 'B'} if pad.GetAttribute() == p.PAD_ATTRIB_PTH else {'F'}
        add_item(pad.GetNetname(), 'pad', layers, poly, [(cx, cy)])
for t in b.GetTracks():
    net = t.GetNetname()
    if isinstance(t, p.PCB_VIA):
        cx, cy = p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)
        add_item(net, 'via', {'F', 'I1', 'I2', 'B'}, Point(cx, cy).buffer(p.ToMM(t.GetWidth(p.F_Cu))/2), [(cx, cy)])
    else:
        L = LAYN.get(t.GetLayer())
        if not L: continue
        s, e2 = t.GetStart(), t.GetEnd()
        pts = [(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e2.x), p.ToMM(e2.y))]
        add_item(net, 'trk', {L}, LineString(pts).buffer(p.ToMM(t.GetWidth())/2), pts)
PADTREE = STRtree(ALL_PADS)

# ---- cached indices: (layer, inflate) -> [tree, shapes, nets]
IDX = {}
def build_idx():
    for L in ('F', 'I1', 'I2', 'B'):
        src = []
        for n, its in items.items():
            for it in its:
                if L in it['layers']: src.append((n, it['shape']))
        src.append(('__ANT__', ANT))
        for infl in INFLATES:
            shapes = [s.buffer(infl) for _, s in src]
            IDX[(L, infl)] = [STRtree(shapes), shapes, [n for n, _ in src]]
build_idx()
def hit(net, layer, infl, geom):
    tree, shapes, nets = IDX[(layer, infl)]
    return any(nets[i] != net and shapes[i].intersects(geom) for i in tree.query(geom))
def idx_append(net, layer, shape):
    for infl in INFLATES:
        ent = IDX[(layer, infl)]
        ent[1].append(shape.buffer(infl)); ent[2].append(net)
        ent[0] = STRtree(ent[1])
def via_legal(net, x, y, clr=0.10):
    vc = Point(x, y).buffer(0.3)
    if any(ALL_PADS[i].intersects(vc) for i in PADTREE.query(vc)): return False
    return not any(hit(net, L, clr, vc) for L in ('F', 'I1', 'I2', 'B'))

def components(net):
    its = items[net]
    parent = list(range(len(its)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    for i in range(len(its)):
        for j in range(i + 1, len(its)):
            if its[i]['layers'] & its[j]['layers'] and its[i]['shape'].intersects(its[j]['shape']):
                parent[find(i)] = find(j)
    comps = {}
    for i in range(len(its)): comps.setdefault(find(i), []).append(i)
    return list(comps.values())

STEP = 0.05
def astar(net, layer, a, bpt, w, clr=0.10):
    infl = 0.25 if w > 0.1 else 0.15
    x0 = math.floor((min(a[0], bpt[0]) - 2.5)/STEP)*STEP; x1 = math.ceil((max(a[0], bpt[0]) + 2.5)/STEP)*STEP
    y0 = math.floor((min(a[1], bpt[1]) - 2.5)/STEP)*STEP; y1 = math.ceil((max(a[1], bpt[1]) + 2.5)/STEP)*STEP
    start = (round((a[0]-x0)/STEP), round((a[1]-y0)/STEP))
    goal = (round((bpt[0]-x0)/STEP), round((bpt[1]-y0)/STEP))
    openh = [(0.0, 0.0, start)]; came, cost = {}, {start: 0.0}
    while openh:
        f, g, cur = heapq.heappop(openh)
        if g > cost.get(cur, 1e18): continue
        if cur == goal:
            path = []; c = cur
            while c != start:
                path.append((round(x0 + c[0]*STEP, 2), round(y0 + c[1]*STEP, 2))); c = came[c]
            path.append(a); path.reverse(); return path
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nk = (cur[0]+dx, cur[1]+dy); nx, ny = x0 + nk[0]*STEP, y0 + nk[1]*STEP
                if not (x0 <= nx <= x1 and y0 <= ny <= y1): continue
                if nk != goal and hit(net, layer, infl, Point(nx, ny)): continue
                ng = g + math.hypot(dx, dy)*STEP
                if ng < cost.get(nk, 1e18):
                    cost[nk] = ng; came[nk] = cur
                    heapq.heappush(openh, (ng + math.hypot(goal[0]-nk[0], goal[1]-nk[1])*STEP, ng, nk))
    return None

def simplify(path):
    if len(path) <= 2: return path
    out = [path[0]]
    for i in range(1, len(path) - 1):
        ax, ay = out[-1]; bx, by = path[i]; cx, cy = path[i+1]
        if abs((bx-ax)*(cy-by) - (by-ay)*(cx-bx)) > 1e-9: out.append(path[i])
    out.append(path[-1]); return out
def add_track(net, x0, y0, x1, y1, w, layer):
    t = p.PCB_TRACK(b); t.SetNet(b.FindNet(net))
    t.SetStart(p.VECTOR2I(round(x0*1e6), round(y0*1e6))); t.SetEnd(p.VECTOR2I(round(x1*1e6), round(y1*1e6)))
    t.SetWidth(int(w*1e6)); t.SetLayer(LAYI[layer]); b.Add(t)
    shp = LineString([(x0, y0), (x1, y1)]).buffer(w/2)
    add_item(net, 'trk', {layer}, shp, [(x0, y0), (x1, y1)])
    idx_append(net, layer, shp)
def add_via(net, x, y):
    v = p.PCB_VIA(b); v.SetNet(b.FindNet(net))
    v.SetPosition(p.VECTOR2I(round(x*1e6), round(y*1e6)))
    v.SetWidth(int(0.6*1e6)); v.SetDrill(int(0.3*1e6)); v.SetViaType(p.VIATYPE_THROUGH); b.Add(v)
    shp = Point(x, y).buffer(0.3)
    add_item(net, 'via', {'F', 'I1', 'I2', 'B'}, shp, [(x, y)])
    for L in ('F', 'I1', 'I2', 'B'): idx_append(net, L, shp)

def endpoint_options(comp, its):
    opts = []
    for i in comp:
        it = its[i]
        for pt in it['pts']: opts.append((pt, it['layers']))
    return opts

total_added = 0
for net in sorted(items):
    if net in ('', 'GND'): continue
    w = WIDE.get(net, 0.1)
    for _round in range(6):
        comps = components(net)
        if len(comps) <= 1: break
        its = items[net]
        cands = []
        for ci in range(len(comps)):
            for cj in range(ci + 1, len(comps)):
                for pa, la in endpoint_options(comps[ci], its):
                    for pb, lb in endpoint_options(comps[cj], its):
                        cands.append((math.hypot(pa[0]-pb[0], pa[1]-pb[1]), pa, la, pb, lb))
        cands.sort(key=lambda c: c[0])
        done = False
        for d, pa, la, pb, lb in cands[:10]:
            for Lr in ('I2', 'B', 'F'):
                need_a = Lr not in la; need_b = Lr not in lb
                if need_a and not via_legal(net, *pa): continue
                if need_b and not via_legal(net, *pb): continue
                path = astar(net, Lr, pa, pb, w)
                if not path: continue
                path = simplify(path)
                for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, Lr)
                if need_a: add_via(net, *pa)
                if need_b: add_via(net, *pb)
                total_added += 1; done = True
                print(net, 'merged via', Lr, 'dist', round(d, 2), 'vias', need_a, need_b, flush=True)
                break
            if done: break
        if not done:
            print(net, 'MERGE FAILED at comps', len(comps), 'closest', round(cands[0][0], 2), flush=True); break
    print(net, 'components now:', len(components(net)), flush=True)
b.Save(str(BPATH))
print('saved; routes added:', total_added)
