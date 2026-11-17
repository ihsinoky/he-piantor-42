"""Issue #268 build step 2: reconnect FH12 pads to surviving link-net copper.
Component analysis (geometric, layer-aware) -> orphan cleanup -> grid A* per net.
Ledger -> .issue268-runtime/step2.json. Board saved in place."""
import heapq, json, math, sys
import numpy as np
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
LINK = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
POWER = {'HALL_5V', 'GND'}
CLR = 0.10
STEP = 0.05
WIN = (76.0, 122.0, 96.0, 138.0)  # xmin xmax ymin ymax
NX = int((WIN[1]-WIN[0])/STEP) + 1
NY = int((WIN[3]-WIN[2])/STEP) + 1
mm = lambda v: v/1e6

b = p.LoadBoard(SRC)

# ---------- geometry items ----------
class Item:
    __slots__ = ('net', 'layers', 'kind', 'obj', 'cx', 'cy', 'r', 'hw', 'hh', 'rot', 'x1', 'y1', 'x2', 'y2')
items = []
def add_track(t):
    it = Item(); it.net = t.GetNetname(); it.obj = t
    s, e = t.GetStart(), t.GetEnd()
    it.x1, it.y1, it.x2, it.y2 = mm(s.x), mm(s.y), mm(e.x), mm(e.y)
    if isinstance(t, p.PCB_VIA):
        it.kind = 'via'; it.layers = {0, 2}; it.r = mm(t.GetWidth(p.F_Cu))/2
        it.cx, it.cy = it.x1, it.y1
    else:
        it.kind = 'seg'; it.layers = {int(t.GetLayer())}; it.r = mm(t.GetWidth())/2
    items.append(it)
def add_pad(fp, pad):
    if pad.GetAttribute() == p.PAD_ATTRIB_NPTH:
        return
    it = Item(); it.net = pad.GetNetname(); it.obj = pad; it.kind = 'pad'
    it.layers = set()
    if pad.IsOnLayer(p.F_Cu): it.layers.add(0)
    if pad.IsOnLayer(p.B_Cu): it.layers.add(2)
    if not it.layers: return
    c = pad.GetPosition(); it.cx, it.cy = mm(c.x), mm(c.y)
    sz = pad.GetSize(); it.hw, it.hh = mm(sz.x)/2, mm(sz.y)/2
    it.rot = pad.GetOrientationDegrees()
    items.append(it)
for t in b.GetTracks(): add_track(t)
for fp in b.GetFootprints():
    for pad in fp.Pads(): add_pad(fp, pad)

def dist_to_item(it, X, Y):
    """Distance from points (X,Y arrays) to item geometry (0 inside pads)."""
    if it.kind == 'seg':
        vx, vy = it.x2-it.x1, it.y2-it.y1
        L2 = vx*vx + vy*vy
        if L2 == 0: d = np.hypot(X-it.x1, Y-it.y1)
        else:
            t = np.clip(((X-it.x1)*vx + (Y-it.y1)*vy)/L2, 0, 1)
            d = np.hypot(X-(it.x1+t*vx), Y-(it.y1+t*vy))
        return d - it.r
    if it.kind == 'via':
        return np.hypot(X-it.cx, Y-it.cy) - it.r
    # pad: rotated rect
    th = math.radians(-it.rot)
    dx, dy = X-it.cx, Y-it.cy
    lx = dx*math.cos(th) - dy*math.sin(th)
    ly = dx*math.sin(th) + dy*math.cos(th)
    qx = np.abs(lx) - it.hw; qy = np.abs(ly) - it.hh
    ox, oy = np.maximum(qx, 0), np.maximum(qy, 0)
    return np.hypot(ox, oy) + np.minimum(np.maximum(qx, qy), 0)

def bbox_of(it, pad):
    if it.kind == 'seg':
        return (min(it.x1, it.x2)-pad, max(it.x1, it.x2)+pad, min(it.y1, it.y2)-pad, max(it.y1, it.y2)+pad)
    r = (max(it.hw, it.hh) if it.kind == 'pad' else it.r) + pad
    return (it.cx-r, it.cx+r, it.cy-r, it.cy+r)

GX, GY = np.meshgrid(WIN[0] + STEP*np.arange(NX), WIN[2] + STEP*np.arange(NY))
def raster_blocked(exclude_net, width, via=False):
    """blocked[2][NY][NX] bool: cell centre too close to other-net copper."""
    need = (0.3 if via else width/2) + CLR
    blocked = [np.zeros((NY, NX), bool), np.zeros((NY, NX), bool)]
    for it in items:
        if it.net == exclude_net: continue
        x0, x1, y0, y1 = bbox_of(it, need + 0.75)
        ix0 = max(0, int((x0-WIN[0])/STEP)); ix1 = min(NX-1, int((x1-WIN[0])/STEP)+1)
        iy0 = max(0, int((y0-WIN[2])/STEP)); iy1 = min(NY-1, int((y1-WIN[2])/STEP)+1)
        if ix0 > ix1 or iy0 > iy1: continue
        sub_x = GX[iy0:iy1+1, ix0:ix1+1]; sub_y = GY[iy0:iy1+1, ix0:ix1+1]
        d = dist_to_item(it, sub_x, sub_y)
        mask = d < need
        for li, layer in enumerate((0, 2)):
            if layer in it.layers:
                blocked[li][iy0:iy1+1, ix0:ix1+1] |= mask
    return blocked

