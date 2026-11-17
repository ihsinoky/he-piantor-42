"""Issue #268 stage 3b: bridge remaining components, driven by the capsule
union-find (validated 1:1 against kicad-cli DRC), reusing bridge_base's
raster/A* machinery for pathfinding."""
import heapq, json, math, sys
import numpy as np
import pcbnew as p

exec(open('.issue268-runtime/bridge_base.py').read())

# ---------- capsule union-find over build2 Items ----------
def _seg_seg(a, b):
    (x1, y1, x2, y2), (x3, y3, x4, y4) = a, b
    def orient(px, py, qx, qy, rx, ry): return (qx-px)*(ry-py) - (qy-py)*(rx-px)
    def pt_seg(px, py, x1, y1, x2, y2):
        dx, dy = x2-x1, y2-y1
        L2 = dx*dx + dy*dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px-x1)*dx + (py-y1)*dy)/L2))
        return math.hypot(px-(x1+t*dx), py-(y1+t*dy))
    d1 = orient(x3, y3, x4, y4, x1, y1); d2 = orient(x3, y3, x4, y4, x2, y2)
    d3 = orient(x1, y1, x2, y2, x3, y3); d4 = orient(x1, y1, x2, y2, x4, y4)
    if ((d1 > 0) != (d2 > 0)) and ((d3 > 0) != (d4 > 0)): return 0.0
    return min(pt_seg(x1, y1, x3, y3, x4, y4), pt_seg(x2, y2, x3, y3, x4, y4),
               pt_seg(x3, y3, x1, y1, x2, y2), pt_seg(x4, y4, x1, y1, x2, y2))

def _item_segs(it):
    if it.kind == 'seg': return [(it.x1, it.y1, it.x2, it.y2)]
    if it.kind == 'via': return [(it.cx, it.cy, it.cx, it.cy)]
    th = math.radians(it.rot); c, s = math.cos(th), math.sin(th)
    pts = []
    for lx, ly in [(-it.hw, -it.hh), (it.hw, -it.hh), (it.hw, it.hh), (-it.hw, it.hh)]:
        pts.append((it.cx + lx*c - ly*s, it.cy + lx*s + ly*c))
    return [(pts[i][0], pts[i][1], pts[(i+1) % 4][0], pts[(i+1) % 4][1]) for i in range(4)] + \
           [(pts[0][0], pts[0][1], pts[2][0], pts[2][1]), (pts[1][0], pts[1][1], pts[3][0], pts[3][1])]

def _item_r(it):
    return 0.0 if it.kind == 'pad' else it.r

def capsule_comps(net):
    rows = [it for it in items if it.net == net]
    par = list(range(len(rows)))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    for i, a in enumerate(rows):
        for j in range(i+1, len(rows)):
            c = rows[j]
            if not (a.layers & c.layers): continue
            # bbox reject
            def bb(it):
                ss = _item_segs(it)
                xs = [q for s in ss for q in (s[0], s[2])]; ys = [q for s in ss for q in (s[1], s[3])]
                return min(xs), max(xs), min(ys), max(ys)
            ax0, ax1, ay0, ay1 = bb(a); cx0, cx1, cy0, cy1 = bb(c)
            m = _item_r(a) + _item_r(c) + 0.01
            if ax1 + m < cx0 or cx1 + m < ax0 or ay1 + m < cy0 or cy1 + m < ay0: continue
            d = min(_seg_seg(sa, sc) for sa in _item_segs(a) for sc in _item_segs(c)) - _item_r(a) - _item_r(c)
            if d <= 0.002: par[find(i)] = find(j)
    groups = {}
    for i, r in enumerate(rows): groups.setdefault(find(i), []).append(r)
    return list(groups.values())

def pad_labels(comp):
    labs = []
    for it in comp:
        if it.kind == 'pad':
            fp = it.obj.GetParentFootprint()
            labs.append(fp.GetReference() + '.' + it.obj.GetNumber())
    return labs

# ---------- A* multi-source (same as bridge.py) ----------
def astar_multi(blocked, viablocked, goal, startmask, hints):
    openh = []; came = {}; gs = {}
    idx = np.argwhere(np.stack([startmask[0], startmask[1]], axis=0))
    for l, y, x in idx.tolist():
        if blocked[l][y, x]: continue
        gs[(x, y, l)] = 0.0
        heapq.heappush(openh, (0.0, x, y, l))
    def hfun(x, y):
        gx, gy = WIN[0]+STEP*x, WIN[2]+STEP*y
        return 0.9*min(math.hypot(gx-hx, gy-hy) for hx, hy in hints)
    while openh:
        f, x, y, l = heapq.heappop(openh)
        if goal[l][y, x] and (x, y, l) in came:
            path = [(x, y, l)]
            while path[-1] in came: path.append(came[path[-1]])
            return path[::-1]
        g0 = gs[(x, y, l)]
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1),(1,1),(1,-1),(-1,1),(-1,-1)):
            nx_, ny_ = x+dx, y+dy
            if not (0 <= nx_ < NX and 0 <= ny_ < NY): continue
            if blocked[l][ny_, nx_]: continue
            if dx and dy and (blocked[l][y, nx_] or blocked[l][ny_, x]): continue
            ng = g0 + STEP*(1.4142 if dx and dy else 1.0)
            if ng < gs.get((nx_, ny_, l), 1e18):
                gs[(nx_, ny_, l)] = ng
                heapq.heappush(openh, (ng+hfun(nx_, ny_), nx_, ny_, l)); came[(nx_, ny_, l)] = (x, y, l)
        ol = 1-l
        if not viablocked[0][y, x] and not viablocked[1][y, x]:
            ng = g0 + 1.5
            if ng < gs.get((x, y, ol), 1e18):
                gs[(x, y, ol)] = ng
                heapq.heappush(openh, (ng+hfun(x, y), x, y, ol)); came[(x, y, ol)] = (x, y, l)
    return None

