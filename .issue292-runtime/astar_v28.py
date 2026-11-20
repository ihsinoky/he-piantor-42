"""Grid A* router for the last nets (MUX_A0/A1/A2 stubs + A1 trunk).
Obstacles from current board geometry (geom_v28.json, dumped from
wmain-v10-routed3). Grid 0.2mm, layers F/I2/B, vias as layer changes.
Output: routes_v28.json (polylines per layer + via points)."""
import json, math, heapq
from shapely.geometry import box, Polygon, LineString
from shapely.strtree import STRtree
from pathlib import Path
E = Path('.').resolve()
G = json.loads((E/'geom_v28.json').read_text())
LAYERS = ['F', 'I2', 'B']
STEP = 0.2
INF = 0.10 + 0.05  # clearance + half track width

def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    pts = []
    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)):
        pts.append((cx + dx * c - dy * s, cy + dx * s + dy * c))
    return Polygon(pts)

# obstacle shapes per layer (other nets added per-run)
base_shapes = {L: [] for L in LAYERS}
via_shapes = []  # block all layers
for p in G['pads']:
    poly = rect_poly(p['x'], p['y'], p['sx'], p['sy'], p['rot']).buffer(INF)
    base_shapes['F'].append((p['net'], poly))
    if p['pth']:
        for L in LAYERS[1:]:
            base_shapes[L].append((p['net'], poly))
for t in G['tracks']:
    ls = LineString([(t['x1'], t['y1']), (t['x2'], t['y2'])]).buffer(t['w'] / 2 + 0.1)
    base_shapes[t['layer']].append((t['net'], ls))
for v in G['vias']:
    from shapely.geometry import Point
    c = Point(v['x'], v['y']).buffer(v['d'] / 2 + 0.1)
    for L in LAYERS:
        base_shapes[L].append((v['net'], c))
# rule areas: antenna strip blocks all layers; trackpad blocks F (tracks)
from shapely.geometry import Polygon as SP
ant = SP([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
for L in LAYERS:
    base_shapes[L].append(('__KEEP__', ant))
from shapely.geometry import Point as _Pt
circ = _Pt(100, 118).buffer(20.0)
for L in LAYERS:
    base_shapes[L].append(('__KEEP__', circ))
outline = SP([(64.1073, 134.4359), (66.1073, 137.9), (133.8927, 137.9), (135.8927, 134.4359), (128.9362, 122.3869), (132.9488, 115.4381), (119.8213, 103.1964), (117.8562, 103.1958), (102.0, 75.7321), (98.0, 75.7321), (82.1438, 103.1958), (80.1787, 103.1964), (67.0512, 115.4381), (71.0638, 122.3869)])

def build_index(net):
    idx = {}
    for L in LAYERS:
        shapes = [s for n, s in base_shapes[L] if n != net]
        idx[L] = (STRtree(shapes), shapes)
    return idx

def blocked(idx, L, x, y, r=0.05):
    from shapely.geometry import Point
    pt = Point(x, y).buffer(r)
    tree, shapes = idx[L]
    for i in tree.query(pt):
        if shapes[i].intersects(pt):
            return True
    return False

def astar(idx, net_shapes_self, start, goal, region):
    """start/goal: (layer, x, y). region: (x0, x1, y0, y1). Returns path list of (layer, x, y)."""
    x0, x1, y0, y1 = region
    def key(L, ix, iy): return (L, ix, iy)
    sx, sy = round((start[1] - x0) / STEP), round((start[2] - y0) / STEP)
    gx, gy = round((goal[1] - x0) / STEP), round((goal[2] - y0) / STEP)
    startk = (start[0], sx, sy); goalk = (goal[0], gx, gy)
    openh = [(0, startk)]
    came = {startk: None}
    cost = {startk: 0.0}
    def h(k):
        return math.hypot(k[1] - gx, k[2] - gy) * STEP + (0 if k[0] == goal[0] else 1.5)
    def pt_of(k):
        return (x0 + k[1] * STEP, y0 + k[2] * STEP)
    selftree = net_shapes_self  # (layer -> (tree, shapes)) of own net copper: goal zone
    while openh:
        _, cur = heapq.heappop(openh)
        if cur == goalk or (cur[0] == goal[0] and cur[1] == gx and cur[2] == gy):
            path = []
            while cur:
                path.append((cur[0], *pt_of(cur)))
                cur = came[cur]
            return path[::-1]
        cx, cy = pt_of(cur)
        nbrs = []
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)):
            nk = (cur[0], cur[1] + dx, cur[2] + dy)
            nx, ny = pt_of(nk)
            if not (x0 - 0.01 <= nx <= x1 + 0.01 and y0 - 0.01 <= ny <= y1 + 0.01):
                continue
            if not outline.contains(Point(nx, ny)):
                continue
            step_cost = STEP * (1.414 if dx and dy else 1.0)
            if nk != goalk and math.hypot(nx - (x0 + gx * STEP), ny - (y0 + gy * STEP)) > 0.31 and blocked(idx, cur[0], nx, ny):
                continue
            nbrs.append((nk, step_cost))
        for L2 in LAYERS:
            if L2 != cur[0]:
                nk = (L2, cur[1], cur[2])
                if not blocked(idx, L2, cx, cy, r=0.3) and not blocked(idx, cur[0], cx, cy, r=0.3):
                    nbrs.append((nk, 2.0))  # via cost
        for nk, sc in nbrs:
            nc = cost[cur] + sc
            if nc < cost.get(nk, 1e18):
                cost[nk] = nc
                came[nk] = cur
                heapq.heappush(openh, (nc + h(nk), nk))
    return None

def self_shapes(net):
    idx = {}
    for L in LAYERS:
        shapes = [s for n, s in base_shapes[L] if n == net]
        idx[L] = (STRtree(shapes), shapes)
    return idx

def route_net(net, jobs):
    """jobs: list of (start(l,x,y), goal(l,x,y), region). Copper grows per job."""
    idx = build_index(net)
    out = []
    grown = []  # (layer, LineString) added copper
    for (s, g, region) in jobs:
        # goal may be 'tree': find nearest own-net point first (handled by caller coords)
        path = astar(idx, None, s, g, region)
        if not path:
            print(net, 'FAILED', s, '->', g)
            return None
        out.append(path)
        # add path as obstacle-free own copper for later jobs: register segments
        for i in range(len(path) - 1):
            L1, xa, ya = path[i]; L2, xb, yb = path[i + 1]
            if L1 == L2:
                ls = LineString([(xa, ya), (xb, yb)]).buffer(0.05 + 0.1)
                base_shapes[L1].append((net, ls))
        idx = build_index(net)
        print(net, 'routed leg', len(path), 'pts')
    return out

result = {}
# A0: J3.12 pad (F) to nearest A0 copper: via near (from DRC) - use goal = J3 area A0 via;
# caller supplies coordinates found in the analysis step (jobs_v28.json)
jobs = json.loads((E/'jobs_v28.json').read_text())
for net, jl in jobs.items():
    r = route_net(net, [((j['s'][0], j['s'][1], j['s'][2]), (j['g'][0], j['g'][1], j['g'][2]), tuple(j['region'])) for j in jl])
    if r:
        result[net] = r
(E/'routes_v28.json').write_text(json.dumps(result))
print('done', list(result))
