"""S3a2: GND taps for the 10 U1 GND pads -> In1 plane.
Grid A* (0.05) on F.Cu per pad, hardest first (7, 14, 18 = the
layout round's failures). Target: a via-legal cell (0.6/0.3 via,
clearance tried at 0.10 then 0.05) or existing GND copper.
Tap track width 0.2. Output: gnd_taps.json {pad: {path, via|None,
via_clearance}}; geometry only - apply step is separate."""
import pcbnew as p, math, json, heapq
from shapely.geometry import Point, LineString, Polygon
from shapely.strtree import STRtree
from pathlib import Path
E = Path('.').resolve()
TREE = E.parent/'hardware/kicad/qualification/issue-292-wmain'
b = p.LoadBoard(str(TREE/'wmain.kicad_pcb'))
STEP = 0.05
X0, X1, Y0, Y1 = 68.0, 82.0, 117.5, 130.0
ANT = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
CIRC = Point(100, 118).buffer(20.0)
LAYN = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}

def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])

raw = {L: [] for L in ('F', 'I1', 'I2', 'B')}   # (net, shape) foreign-geometry source
gnd_items = []                                 # (id, shape) GND copper on F = tap targets
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y),
                         pad.GetOrientationDegrees())
        n = pad.GetNetname()
        if pad.IsOnLayer(p.F_Cu):
            raw['F'].append((n, poly))
            # U1's own GND pads are NOT tap targets: they are the
            # ungrounded items themselves (fake short targets broke
            # the closure). Targets = plane-connected copper only.
            if n == 'GND' and str(f.GetReference()) != 'U1':
                gnd_items.append((f'{f.GetReference()}.{pad.GetNumber()}', poly))
        if pad.GetAttribute() == p.PAD_ATTRIB_PTH:
            for L in ('I1', 'I2', 'B'): raw[L].append((n, poly))
_tid = 0
for t in b.GetTracks():
    if isinstance(t, p.PCB_VIA):
        c = Point(p.ToMM(t.GetPosition().x), p.ToMM(t.GetPosition().y)).buffer(p.ToMM(t.GetWidth(p.F_Cu)) / 2)
        for L in raw: raw[L].append((t.GetNetname(), c))
        if t.GetNetname() == 'GND': gnd_items.append((f'via{_tid}', c)); _tid += 1
    else:
        L = LAYN.get(t.GetLayer())
        if L:
            s, e = t.GetStart(), t.GetEnd()
            ls = LineString([(p.ToMM(s.x), p.ToMM(s.y)), (p.ToMM(e.x), p.ToMM(e.y))]).buffer(p.ToMM(t.GetWidth()) / 2)
            raw[L].append((t.GetNetname(), ls))
            if t.GetNetname() == 'GND' and L == 'F': gnd_items.append((f'trk{_tid}', ls)); _tid += 1
gnd_f = [s for _, s in gnd_items]

def idx_for(layer, inflate, net='GND'):
    shapes = [s.buffer(inflate) for n, s in raw[layer] if n != net]
    if layer == 'F': shapes += [ANT.buffer(inflate), CIRC.buffer(inflate)]
    return STRtree(shapes), shapes
def blocked(idx, x, y, r=0.0):
    pt = Point(x, y).buffer(r) if r else Point(x, y)
    tree, shapes = idx
    return any(shapes[i].intersects(pt) for i in tree.query(pt))

ALL_PADS = []
for f in b.GetFootprints():
    for pad in f.Pads():
        pos, sz = pad.GetPosition(), pad.GetSize()
        ALL_PADS.append(rect_poly(p.ToMM(pos.x), p.ToMM(pos.y), p.ToMM(sz.x), p.ToMM(sz.y),
                                  pad.GetOrientationDegrees()))
PADTREE = STRtree(ALL_PADS)
# Prebuilt via-legality indices (buffering per call was the timeout
# cause): per layer, shapes inflated by 0.10 and by 0.05, built once;
# grow() appends new via shapes and rebuilds that layer's trees.
_via_shapes = {}
def _build_via_idx():
    _via_shapes.clear()
    for clr in (0.10, 0.05):
        for L in ('F', 'I1', 'I2', 'B'):
            shapes = [s.buffer(clr) for n, s in raw[L] if n != 'GND']
            if L == 'F': shapes += [ANT.buffer(clr), CIRC.buffer(clr)]
            _via_shapes[(L, clr)] = (STRtree(shapes), shapes)
_build_via_idx()
def _via_add(shape):
    for clr in (0.10, 0.05):
        for L in ('F', 'I1', 'I2', 'B'):
            st, shapes = _via_shapes[(L, clr)]
            shapes.append(shape.buffer(clr))
            _via_shapes[(L, clr)] = (STRtree(shapes), shapes)
def via_legal(x, y, clr):
    vc = Point(x, y).buffer(0.3)
    # a via must never overlap ANY pad (drill in an SMD pad = defect),
    # including same-net pads
    if any(ALL_PADS[i].intersects(vc) for i in PADTREE.query(vc)): return False
    for L in ('F', 'I1', 'I2', 'B'):
        st, shapes = _via_shapes[(L, clr)]
        if any(shapes[i].intersects(vc) for i in st.query(vc)): return False
    return True

