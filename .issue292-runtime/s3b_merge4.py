"""S3b v3: merger with shape-seeded A* (pads are targets, not points),
per-net checkpoint save, cached indices, bitmap-blocked A*.
Rules: w=0.10 (0.30 SYS_3V3/VBUS), clr 0.10; ANT strip obstacle on
all layers; trackpad circle not an obstacle."""
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
def astar(net, layer, seed_shape, goal_shape, w):
    """Route from any cell touching seed_shape to any cell touching
    goal_shape (shapes pre-buffered by caller with w/2). Blocked
    bitmap rasterized once per call."""
    infl = 0.25 if w > 0.1 else 0.15
    sb, gb = seed_shape.bounds, goal_shape.bounds
    x0 = math.floor((min(sb[0], gb[0]) - 5.0)/STEP)*STEP; x1 = math.ceil((max(sb[2], gb[2]) + 5.0)/STEP)*STEP
    y0 = math.floor((min(sb[1], gb[1]) - 5.0)/STEP)*STEP; y1 = math.ceil((max(sb[3], gb[3]) + 5.0)/STEP)*STEP
    nx, ny = int(round((x1-x0)/STEP)) + 1, int(round((y1-y0)/STEP)) + 1
    tree, shapes, nets = IDX[(layer, infl)]
    blocked = bytearray(nx*ny)
    for gy in range(ny):
        y = y0 + gy*STEP
        for gx in range(nx):
            pt = Point(x0 + gx*STEP, y)
            if any(nets[i] != net and shapes[i].intersects(pt) for i in tree.query(pt)):
                blocked[gy*nx + gx] = 1
    def cells_of(shape):
        out = set()
        bx0, by0, bx1, by1 = shape.bounds
        for gy in range(max(0, int((by0-y0)/STEP)), min(ny, int((by1-y0)/STEP) + 2)):
            for gx in range(max(0, int((bx0-x0)/STEP)), min(nx, int((bx1-x0)/STEP) + 2)):
                if shape.intersects(Point(x0 + gx*STEP, y0 + gy*STEP)):
                    out.add((gx, gy))
        return out
    seeds = cells_of(seed_shape); goals = cells_of(goal_shape)
    if not seeds or not goals: return None
    openh = []; came, cost = {}, {}
    for s in seeds:
        cost[s] = 0.0; heapq.heappush(openh, (0.0, 0.0, s))
    goal = None
    gxg, gyg = next(iter(goals))
    while openh:
        f, g, cur = heapq.heappop(openh)
        if g > cost.get(cur, 1e18): continue
        if cur in goals: goal = cur; break
        cx, cy = cur
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0: continue
                nk = (cx + dx, cy + dy)
                if not (0 <= nk[0] < nx and 0 <= nk[1] < ny): continue
                if nk not in goals and blocked[nk[1]*nx + nk[0]]: continue
                ng = g + math.hypot(dx, dy)*STEP
                if ng < cost.get(nk, 1e18):
                    cost[nk] = ng; came[nk] = cur
                    heapq.heappush(openh, (ng + math.hypot(gxg-nk[0], gyg-nk[1])*STEP, ng, nk))
    if goal is None: return None
    path = []; c = goal
    while c in came:
        path.append((round(x0 + c[0]*STEP, 2), round(y0 + c[1]*STEP, 2))); c = came[c]
    path.append((round(x0 + c[0]*STEP, 2), round(y0 + c[1]*STEP, 2)))
    path.reverse(); return path

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


def extend(path, amt=0.11):
    if len(path) >= 2:
        (x0, y0), (x1, y1) = path[0], path[1]
        d = math.hypot(x1-x0, y1-y0) or 1
        path[0] = (round(x0 - (x1-x0)/d*amt, 2), round(y0 - (y1-y0)/d*amt, 2))
        (x0, y0), (x1, y1) = path[-1], path[-2]
        d = math.hypot(x1-x0, y1-y0) or 1
        path[-1] = (round(x0 - (x1-x0)/d*amt, 2), round(y0 - (y1-y0)/d*amt, 2))
    return path

