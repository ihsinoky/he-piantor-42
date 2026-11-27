"""Gate 5: HALL_3V3 rail re-verification from PLACED copper.

Model (single net, so generous merging only ever under-estimates R):
- track segments split at every projected junction (other endpoints, via
  centres, pad centres landing on the segment's copper);
- terminals (segment ends, via centres, pad centres) on the same layer
  within 0.65mm are one electrical cluster (copper shapes overlap there);
- segment resistance R = rho*L/(w*t), rho_Cu 35um = 0.491 mOhm/sq;
- vias 1 mOhm between their F and B clusters;
- the F.Cu zone pour is an ideal conductor unioning every F terminal
  inside its filled outline.
Per-sensor burst current injected at each TMAG VCC pad, extracted at
J_WING pin 1. Upstream chain (TPS22919 + Main + FH12 + FFC) = 0.417 Ohm
(Stage-1 study). Study far-VCC: 3.276 V typ / 3.253 V max.
Usage: s2_gate5.py <variant>
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, '/home/hatch/workspace/projects/he-piantor-wwing/.issue299-runtime')
import s2_env
s2_env.apply_env()
import numpy as np  # noqa: E402
import pcbnew  # noqa: E402

MM = 1e6
VAR = sys.argv[1]
NET = 'HALL_3V3'
RHO_SQ = 0.491e-3
board = pcbnew.LoadBoard(sys.argv[2])

segs = []        # (x1, y1, x2, y2, layer, w)
vias = []        # (x, y)
pads = []        # (ref, num, x, y, layer)
for t in board.GetTracks():
    if t.GetNetname() != NET:
        continue
    if isinstance(t, pcbnew.PCB_VIA):
        p = t.GetPosition()
        vias.append((p.x / MM, p.y / MM))
    else:
        s, e = t.GetStart(), t.GetEnd()
        lay = 'F' if t.GetLayer() == pcbnew.F_Cu else 'B'
        segs.append((s.x / MM, s.y / MM, e.x / MM, e.y / MM, lay, t.GetWidth() / MM))
for fp in board.GetFootprints():
    for pad in fp.Pads():
        if pad.GetNetname() != NET:
            continue
        p = pad.GetPosition()
        lay = 'F' if pad.IsOnLayer(pcbnew.F_Cu) else 'B'
        pads.append((fp.GetReference(), pad.GetNumber(), p.x / MM, p.y / MM, lay))

# ---- split segments at projected junctions ---------------------------------
def split(segs, jpoints):
    # jpoints: (x, y, layer, reach) -- split a segment if the point projects
    # onto its interior within (reach + w/2) of the centreline
    out = []
    for (x1, y1, x2, y2, lay, w) in segs:
        L = math.hypot(x2 - x1, y2 - y1)
        if L == 0:
            continue
        cuts = [0.0, 1.0]
        for (px, py, play, reach) in jpoints:
            if play != lay:
                continue
            vx, vy = x2 - x1, y2 - y1
            tp = ((px - x1) * vx + (py - y1) * vy) / (L * L)
            if 0.001 < tp < 0.999:
                qx, qy = x1 + tp * vx, y1 + tp * vy
                if math.hypot(px - qx, py - qy) <= reach + w / 2 + 0.02:
                    cuts.append(tp)
        cuts = sorted(set(round(c, 6) for c in cuts))
        for a, b in zip(cuts, cuts[1:]):
            out.append((x1 + a * (x2 - x1), y1 + a * (y2 - y1),
                        x1 + b * (x2 - x1), y1 + b * (y2 - y1), lay, w))
    return out

jpoints = []
for (x1, y1, x2, y2, lay, w) in segs:
    jpoints.append((x1, y1, lay, w / 2))
    jpoints.append((x2, y2, lay, w / 2))
for (x, y) in vias:
    jpoints.append((x, y, 'F', 0.30))
    jpoints.append((x, y, 'B', 0.30))
for (ref, num, x, y, lay) in pads:
    jpoints.append((x, y, lay, 0.30))
segs = split(segs, jpoints)

# ---- terminals + clustering --------------------------------------------------
terms = []  # (x, y, layer)
def term(x, y, lay):
    terms.append((round(x, 4), round(y, 4), lay))
    return len(terms) - 1

seg_terms = []
for (x1, y1, x2, y2, lay, w) in segs:
    a = term(x1, y1, lay)
    b = term(x2, y2, lay)
    seg_terms.append((a, b, RHO_SQ * math.hypot(x2 - x1, y2 - y1) / w if w else 0.0))
via_terms = [(term(x, y, 'F'), term(x, y, 'B')) for (x, y) in vias]
pad_term = {}
for (ref, num, x, y, lay) in pads:
    pad_term[(ref, num)] = term(x, y, lay)

parent = list(range(len(terms)))
def find(a):
    while parent[a] != a:
        parent[a] = parent[parent[a]]
        a = parent[a]
    return a
def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb

# same-layer terminals within 0.65mm merge (copper overlap), via spatial hash
from collections import defaultdict
grid = defaultdict(list)
for i, (x, y, lay) in enumerate(terms):
    grid[(lay, int(x / 0.65), int(y / 0.65))].append(i)
for i, (x, y, lay) in enumerate(terms):
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for j in grid.get((lay, int(x / 0.65) + dx, int(y / 0.65) + dy), []):
                if j > i and math.hypot(terms[j][0] - x, terms[j][1] - y) <= 0.65:
                    union(i, j)
for a, b in via_terms:
    union(a, b)  # via barrel joins its own F/B terminals through 1 mOhm below

clusters = {}
def cid(i):
    r = find(i)
    if r not in clusters:
        clusters[r] = len(clusters)
    return clusters[r]

edges = []
for a, b, r in seg_terms:
    ca, cb = cid(a), cid(b)
    if ca != cb and r > 0:
        edges.append((ca, cb, r))
for a, b in via_terms:
    ca, cb = cid(a), cid(b)
    if ca != cb:
        edges.append((ca, cb, 1e-3))

# F.Cu pour unions every F terminal inside the filled outline
zone = None
for z in board.Zones():
    if z.GetNetname() == NET and z.GetLayer() == pcbnew.F_Cu:
        zone = z
        break
if zone is not None:
    filled = zone.GetFilledPolysList(pcbnew.F_Cu)
    outlines = []
    for oi in range(filled.OutlineCount()):
        ol = filled.Outline(oi)
        pts = [(ol.CPoint(k).x / MM, ol.CPoint(k).y / MM) for k in range(ol.PointCount())]
        xs = [q[0] for q in pts]
        ys = [q[1] for q in pts]
        outlines.append((pts, (min(xs), max(xs), min(ys), max(ys))))
    def inside(x, y):
        for pts, (x0, x1, y0, y1) in outlines:
            if not (x0 - 0.01 <= x <= x1 + 0.01 and y0 - 0.01 <= y <= y1 + 0.01):
                continue
            c = False
            n = len(pts)
            for i in range(n):
                ax, ay = pts[i]
                bx, by = pts[(i + 1) % n]
                if (ay > y) != (by > y) and x < (bx - ax) * (y - ay) / (by - ay) + ax:
                    c = not c
            if c:
                return True
        return False
    f_terms = [i for i, t in enumerate(terms) if t[2] == 'F' and inside(t[0], t[1])]
    if f_terms:
        base = cid(f_terms[0])
        for i in f_terms[1:]:
            ci = cid(i)
            if ci != base:
                edges.append((base, ci, 1e-4))

src = cid(pad_term[('J_WING', '1')])
sensor_c = {}
for (ref, num), ti in pad_term.items():
    if ref.startswith('U_H') and num == '1':
        sensor_c[ref] = cid(ti)
assert len(sensor_c) == 21, f'sensors: {len(sensor_c)}'

N = len(clusters)
G = np.zeros((N, N))
for a, b, r in edges:
    g = 1.0 / r
    G[a, a] += g
    G[b, b] += g
    G[a, b] -= g
    G[b, a] -= g
keep = [i for i in range(N) if i != src]
pos = {idx: j for j, idx in enumerate(keep)}
Gk = G[np.ix_(keep, keep)]

out = {'gate': 5, 'variant': VAR, 'clusters': N, 'edges': len(edges)}
UPSTREAM_R = 0.417
for label, i_tot_ma, study_far in (('typ', 54.9, 3.276), ('max', 105.3, 3.253)):
    i_s = (i_tot_ma / 21.0) / 1000.0
    I = np.zeros(len(keep))
    for ref, c in sensor_c.items():
        I[pos[c]] += i_s
    V = np.linalg.solve(Gk, I)
    drops = {ref: float(V[pos[c]]) * 1000.0 for ref, c in sensor_c.items()}
    far_ref = max(drops, key=drops.get)
    wing_drop = drops[far_ref]
    up_drop = i_tot_ma * UPSTREAM_R  # mA * Ohm = mV
    far_vcc = 3.300 - (up_drop + wing_drop) / 1000.0
    out[label] = {'wing_drop_mV': round(wing_drop, 3), 'far_sensor': far_ref,
                  'upstream_drop_mV': round(up_drop, 2),
                  'far_VCC_V': round(far_vcc, 4),
                  'study_far_VCC_V': study_far,
                  'delta_mV': round((far_vcc - study_far) * 1000.0, 2)}
print(json.dumps(out))
