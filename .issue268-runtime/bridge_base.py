"""Issue #268 build step 2: reconnect FH12 pads to surviving link-net copper.
Component analysis (geometric, layer-aware) -> orphan cleanup -> grid A* per net.
Ledger -> .issue268-runtime/step3-bridge.json. Board saved in place."""
import heapq, json, math, sys
import numpy as np
import pcbnew as p

SRC = 'hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb'
LINK = ['HALL_5V','GND','MUX_A0','MUX_A1','MUX_A2','WING_EN','MUX_OUT_A','MUX_OUT_B','MUX_OUT_C']
POWER = {'HALL_5V', 'GND'}
CLR = 0.10
STEP = 0.05
WIN = (76.0, 128.0, 96.0, 138.0)  # xmin xmax ymin ymax
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
PAD_COL = {  # FH12 pad centre x per net (GND has six)
    'HALL_5V': [103.25], 'GND': [102.75, 101.75, 99.75, 98.75, 97.75, 96.75],
    'MUX_A0': [102.25], 'MUX_A1': [101.25], 'MUX_A2': [100.75], 'WING_EN': [100.25],
    'MUX_OUT_A': [99.25], 'MUX_OUT_B': [98.25], 'MUX_OUT_C': [97.25]}
PAD_W = {'HALL_5V': 0.3, 'GND': 0.3}
def raster_blocked(exclude_net, width, via=False, reserve=True):
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
    # reserved escape columns near the pads (y 129.5..132.7) - tracks only;
    # vias are governed by item geometry (0.4 from surfaces), since a 0.6 via's
    # x-band reservation would exceed the 0.5 pad pitch and ban own-column vias.
    # North of 129.5 the escapes have fanned out; horizontal travel is allowed
    # there (subject to copper), which the east/west-target nets require.
    if not via and reserve:
        iy0 = max(0, int((129.5-WIN[2])/STEP)); iy1 = min(NY-1, int((132.7-WIN[2])/STEP)+1)
        for net, cols in PAD_COL.items():
            if net == exclude_net: continue
            half = PAD_W.get(net, 0.1)/2 + CLR + width/2
            for cx in cols:
                ix0 = max(0, int((cx-half-WIN[0])/STEP)); ix1 = min(NX-1, int((cx+half-WIN[0])/STEP)+1)
                blocked[0][iy0:iy1+1, ix0:ix1+1] = True
                blocked[1][iy0:iy1+1, ix0:ix1+1] = True
        # pad moats: no other-net tracks within +-0.42 of a J_WING pad centre at
        # y>=130.4 (prevents a routed net wrapping a neighbour pad and poisoning
        # its in-column via spots / lane); 0.42 leaves each 0.5-pitch lane centre
        # free between the flanking moats
        my0 = max(0, int((130.4-WIN[2])/STEP))
        for net, cols in PAD_COL.items():
            if net == exclude_net: continue
            for cx in cols:
                ix0 = max(0, int((cx-0.42-WIN[0])/STEP)); ix1 = min(NX-1, int((cx+0.42-WIN[0])/STEP)+1)
                blocked[0][my0:NY, ix0:ix1+1] = True
                blocked[1][my0:NY, ix0:ix1+1] = True
    # FH12 housing keepout: no B.Cu copper, no vias under the body
    hx0 = max(0, int((93.8-WIN[0])/STEP)); hx1 = min(NX-1, int((106.2-WIN[0])/STEP)+1)
    hy0 = max(0, int((132.7-WIN[2])/STEP)); hy1 = min(NY-1, int((137.4-WIN[2])/STEP)+1)
    blocked[1][hy0:hy1+1, hx0:hx1+1] = True
    if via:
        blocked[0][hy0:hy1+1, hx0:hx1+1] = True
    # no routing south of the pad row on either layer (FFC exit side discipline)
    sy0 = max(0, int((132.6-WIN[2])/STEP))
    blocked[0][sy0:NY, :] = True; blocked[1][sy0:NY, :] = True
    if via:
        # no new vias in the pad-adjacent band: a 0.6 via 0.5mm from a GND pad
        # leaves <0.5mm for the pad's own 0.3 escape track (via sandwich)
        vx0 = max(0, int((93.0-WIN[0])/STEP)); vx1 = min(NX-1, int((107.0-WIN[0])/STEP)+1)
        vy0 = max(0, int((130.9-WIN[2])/STEP)); vy1 = min(NY-1, int((132.7-WIN[2])/STEP)+1)
        blocked[0][vy0:vy1+1, vx0:vx1+1] = True; blocked[1][vy0:vy1+1, vx0:vx1+1] = True
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
# NOTE(continuation): orphan deletion removed - DRC-verified state is kept intact.

# ---------- A* ----------