def goal_mask(comp_items, width):
    g = [np.zeros((NY, NX), bool), np.zeros((NY, NX), bool)]
    for it in comp_items:
        x0, x1, y0, y1 = bbox_of(it, width/2 + 0.1)
        ix0 = max(0, int((x0-WIN[0])/STEP)); ix1 = min(NX-1, int((x1-WIN[0])/STEP)+1)
        iy0 = max(0, int((y0-WIN[2])/STEP)); iy1 = min(NY-1, int((y1-WIN[2])/STEP)+1)
        if ix0 > ix1 or iy0 > iy1: continue
        d = dist_to_item(it, GX[iy0:iy1+1, ix0:ix1+1], GY[iy0:iy1+1, ix0:ix1+1])
        for li, layer in enumerate((0, 2)):
            if layer in it.layers:
                g[li][iy0:iy1+1, ix0:ix1+1] |= d <= width/2 + 0.02
    return g

# ---------- components per net ----------
def components(net):
    rows = [it for it in items if it.net == net]
    par = list(range(len(rows)))
    def find(i):
        while par[i] != i: par[i] = par[par[i]]; i = par[i]
        return i
    def centre(it):
        return ((it.x1+it.x2)/2, (it.y1+it.y2)/2) if it.kind == 'seg' else (it.cx, it.cy)
    def reach(it):
        if it.kind == 'seg': return math.hypot(it.x2-it.x1, it.y2-it.y1)/2 + it.r
        if it.kind == 'via': return it.r
        return math.hypot(it.hw, it.hh)
    for i, a in enumerate(rows):
        ca = centre(a)
        for j in range(i+1, len(rows)):
            c = rows[j]
            if not (a.layers & c.layers): continue
            cc = centre(c)
            if math.hypot(ca[0]-cc[0], ca[1]-cc[1]) > reach(a) + reach(c) + 0.02: continue
            pts_a = [(a.x1, a.y1), (a.x2, a.y2)] if a.kind == 'seg' else [(a.cx, a.cy)]
            pts_c = [(c.x1, c.y1), (c.x2, c.y2)] if c.kind == 'seg' else [(c.cx, c.cy)]
            ra = a.r if a.kind != 'pad' else 0.0
            rc = c.r if c.kind != 'pad' else 0.0
            touch = False
            for q in pts_a:
                if dist_to_item(c, np.array([q[0]]), np.array([q[1]]))[0] - rc <= 0.03: touch = True
            for q in pts_c:
                if dist_to_item(a, np.array([q[0]]), np.array([q[1]]))[0] - ra <= 0.03: touch = True
            if touch:
                par[find(i)] = find(j)
    groups = {}
    for i, r in enumerate(rows): groups.setdefault(find(i), []).append(r)
    return list(groups.values())

ledger = {'orphans_deleted': [], 'routes': []}
# J_WING pad centres (measured after placement): pads at y=132.0, x = 103.25 - 0.5*(k-1)
JW_CENTRES = {(round(103.25 - 0.5*k, 4), 132.0) for k in range(14)}
def is_jw_pad(it):
    return it.kind == 'pad' and (round(it.cx, 4), round(it.cy, 4)) in JW_CENTRES
for net in LINK:
    for comp in components(net):
        if any(it.kind == 'pad' for it in comp): continue
        for it in comp:
            if it.obj is not None and not isinstance(it.obj, p.PAD):
                ledger['orphans_deleted'].append(it.obj.m_Uuid.AsString())
                b.RemoveNative(it.obj)
                items.remove(it)
print('orphans deleted:', len(ledger['orphans_deleted']), flush=True)

# ---------- A* ----------
def astar(blocked, viablocked, goal, start, hints):
    sx, sy, sl = start
    openh = [(0.0, sx, sy, sl)]
    came = {}
    gs = {(sx, sy, sl): 0.0}
    def hfun(x, y):
        gx, gy = WIN[0]+STEP*x, WIN[2]+STEP*y
        return 0.9*min(math.hypot(gx-hx, gy-hy) for hx, hy in hints)
    def is_goal(x, y, l): return goal[l][y, x]
    while openh:
        f, x, y, l = heapq.heappop(openh)
        if is_goal(x, y, l) and (x, y, l) != (sx, sy, sl):
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

def cell_of(x, y): return (int(round((x-WIN[0])/STEP)), int(round((y-WIN[2])/STEP)))
def xy_of(cx, cy): return (WIN[0]+STEP*cx, WIN[2]+STEP*cy)

for net in ('HALL_5V', 'GND'):
    comps = components(net)
    print(net, 'comps:', len(comps))
    for c in comps:
        pads = sorted({f"{it.obj.GetParentFootprint().GetReference()}.{it.obj.GetNumber()}" for it in c if it.kind == 'pad'})
        xs = [it.cx if it.kind != 'seg' else (it.x1+it.x2)/2 for it in c]
        ys = [it.cy if it.kind != 'seg' else (it.y1+it.y2)/2 for it in c]
        print('  size', len(c), 'pads', len(pads), pads[:4], 'x', round(min(xs),1), round(max(xs),1), 'y', round(min(ys),1), round(max(ys),1), 'jw' , any(is_jw_pad(it) for it in c))
