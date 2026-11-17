"""Issue #268 reference extraction: track-graph Dijkstra for HALL_5V / GND
from J_WING to each U_MUX VDD/GND pad. Sheet R = rho/t = 0.4926 mOhm/sq (1 oz).
Vias modelled as 0 ohm layer shorts. REFERENCE ONLY (bench board)."""
import heapq, math, json
import pcbnew as p

mm = lambda v: v / 1e6
SQ = 0.4926  # mOhm per square
b = p.LoadBoard('hardware/kicad/qualification/issue-268-matrix-rev4/board/m1-matrix18.kicad_pcb')

def build(net):
    segs, vias = [], []
    for t in b.GetTracks():
        if t.GetNetname() != net:
            continue
        s, e = t.GetStart(), t.GetEnd()
        if isinstance(t, p.PCB_VIA):
            vias.append((mm(s.x), mm(s.y)))
        else:
            segs.append((mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()),
                         'F' if t.GetLayerName() == 'F.Cu' else 'B'))
    # nodes: endpoints + T-junction splits
    pts = set()
    for x1, y1, x2, y2, w, L in segs:
        pts.add((round(x1, 2), round(y1, 2), L)); pts.add((round(x2, 2), round(y2, 2), L))
    for (x, y) in vias:
        pts.add((round(x, 2), round(y, 2), 'F')); pts.add((round(x, 2), round(y, 2), 'B'))
    def on_seg(px, py, x1, y1, x2, y2):
        dx, dy = x2 - x1, y2 - y1
        ll = dx * dx + dy * dy
        if ll == 0: return False
        u = ((px - x1) * dx + (py - y1) * dy) / ll
        if u <= 0.02 or u >= 0.98: return False
        cx, cy = x1 + u * dx, y1 + u * dy
        return math.hypot(px - cx, py - cy) < 0.17
    splits = {i: [] for i in range(len(segs))}
    for i, (x1, y1, x2, y2, w, L) in enumerate(segs):
        for (px, py, Lp) in pts:
            if Lp == L and on_seg(px, py, x1, y1, x2, y2):
                splits[i].append((px, py))
    adj = {}
    def link(a, c, r):
        adj.setdefault(a, []).append((c, r)); adj.setdefault(c, []).append((a, r))
    for i, (x1, y1, x2, y2, w, L) in enumerate(segs):
        chain = [(x1, y1)] + sorted(splits[i], key=lambda q: (q[0] - x1) ** 2 + (q[1] - y1) ** 2) + [(x2, y2)]
        for (ax, ay), (cx, cy) in zip(chain, chain[1:]):
            r = math.hypot(cx - ax, cy - ay) / w * SQ
            link((round(ax, 2), round(ay, 2), L), (round(cx, 2), round(cy, 2), L), r)
    for (x, y) in vias:
        link((round(x, 2), round(y, 2), 'F'), (round(x, 2), round(y, 2), 'B'), 0.0)
    # copper-overlap joints: same-layer nodes whose centrelines pass within
    # 0.28mm are copper-merged for these 0.30/0.15-wide nets even when the
    # centrelines do not exactly intersect (corner stacks, grazes).
    # pads are copper: link each pad centre of this net to graph nodes
    # within the pad half-diagonal + 0.1 on a layer the pad touches.
    for fp in b.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() != net: continue
            pos, sz = pad.GetPosition(), pad.GetSize()
            cx, cy = round(mm(pos.x), 2), round(mm(pos.y), 2)
            reach = math.hypot(mm(sz.x), mm(sz.y)) / 2 + 0.1
            layers = (['F'] if pad.IsOnLayer(p.F_Cu) else []) + (['B'] if pad.IsOnLayer(p.B_Cu) else [])
            for L in layers:
                pn = (cx, cy, L)
                for n in list(adj.keys()):
                    if n[2] == L and math.hypot(n[0] - cx, n[1] - cy) <= reach:
                        link(pn, n, 0.0)
    nodes = list(adj.keys())
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            a, c = nodes[i], nodes[j]
            if a[2] == c[2] and math.hypot(a[0] - c[0], a[1] - c[1]) < 0.45:
                link(a, c, 0.0)
    return adj

def dijkstra(adj, sources):
    dist = {s: 0.0 for s in sources}
    pq = [(0.0, s) for s in sources]
    heapq.heapify(pq)
    while pq:
        d, u = heapq.heappop(pq)
        if d > dist.get(u, 1e18): continue
        for v, r in adj.get(u, []):
            nd = d + r
            if nd < dist.get(v, 1e18):
                dist[v] = nd; heapq.heappush(pq, (nd, v))
    return dist

def attach(adj, node):
    if node in adj: return node
    best, bd = None, 1.0
    for n in adj:
        if n[2] != node[2]: continue
        d = math.hypot(n[0]-node[0], n[1]-node[1])
        if d < bd: bd, best = d, n
    return best

def pad_node(ref, num):
    for fp in b.GetFootprints():
        if fp.GetReference() != ref: continue
        for pad in fp.Pads():
            if pad.GetNumber() == str(num):
                pos = pad.GetPosition()
                return (round(mm(pos.x), 2), round(mm(pos.y), 2), 'B' if pad.IsOnLayer(p.B_Cu) and not pad.IsOnLayer(p.F_Cu) else 'F')
    return None

res = {}
for net, src_pads, tgt_pad in (('HALL_5V', [1], 13), ('GND', [2, 4, 8, 10, 12, 14], 14)):
    adj = build(net)
    srcs = [attach(adj, pad_node('J_WING', n)) for n in src_pads]
    dist = dijkstra(adj, srcs)
    res[net] = {}
    for mux in ('U_MUX_A', 'U_MUX_B', 'U_MUX_C'):
        t = attach(adj, pad_node(mux, tgt_pad))
        res[net][mux] = round(dist.get(t, float('nan')), 2)
    print(net, res[net])
print('loop (HALL+GND) mOhm and drop @127mA reference:')
for mux in ('U_MUX_A', 'U_MUX_B', 'U_MUX_C'):
    loop = res['HALL_5V'][mux] + res['GND'][mux]
    print(' ', mux, round(loop, 2), 'mOhm ->', round(loop * 0.127, 2), 'mV')
json.dump(res, open('.issue268-runtime/extraction268.json', 'w'), indent=1)