def xy_of(cx, cy): return (WIN[0]+STEP*cx, WIN[2]+STEP*cy)

def emit(net, path, target, width):
    gx, gy = xy_of(*path[-1][:2]); gl = path[-1][2]
    best = None
    for it in target:
        layers = {0 if gl == 0 else 2}
        if not (it.layers & layers): continue
        if it.kind == 'seg':
            vx, vy = it.x2-it.x1, it.y2-it.y1
            L2 = vx*vx + vy*vy
            t = 0 if L2 == 0 else max(0, min(1, ((gx-it.x1)*vx + (gy-it.y1)*vy)/L2))
            q = (it.x1 + t*vx, it.y1 + t*vy)
        else:
            q = (it.cx, it.cy)
        d = math.hypot(q[0]-gx, q[1]-gy)
        if best is None or d < best[0]: best = (d, q)
    pts = [(xy_of(x, y), l) for x, y, l in path]
    if best is not None and best[0] > 1e-6: pts.append((best[1], gl))
    simp = [pts[0]]
    for i in range(1, len(pts)-1):
        (ax, ay), al = simp[-1]; (bx, by), bl = pts[i]; (cx, cy), cl = pts[i+1]
        if al == bl == cl and abs((bx-ax)*(cy-ay) - (by-ay)*(cx-ax)) < 1e-9: continue
        simp.append(pts[i])
    simp.append(pts[-1])
    netcode = b.GetNetInfo().GetNetItem(net)
    nseg = nvia = 0; length = 0.0
    for i in range(len(simp)-1):
        (ax, ay), al = simp[i]; (bx, by), bl = simp[i+1]
        if al != bl:
            v = p.PCB_VIA(b); v.SetPosition(p.VECTOR2I(p.FromMM(ax), p.FromMM(ay)))
            v.SetWidth(p.FromMM(0.6)); v.SetDrill(p.FromMM(0.3)); v.SetNet(netcode)
            v.SetLayerPair(p.F_Cu, p.B_Cu); b.Add(v); nvia += 1
            it = Item(); it.net = net; it.obj = v; it.kind = 'via'; it.layers = {0, 2}
            it.r = 0.3; it.cx, it.cy = ax, ay; items.append(it)
        if (ax, ay) != (bx, by):
            t = p.PCB_TRACK(b)
            t.SetStart(p.VECTOR2I(p.FromMM(ax), p.FromMM(ay))); t.SetEnd(p.VECTOR2I(p.FromMM(bx), p.FromMM(by)))
            t.SetWidth(p.FromMM(width)); t.SetLayer(p.F_Cu if bl == 0 else p.B_Cu); t.SetNet(netcode)
            b.Add(t); nseg += 1; length += math.hypot(bx-ax, by-ay)
            it = Item(); it.net = net; it.obj = t; it.kind = 'seg'; it.layers = {0 if bl == 0 else 2}
            it.r = width/2; it.x1, it.y1, it.x2, it.y2 = ax, ay, bx, by; items.append(it)
    return nseg, nvia, length

results = []
for net in ['GND', 'MUX_A2']:
    width = 0.3 if net in POWER else 0.1
    for attempt in range(6):
        comps = [c for c in capsule_comps(net) if any(it.kind == 'pad' for it in c)]
        print(net, 'capsule pad comps:', [(len(c), sorted(set(pad_labels(c)))[:3]) for c in comps], flush=True)
        if len(comps) <= 1: break
        comps.sort(key=lambda c: -len(c))
        target = comps[0]
        # source: the comp whose pads are NOT in target, prefer one containing a J_WING pad
        rest = comps[1:]
        rest.sort(key=lambda c: 0 if any(l.startswith('J_WING') for l in pad_labels(c)) else 1)
        source = rest[0]
        blocked = raster_blocked(net, width, reserve=(net != 'GND'))
        viablocked = raster_blocked(net, width, via=True, reserve=(net != 'GND'))
        goal = goal_mask(target, width)
        startmask = goal_mask(source, width)
        hints = []
        for it in target:
            if it.kind == 'seg': hints += [(it.x1, it.y1), (it.x2, it.y2)]
            else: hints.append((it.cx, it.cy))
        path = astar_multi(blocked, viablocked, goal, startmask, hints)
        if path is None:
            print('BRIDGE2 FAIL', net, 'source pads:', sorted(set(pad_labels(source)))[:4], flush=True)
            b.Save(SRC); sys.exit(2)
        nseg, nvia, length = emit(net, path, target, width)
        results.append(dict(net=net, segs=nseg, vias=nvia, length_mm=round(length, 2)))
        print('bridged2', net, nseg, 'segs', nvia, 'vias', round(length, 1), 'mm', flush=True)
        b.Save(SRC)
b.Save(SRC)
json.dump(results, open('.issue268-runtime/step3b-bridge2.json', 'w'), indent=1)
print('saved; bridges2:', len(results))