def stub_via(net, item, pt, other_pt, w):
    """Find a via point near pt (on the way toward other_pt) whose
    straight stub from pt on the item's native layer is clear at
    clr 0.10 outside the item's own shape. Returns (via_pt, layer)
    or None."""
    layer = next(iter(item['layers']))
    dx, dy = other_pt[0]-pt[0], other_pt[1]-pt[1]
    dd = math.hypot(dx, dy) or 1
    ux, uy = dx/dd, dy/dd
    for dist in (0.8, 1.1, 1.4, 0.6, 1.7, 2.0):
        for off in (0.0, 0.3, -0.3, 0.6, -0.6):
            vx = round(pt[0] + ux*dist - uy*off, 2)
            vy = round(pt[1] + uy*dist + ux*off, 2)
            if not via_legal(net, vx, vy): continue
            # stub clearance: sample the exposed part of pt->via
            ok = True
            steps = max(2, int(math.hypot(vx-pt[0], vy-pt[1]) / 0.05))
            for k in range(steps + 1):
                sx = pt[0] + (vx-pt[0]) * k/steps
                sy = pt[1] + (vy-pt[1]) * k/steps
                if item['shape'].buffer(0.02).contains(Point(sx, sy)): continue
                if hit(net, layer, 0.15, Point(sx, sy)): ok = False; break
            if ok: return (vx, vy), layer
    return None

total_added = 0
for net in sorted(items):
    if net in ('', 'GND'): continue
    w = WIDE.get(net, 0.1)
    changed = False
    bad = set()
    for _round in range(10):
        comps = components(net)
        if len(comps) <= 1: break
        ncomp_before = len(comps)
        its = items[net]
        cands = []
        for ci in range(len(comps)):
            for cj in range(ci + 1, len(comps)):
                for i in comps[ci]:
                    for j in comps[cj]:
                        for pa in its[i]['pts']:
                            for pb in its[j]['pts']:
                                cands.append((math.hypot(pa[0]-pb[0], pa[1]-pb[1]),
                                              its[i], pa, its[j], pb))
        # via endpoints first (layer-flexible: no stub needed),
        # then by distance
        cands.sort(key=lambda c: (0 if (c[1]['kind'] == 'via' or c[3]['kind'] == 'via') else 1, c[0]))
        done = False
        seen_ep = set()
        tried = 0
        for d, ia, pa, ib, pb in cands:
            if tried >= 40: break
            epk = (round(pa[0]), round(pa[1]), round(pb[0]), round(pb[1]))
            if epk in seen_ep: continue
            seen_ep.add(epk); tried += 1
            for Lr in ('I2', 'B', 'F'):
                key = (pa, pb, Lr)
                if key in bad: continue
                # resolve side A
                def side(item, pt, other):
                    if Lr in item['layers']:
                        return (item['shape'].buffer(w/2), None, None)
                    if via_legal(net, *pt):
                        return (Point(*pt).buffer(0.3 + w/2), pt, None)
                    sv = stub_via(net, item, pt, other, w)
                    if sv:
                        vp, _lay = sv
                        return (Point(*vp).buffer(0.3 + w/2), vp, (pt, vp))
                    return None
                sa = side(ia, pa, pb); sb = side(ib, pb, pa)
                if sa is None or sb is None: continue
                path = astar(net, Lr, sa[0], sb[0], w)
                if not path: bad.add(key); continue
                path = extend(simplify(path))
                for i in range(len(path) - 1): add_track(net, *path[i], *path[i+1], w, Lr)
                for sres, item, pt in ((sa, ia, pa), (sb, ib, pb)):
                    if sres[2]:
                        (x0, y0), (x1, y1) = sres[2]
                        add_track(net, x0, y0, x1, y1, w, next(iter(item['layers'])))
                    if sres[1]: add_via(net, *sres[1])
                total_added += 1; changed = True; done = True
                ncomp_after = len(components(net))
                print(net, 'merged via', Lr, 'dist', round(d, 2),
                      'comps', ncomp_before, '->', ncomp_after, flush=True)
                if ncomp_after >= ncomp_before:
                    print(net, 'WARNING: merge did not reduce components', flush=True)
                    bad.add(key)
                break
            if done: break
        if not done:
            print(net, 'MERGE FAILED at comps', len(comps), 'closest', round(cands[0][0], 2), flush=True); break
    print(net, 'components now:', len(components(net)), flush=True)
    if changed: b.Save(str(BPATH))
print('saved; routes added:', total_added)