u1 = [f for f in b.GetFootprints() if str(f.GetReference()) == 'U1'][0]
gnd_pads = {}
for pad in u1.Pads():
    if pad.GetNetname() == 'GND':
        gnd_pads[pad.GetNumber()] = (p.ToMM(pad.GetPosition().x), p.ToMM(pad.GetPosition().y))
ORDER = ['7', '14', '21', '18', '16', '24', '1', '25', '31', '23']
W = 0.2
out = {}
grounded_ids = {i for i, _ in gnd_items if not i.startswith('U1.')}
def plan_one(num, grounded_only):
    sx, sy = gnd_pads[num]
    for clr in (0.10, 0.05):
        idx = idx_for('F', clr + W / 2)
        gtree = STRtree(gnd_f)
        src_id = f'U1.{num}'
        hit = {'id': None}
        def is_target(x, y, dist):
            if via_legal(x, y, 0.10): return 'via10'
            if via_legal(x, y, 0.05): return 'via05'
            if dist >= 0.25:
                pt = Point(x, y).buffer(W / 2)
                for i in gtree.query(pt):
                    iid = gnd_items[i][0]
                    if iid == src_id: continue
                    if grounded_only and iid not in grounded_ids: continue
                    if gnd_f[i].intersects(pt):
                        hit['id'] = iid; return 'copper'
            return None
        start = (round((sx - X0) / STEP), round((sy - Y0) / STEP))
        openh = [(0.0, 0.0, start)]; came, cost = {}, {start: 0.0}; goal = None; gkind = None
        while openh:
            f_, g, cur = heapq.heappop(openh)
            if g > cost.get(cur, 1e18): continue
            cx, cy = X0 + cur[0] * STEP, Y0 + cur[1] * STEP
            if cur != start:
                gkind = is_target(cx, cy, g)
                if gkind: goal = cur; break
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    if dx == 0 and dy == 0: continue
                    nk = (cur[0] + dx, cur[1] + dy)
                    nx, ny = X0 + nk[0] * STEP, Y0 + nk[1] * STEP
                    if not (X0 <= nx <= X1 and Y0 <= ny <= Y1): continue
                    if blocked(idx, nx, ny): continue
                    ng = g + math.hypot(dx, dy) * STEP
                    if ng < cost.get(nk, 1e18):
                        cost[nk] = ng; came[nk] = cur
                        heapq.heappush(openh, (ng, ng, nk))
        if goal is None: continue
        path = []; cur = goal
        while cur != start:
            path.append((round(X0 + cur[0] * STEP, 2), round(Y0 + cur[1] * STEP, 2)))
            cur = came[cur]
        path.append((round(sx, 2), round(sy, 2))); path.reverse()
        via = list(path[-1]) if gkind in ('via10', 'via05') else None
        entry = {'path': path, 'via': via,
                 'via_clearance': 0.10 if gkind == 'via10' else (0.05 if gkind == 'via05' else None),
                 'target': gkind, 'hit': hit['id'], 'width': W}
        return entry
    return None
def grow(num, entry):
    ids = []
    for i in range(len(entry['path']) - 1):
        ls = LineString([entry['path'][i], entry['path'][i + 1]]).buffer(entry['width'] / 2)
        gnd_f.append(ls); gnd_items.append((f'tap{num}_{i}', ls)); ids.append(f'tap{num}_{i}')
    if entry['via']:
        vc = Point(*entry['via']).buffer(0.3)
        for L in raw: raw[L].append(('GND', vc))
        gnd_f.append(vc); gnd_items.append((f'tapvia{num}', vc)); ids.append(f'tapvia{num}')
    return ids
def ungrow(ids):
    keep = [(i, s) for i, s in gnd_items if i not in ids]
    gnd_items.clear(); gnd_items.extend(keep)
    gnd_f.clear(); gnd_f.extend(s for _, s in keep)

tap_ids = {}
for num in ORDER:
    e = None
    for wtry in (0.2, 0.15, 0.1):
        W = wtry
        e = plan_one(num, grounded_only=False)
        if e is not None: break
    if e is None:
        print('pad', num, 'TAP FAILED'); continue
    out[num] = e; tap_ids[num] = grow(num, e)
    if e['target'] in ('via10', 'via05') or (e['hit'] in grounded_ids):
        grounded_ids.add(f'U1.{num}'); grounded_ids.update(tap_ids[num])
    print('pad', num, 'target', e['target'], 'hit', e['hit'], 'via', e['via'],
          'grounded:', f'U1.{num}' in grounded_ids)
for _pass in range(4):
    todo = [n for n in ORDER if n in out and f'U1.{n}' not in grounded_ids]
    if not todo: break
    print('closure pass', _pass + 2, 'ungrounded:', todo)
    for num in todo:
        ungrow(set(tap_ids[num]))
        W = 0.1
        e = plan_one(num, grounded_only=True)
        if e is None:
            print('pad', num, 'CLOSURE FAILED'); continue
        out[num] = e; tap_ids[num] = grow(num, e)
        grounded_ids.add(f'U1.{num}'); grounded_ids.update(tap_ids[num])
        print('pad', num, 're-planned target', e['target'], 'hit', e['hit'], 'via', e['via'])
print('all grounded:', all(f'U1.{n}' in grounded_ids for n in ORDER))
(E/'gnd_taps.json').write_text(json.dumps(out, indent=1))
print('taps planned:', len(out), 'of', len(ORDER))
