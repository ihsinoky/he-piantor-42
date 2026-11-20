"""S3c/S3d: west-cluster re-route on the work board (model-based).

KiCad SWIG in this build degrades board container iterators (GetTracks /
GetFootprints) after mass Remove() calls, so EVERYTHING is snapshotted into
a Python model first; the board is only mutated via Remove/Add of known
objects, and all queries read the model.

Per target net: delete model tracks/vias with any geometry west of CUT_X,
compute remaining components (pads + tracks + vias + zone fills for GND are
NOT modelled -- GND handled separately), reconnect components with a
multi-source grid A* (layers F/I2/B):
  - cell centre inside outline eroded by 0.5 + w/2 (+0.05 safety)
  - clearance to other nets: 0.05 inside the D-057 field rect (0.05-class
    nets only), 0.10 elsewhere; antenna strip blocked on all layers;
    trackpad circle blocked on F/B; no diagonal corner-cutting
  - vias 0.6/0.3, sites cleared on all layers at 0.10, never on pads,
    centre >=0.85mm inside the outline
Usage: kpy.sh west_router.py NET [NET...]
"""
import pcbnew as p, math, sys, heapq, os
from shapely.geometry import Point, LineString, Polygon, box
from shapely.strtree import STRtree

DST = '.issue292-runtime/wmain-work.kicad_pcb'
CUT_X = 84.5
FIELD = (69.3, 119.05, 80.9, 128.9)
ANT = Polygon([(70.3, 128.9), (79.9, 128.9), (79.9, 137.9), (70.3, 137.9)])
CIRC = Point(100, 118).buffer(20.0)
LAYERS = ['F', 'I2', 'B']
LC = {'F': p.F_Cu, 'I2': p.In2_Cu, 'B': p.B_Cu}
STEP = 0.05
NETW = {
    'SYS_3V3': (0.3, False), 'USB_DP': (0.1, False), 'USB_DM': (0.1, False),
    'PAD_SCL': (0.05, True), 'MUX_A1': (0.1, False), 'MUX_A0': (0.05, True),
    'MUX_A2': (0.05, True), 'LED_DRV': (0.05, True), 'HALL_PWR_EN': (0.05, True),
    'ADC_B': (0.1, True), 'VIN_IN': (0.1, False),
    'PAD_SDA': (0.1, False), 'PAD_DR': (0.1, False), 'PAD_3V3': (0.1, False),
    'VBAT_GATE': (0.1, False), 'VAUX': (0.2, False), 'CONV_PG': (0.1, False),
    'VBAT_SENSE': (0.1, True), 'LED_A': (0.1, False), 'ADC_C': (0.1, False),
    'HALL_3V3': (0.3, False)}

def mm(v): return v / 1e6
def iu(v): return int(round(v * 1e6))

b = p.LoadBoard(DST)

# ---------- outline ----------
po = p.SHAPE_POLY_SET(); b.GetBoardPolygonOutlines(po)
_ch = po.Outline(0); _ps = p.SHAPE_POLY_SET(); _ch.TransformToPolygon(_ps, 100, False)
_c2 = _ps.Outline(0)
OUTLINE = Polygon([(_c2.CPoint(i).x / 1e6, _c2.CPoint(i).y / 1e6) for i in range(_c2.PointCount())])

# ---------- shapes ----------
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    # KiCad orientation is CCW in y-up; board coords are y-down, so the
    # conjugate rotation applies (verified vs GetEffectiveShape, J3.10).
    return Polygon([(cx + dx * c + dy * s, cy - dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])

def pad_shape(pad):
    q = pad.GetPosition(); sz = pad.GetSize()
    cx, cy, w, h = mm(q.x), mm(q.y), mm(sz.x), mm(sz.y)
    if pad.GetShape() == p.PAD_SHAPE_CIRCLE:
        return Point(cx, cy).buffer(w / 2, quad_segs=24)
    return rect_poly(cx, cy, w, h, pad.GetOrientationDegrees())

def seg_shape(x1, y1, x2, y2, w):
    return LineString([(x1, y1), (x2, y2)]).buffer(w / 2, quad_segs=8)

def disc_shape(x, y, d):
    return Point(x, y).buffer(d / 2, quad_segs=24)

# ---------- snapshot: pads, tracks, zones ----------
PAD_INDEX = {}          # net -> [(layershape dict, ref)]
PADS_BY_LAYER = {L: [] for L in LAYERS}
OBS_STATIC = {L: [] for L in LAYERS}
for f in b.GetFootprints():
    for pad in f.Pads():
        sh = pad_shape(pad); net = pad.GetNetname()
        lay = {}
        for L in LAYERS:
            if pad.IsOnLayer(LC[L]):
                lay[L] = sh; OBS_STATIC[L].append((net, sh)); PADS_BY_LAYER[L].append((net, sh))
        if pad.GetAttribute() == p.PAD_ATTRIB_PTH:
            for L in LAYERS:
                if L not in lay:
                    lay[L] = sh; OBS_STATIC[L].append((net, sh)); PADS_BY_LAYER[L].append((net, sh))
        PAD_INDEX.setdefault(net, []).append((lay, f"{f.GetReference()}.{pad.GetNumber()}"))

for zn in b.Zones():
    if zn.GetNetname() == '':
        for L in LAYERS:
            if zn.IsOnLayer(LC[L]):
                fps = zn.GetFilledPolysList(LC[L])
                for i in range(fps.OutlineCount()):
                    ch = fps.Outline(i); ps = p.SHAPE_POLY_SET()
                    ch.TransformToPolygon(ps, 100, False)
                    c2 = ps.Outline(0)
                    pts = [(c2.CPoint(j).x / 1e6, c2.CPoint(j).y / 1e6) for j in range(c2.PointCount())]
                    if len(pts) >= 3: OBS_STATIC[L].append(('', Polygon(pts)))

MODEL = []  # {obj, net, shapes:{L:shape}, alive}
for t in b.GetTracks():
    net = t.GetNetname()
    if isinstance(t, p.PCB_VIA):
        q = t.GetPosition()
        shapes = {L: disc_shape(mm(q.x), mm(q.y), mm(t.GetWidth(LC[L]))) for L in LAYERS}
        MODEL.append({'obj': t, 'net': net, 'shapes': shapes, 'alive': True, 'via': True})
    else:
        L = {p.F_Cu: 'F', p.In2_Cu: 'I2', p.B_Cu: 'B'}.get(t.GetLayer())
        if L is None: continue
        s, e = t.GetStart(), t.GetEnd()
        sh = seg_shape(mm(s.x), mm(s.y), mm(e.x), mm(e.y), mm(t.GetWidth()))
        MODEL.append({'obj': t, 'net': net, 'shapes': {L: sh}, 'alive': True, 'via': False})

# FH12 fanout rects (J2/J3 pad rows + 1.2mm): the 0.5mm-pitch pad streets are
# 0.2mm wide, so 0.10mm tracks there sit at 0.05mm clearance -- the inherited
# Rev.10 condition. Track clearance 0.05 applies inside these rects.
FANOUT = []
for _pfx in ('J2.', 'J3.', 'JPAD.'):
    _bb = [s.bounds for net, lst in PAD_INDEX.items() for lay, ref in lst
           if ref.startswith(_pfx) for s in lay.values()]
    if _bb:
        FANOUT.append((min(x[0] for x in _bb) - 1.2, min(x[1] for x in _bb) - 1.2,
                       max(x[2] for x in _bb) + 1.2, max(x[3] for x in _bb) + 1.2))
print('FANOUT rects:', FANOUT, flush=True)

def obs_trk(L):
    return [(m['net'], m['shapes'][L]) for m in MODEL if m['alive'] and L in m['shapes']]

def all_obs(L):
    return OBS_STATIC[L] + obs_trk(L)

# ---------- components ----------
def net_components(net):
    elems = [(lay, ref) for lay, ref in PAD_INDEX.get(net, [])]
    for m in MODEL:
        if m['alive'] and m['net'] == net:
            elems.append((m['shapes'], 'via' if m['via'] else 'trk'))
    parent = list(range(len(elems)))
    def find(a):
        while parent[a] != a: parent[a] = parent[parent[a]]; a = parent[a]
        return a
    flat = []
    for i, (lay, _) in enumerate(elems):
        for L, sh in lay.items(): flat.append((i, sh))
    tree = STRtree([sh for _, sh in flat])
    for k, (i, sh) in enumerate(flat):
        for j in tree.query(sh, predicate='intersects'):
            if flat[j][0] != i: parent[find(flat[j][0])] = find(i)
    comps = {}
    for i, (lay, ref) in enumerate(elems): comps.setdefault(find(i), []).append((lay, ref))
    return list(comps.values())

def delete_west(net):
    n = 0
    for m in MODEL:
        if not m['alive'] or m['net'] != net: continue
        if any(sh.bounds[0] < CUT_X for sh in m['shapes'].values()):
            b.Remove(m['obj']); m['alive'] = False; n += 1
    return n

# ---------- rasterization ----------
def rasterize(net, w, region, via_field05=False):
    import numpy as np
    x0, y0, x1, y1 = region
    nx = int((x1 - x0) / STEP) + 1; ny = int((y1 - y0) / STEP) + 1
    xs = x0 + np.arange(nx) * STEP; ys = y0 + np.arange(ny) * STEP
    eroded = OUTLINE.buffer(-(0.5 + w / 2 + 0.05))
    def mark(shapes, arr):
        if not shapes: return
        tree = STRtree(shapes)
        for j, y in enumerate(ys):
            strip = box(x0 - 1, y - STEP / 2, x1 + 1, y + STEP / 2)
            for i in tree.query(strip, predicate='intersects'):
                inter = shapes[i].intersection(strip)
                if not inter.is_empty:
                    a, bq = inter.bounds[0], inter.bounds[2]
                    i0 = max(0, int(math.ceil((a - x0) / STEP - 1e-9)))
                    i1 = min(nx - 1, int(math.floor((bq - x0) / STEP + 1e-9)))
                    if i0 <= i1: arr[j, i0:i1 + 1] = True
    grids = {}
    for L in LAYERS:
        base = [sh for n, sh in all_obs(L) if n != net]
        s10 = [sh.buffer(0.10 + w / 2) for sh in base] + [ANT.buffer(0.10 + w / 2)]
        s05 = [sh.buffer(0.05 + w / 2) for sh in base] + [ANT.buffer(0.05 + w / 2)]
        if L in ('F', 'B'):
            s10.append(CIRC.buffer(0.10 + w / 2)); s05.append(CIRC.buffer(0.05 + w / 2))
        g10 = np.zeros((ny, nx), dtype=bool); mark(s10, g10)
        g05 = np.zeros((ny, nx), dtype=bool); mark(s05, g05)
        okm = np.zeros((ny, nx), dtype=bool); mark([eroded], okm)
        grids[L] = {'c10': g10, 'c05': g05, 'ok': okm}
    via_ok = np.ones((ny, nx), dtype=bool)
    via05 = np.ones((ny, nx), dtype=bool)
    for L in LAYERS:
        shapes = [sh.buffer(0.10 + 0.3) for n, sh in all_obs(L) if n != net]
        shapes.append(ANT.buffer(0.10 + 0.3))
        if L in ('F', 'B'): shapes.append(CIRC.buffer(0.10 + 0.3))
        arr = np.zeros((ny, nx), dtype=bool); mark(shapes, arr)
        via_ok &= ~arr
        shapes5 = [sh.buffer(0.05 + 0.3) for n, sh in all_obs(L) if n != net]
        shapes5.append(ANT.buffer(0.05 + 0.3))
        if L in ('F', 'B'): shapes5.append(CIRC.buffer(0.05 + 0.3))
        arr5 = np.zeros((ny, nx), dtype=bool); mark(shapes5, arr5)
        via05 &= ~arr5
    if via_field05:
        fi0 = max(0, int((FIELD[0] - x0) / STEP)); fi1 = min(nx - 1, int((FIELD[2] - x0) / STEP))
        fj0 = max(0, int((FIELD[1] - y0) / STEP)); fj1 = min(ny - 1, int((FIELD[3] - y0) / STEP))
        via_ok[fj0:fj1 + 1, fi0:fi1 + 1] = via05[fj0:fj1 + 1, fi0:fi1 + 1]
    okm = np.zeros((ny, nx), dtype=bool); mark([OUTLINE.buffer(-0.85)], okm)
    padm = np.zeros((ny, nx), dtype=bool)
    mark([sh for L in LAYERS for _, sh in PADS_BY_LAYER[L]], padm)
    via_ok &= okm & ~padm
    return grids, via_ok, (x0, y0, nx, ny)

# ---------- routing ----------
X0G = Y0G = 0.0
def _route_pass(net, w, field05, merge_map):
    """One Dijkstra pass. merge_map: comp index -> seed label.
    Returns (ok, group_of_comp dict). Adds copper for each connection."""
    import numpy as np
    global X0G, Y0G
    comps = net_components(net)
    if len(comps) <= 1: return True, {0: 0}
    allsh = [s for comp in comps for lay, _ in comp for s in lay.values()]
    region = (max(60.0, min(s.bounds[0] for s in allsh) - 3),
              max(70.0, min(s.bounds[1] for s in allsh) - 3),
              min(140.0, max(s.bounds[2] for s in allsh) + 3),
              min(140.0, max(s.bounds[3] for s in allsh) + 3))
    grids, via_ok, (x0, y0, nx, ny) = rasterize(net, w, region, via_field05=field05)
    X0G, Y0G = x0, y0
    lab = {L: np.full((ny, nx), -1, dtype=np.int32) for L in LAYERS}
    for ci, comp in enumerate(comps):
        sl = merge_map.get(ci, ci)
        for lay, _ref in comp:
            for L, sh in lay.items():
                a, bq, c, d = sh.bounds
                i0 = max(0, int((a - x0) / STEP) - 1); i1 = min(nx - 1, int((c - x0) / STEP) + 1)
                j0 = max(0, int((bq - y0) / STEP) - 1); j1 = min(ny - 1, int((d - y0) / STEP) + 1)
                for j in range(j0, j1 + 1):
                    for i in range(i0, i1 + 1):
                        if sh.contains(Point(x0 + i * STEP, y0 + j * STEP)):
                            lab[L][j, i] = sl
    blocked = {}
    fmask = np.zeros((ny, nx), dtype=bool)
    rects = ([FIELD] if field05 else []) + FANOUT
    for (rx0, ry0, rx1, ry1) in rects:
        fi0 = max(0, int((rx0 - x0) / STEP)); fi1 = min(nx - 1, int((rx1 - x0) / STEP))
        fj0 = max(0, int((ry0 - y0) / STEP)); fj1 = min(ny - 1, int((ry1 - y0) / STEP))
        fmask[fj0:fj1 + 1, fi0:fi1 + 1] = True
    for L in LAYERS:
        base = grids[L]['c10'] | ~grids[L]['ok']
        if rects:
            base = np.where(fmask, grids[L]['c05'] | ~grids[L]['ok'], base)
        blocked[L] = base
    parent = {}; dist = {}; label = {}; heap = []
    seed_labels = sorted({merge_map.get(ci, ci) for ci in range(len(comps))})
    for L in LAYERS:
        jj, ii = np.nonzero(lab[L] >= 0)
        for j, i in zip(jj.tolist(), ii.tolist()):
            key = (L, int(j), int(i)); dist[key] = 0.0; label[key] = int(lab[L][j, i])
            heapq.heappush(heap, (0.0, key))
    group = {s: s for s in seed_labels}
    def gfind(a):
        while group[a] != a: group[a] = group[group[a]]; a = group[a]
        return a
    connections = []
    DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
            (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))]
    while heap and len({gfind(s) for s in seed_labels}) > 1:
        dcur, key = heapq.heappop(heap)
        if dcur > dist.get(key, 1e18) + 1e-9: continue
        L, j, i = key; mygrp = gfind(label[key])
        if via_ok[j, i]:
            for L2 in LAYERS:
                if L2 == L: continue
                k2 = (L2, j, i)
                if k2 not in dist:
                    dist[k2] = dcur + 1.5; label[k2] = label[key]; parent[k2] = key
                    heapq.heappush(heap, (dist[k2], k2))
        for di, dj, cst in DIRS:
            ni, nj = i + di, j + dj
            if not (0 <= ni < nx and 0 <= nj < ny): continue
            k2 = (L, nj, ni)
            if k2 in label and gfind(label[k2]) != mygrp:
                connections.append((key, k2))
                group[gfind(label[k2])] = mygrp
                continue
            if blocked[L][nj, ni]: continue
            if di and dj and (blocked[L][j, ni] or blocked[L][nj, i]): continue
            if k2 not in dist or dcur + cst * STEP < dist[k2]:
                dist[k2] = dcur + cst * STEP; label[k2] = label[key]; parent[k2] = key
                heapq.heappush(heap, (dist[k2], k2))
    ngroups = len({gfind(s) for s in seed_labels})
    print(f'  pass w={w}: connections {len(connections)}; groups left {ngroups}', flush=True)
    def path_to(key):
        pts = []
        while key is not None:
            pts.append(key); key = parent.get(key)
        return pts[::-1]
    nadd = 0
    for k1, k2 in connections:
        full = path_to(k1) + path_to(k2)[::-1]
        run = [full[0]]
        for st in full[1:]:
            if st[0] != run[-1][0]:
                nadd += emit_run(net, w, run)
                add_via(net, X0G + run[-1][2] * STEP, Y0G + run[-1][1] * STEP); nadd += 1
                run = [st]
            else:
                run.append(st)
        nadd += emit_run(net, w, run)
    print(f'  pass w={w}: added {nadd} items', flush=True)
    group_of = {ci: gfind(merge_map.get(ci, ci)) for ci in range(len(comps))}
    if ngroups > 1:
        for ci, comp in enumerate(comps):
            refs = [r for _, r in comp if r not in ('trk', 'via')]
            bb = [s.bounds for lay, _ in comp for s in lay.values()]
            bx = (round(min(x[0] for x in bb), 1), round(min(x[1] for x in bb), 1),
                  round(max(x[2] for x in bb), 1), round(max(x[3] for x in bb), 1)) if bb else None
            print(f'    group {group_of[ci]} comp {ci}: pads={refs[:8]} bbox={bx}', flush=True)
    return ngroups <= 1, group_of

SKIP_DELETE = set()
def route_net(net):
    w, field05 = NETW[net]
    nk = 0 if net in SKIP_DELETE else delete_west(net)
    comps = net_components(net)
    print(f'{net}: deleted {nk} west items; components after cut: {len(comps)}', flush=True)
    if len(comps) <= 1:
        print(f'{net}: nothing to reconnect'); return True
    ok, group_of = _route_pass(net, w, field05, {})
    if ok: return True
    # neck passes: merge the largest group into seed 0, islands keep own seeds
    for nw in (0.10, 0.05):
        comps = net_components(net)
        if len(comps) <= 1: return True
        from collections import Counter
        cnt = Counter(group_of.get(ci, ci) for ci in range(len(net_components(net))) if False)
        # recompute group sizes from previous pass mapping against fresh comps is
        # unreliable; instead: seed = 0 for the comp containing the most pads
        sizes = []
        for ci, comp in enumerate(comps):
            npads = sum(1 for _, r in comp if r not in ('trk', 'via'))
            sizes.append((npads, ci))
        main_ci = max(sizes)[1]
        merge_map = {ci: (0 if ci == main_ci else ci + 1) for ci in range(len(comps))}
        print(f'{net}: neck pass w={nw} (main comp {main_ci})', flush=True)
        ok, group_of = _route_pass(net, nw, True, merge_map)
        if ok: return True
        # translate group_of back to comp indices for a possible next pass
        group_of = {ci: group_of[ci] for ci in range(len(comps))}
    return len(net_components(net)) <= 1

def emit_run(net, w, run):
    if len(run) < 2: return 0
    L = run[0][0]
    pts = [(X0G + i * STEP, Y0G + j * STEP) for (_L, j, i) in run]
    simp = [pts[0]]
    for k in range(1, len(pts) - 1):
        a, bq, c = simp[-1], pts[k], pts[k + 1]
        if abs((bq[0] - a[0]) * (c[1] - bq[1]) - (bq[1] - a[1]) * (c[0] - bq[0])) > 1e-9:
            simp.append(bq)
    simp.append(pts[-1])
    netobj = b.FindNet(net); n = 0
    for a, bq in zip(simp, simp[1:]):
        if math.hypot(bq[0] - a[0], bq[1] - a[1]) < 1e-6: continue
        t = p.PCB_TRACK(b)
        t.SetStart(p.VECTOR2I(iu(a[0]), iu(a[1]))); t.SetEnd(p.VECTOR2I(iu(bq[0]), iu(bq[1])))
        t.SetWidth(iu(w)); t.SetLayer(LC[L]); t.SetNet(netobj)
        b.Add(t)
        MODEL.append({'obj': t, 'net': net, 'alive': True, 'via': False,
                      'shapes': {L: seg_shape(a[0], a[1], bq[0], bq[1], w)}})
        n += 1
    return n

def add_via(net, x, y):
    v = p.PCB_VIA(b)
    v.SetPosition(p.VECTOR2I(iu(x), iu(y)))
    v.SetWidth(iu(0.6)); v.SetDrill(iu(0.3))
    v.SetNet(b.FindNet(net))
    b.Add(v)
    MODEL.append({'obj': v, 'net': net, 'alive': True, 'via': True,
                  'shapes': {L: disc_shape(x, y, 0.6) for L in LAYERS}})

if sys.argv[1:] == ['DELETE_GND']:
    n = delete_west('GND')
    p.SaveBoard(DST, b)
    print('DELETE_GND saved, deleted', n)
    sys.exit(0)

if sys.argv[1:] == ['DELETE_ALL']:
    tot = 0
    for net in NETW:
        n = delete_west(net); tot += n
        print(f'{net}: deleted {n}')
    p.SaveBoard(DST, b)
    print('DELETE_ALL saved, total', tot)
    sys.exit(0)

def micro_escape(net, padref):
    """Connect the component containing pad `padref` to any other component
    of the net, on a 0.025mm grid in a tight region (w=0.05, field rules)."""
    import numpy as np
    global STEP, X0G, Y0G
    comps = net_components(net)
    si = [i for i, c in enumerate(comps) if any(r == padref for _, r in c)]
    if not si: print('MICRO: pad not found', padref); return False
    si = si[0]
    if len(comps) <= 1: print('MICRO: single component already'); return True
    STEP = 0.025
    w = 0.05
    sb = [s.bounds for lay, _ in comps[si] for s in lay.values()]
    rx0 = max(60.0, min(x[0] for x in sb) - 2.0); ry0 = max(70.0, min(x[1] for x in sb) - 5.0)
    ry1 = min(140.0, max(x[3] for x in sb) + 5.0)
    # extend in ALL directions until another component's copper intersects
    # the region (a northward target must pull the region north, etc.)
    rx1 = min(x[2] for x in sb) + 2.0
    others = [s for ci, comp in enumerate(comps) if ci != si for lay, _ in comp for s in lay.values()]
    def _hit():
        return any(s.bounds[0] < rx1 and s.bounds[2] > rx0 and
                   s.bounds[1] < ry1 and s.bounds[3] > ry0 for s in others)
    while not _hit() and (rx1 < 140 or ry0 > 70 or ry1 < 140 or rx0 > 60):
        rx1 = min(140.0, rx1 + 2.0); ry0 = max(70.0, ry0 - 2.0)
        ry1 = min(140.0, ry1 + 2.0); rx0 = max(60.0, rx0 - 2.0)
    region = (rx0, ry0, rx1, ry1)
    if os.environ.get('MICRO_FULL') == '1':
        allb = [s.bounds for comp in comps for lay, _ in comp for s in lay.values()]
        region = (max(60.0, min(x[0] for x in allb) - 3), max(70.0, min(x[1] for x in allb) - 3),
                  min(140.0, max(x[2] for x in allb) + 3), min(140.0, max(x[3] for x in allb) + 3))
    print(f'MICRO {net} {padref}: region {tuple(round(v,1) for v in region)}', flush=True)
    grids, via_ok, (x0, y0, nx, ny) = rasterize(net, w, region, via_field05=True)
    X0G, Y0G = x0, y0
    clr_x = float(os.environ.get('MICRO_CLR', '0.05'))
    if clr_x != 0.05:
        # rebuild the 'c05' grids at the requested clearance
        import numpy as _np
        for L in LAYERS:
            shapes = [sh.buffer(clr_x + w / 2) for n, sh in all_obs(L) if n != net]
            shapes.append(ANT.buffer(clr_x + w / 2))
            if L in ('F', 'B'): shapes.append(CIRC.buffer(clr_x + w / 2))
            arr = _np.zeros((ny, nx), dtype=bool)
            tree = STRtree(shapes)
            ys = y0 + _np.arange(ny) * STEP
            for j, y in enumerate(ys):
                strip = box(x0 - 1, y - STEP / 2, x0 + nx * STEP + 1, y + STEP / 2)
                for i in tree.query(strip, predicate='intersects'):
                    inter = shapes[i].intersection(strip)
                    if not inter.is_empty:
                        a, bq = inter.bounds[0], inter.bounds[2]
                        i0 = max(0, int(math.ceil((a - x0) / STEP - 1e-9)))
                        i1 = min(nx - 1, int(math.floor((bq - x0) / STEP + 1e-9)))
                        if i0 <= i1: arr[j, i0:i1 + 1] = True
            grids[L]['c05'] = arr
    lab = {L: np.full((ny, nx), -1, dtype=np.int32) for L in LAYERS}
    for ci, comp in enumerate(comps):
        sl = 1 if ci == si else 0
        for lay, _ref in comp:
            for L, sh in lay.items():
                a, bq, c, d = sh.bounds
                if c < region[0] or a > region[2] or d < region[1] or bq > region[3]: continue
                i0 = max(0, int((a - x0) / STEP) - 1); i1 = min(nx - 1, int((c - x0) / STEP) + 1)
                j0 = max(0, int((bq - y0) / STEP) - 1); j1 = min(ny - 1, int((d - y0) / STEP) + 1)
                for j in range(j0, j1 + 1):
                    for i in range(i0, i1 + 1):
                        if sh.contains(Point(x0 + i * STEP, y0 + j * STEP)):
                            lab[L][j, i] = sl
    fmask = np.zeros((ny, nx), dtype=bool)
    for (fx0, fy0, fx1, fy1) in [FIELD] + FANOUT:
        fi0 = max(0, int((fx0 - x0) / STEP)); fi1 = min(nx - 1, int((fx1 - x0) / STEP))
        fj0 = max(0, int((fy0 - y0) / STEP)); fj1 = min(ny - 1, int((fy1 - y0) / STEP))
        fmask[fj0:fj1 + 1, fi0:fi1 + 1] = True
    blocked = {}
    for L in LAYERS:
        blocked[L] = np.where(fmask, grids[L]['c05'] | ~grids[L]['ok'],
                              grids[L]['c10'] | ~grids[L]['ok'])
    parent = {}; dist = {}; label = {}; heap = []
    for L in LAYERS:
        jj, ii = np.nonzero(lab[L] >= 0)
        for j, i in zip(jj.tolist(), ii.tolist()):
            key = (L, int(j), int(i)); dist[key] = 0.0; label[key] = int(lab[L][j, i])
            heapq.heappush(heap, (0.0, key))
    found = None
    NOCUT = os.environ.get('MICRO_NOCUT') == '1'
    DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
            (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))]
    while heap and found is None:
        dcur, key = heapq.heappop(heap)
        if dcur > dist.get(key, 1e18) + 1e-9: continue
        L, j, i = key; mylab = label[key]
        if via_ok[j, i]:
            for L2 in LAYERS:
                if L2 == L: continue
                k2 = (L2, j, i)
                if k2 not in dist:
                    dist[k2] = dcur + 1.5; label[k2] = mylab; parent[k2] = key
                    heapq.heappush(heap, (dist[k2], k2))
        for di, dj, cst in DIRS:
            ni, nj = i + di, j + dj
            if not (0 <= ni < nx and 0 <= nj < ny): continue
            k2 = (L, nj, ni)
            if k2 in label and label[k2] != mylab:
                found = (key, k2); break
            if blocked[L][nj, ni]: continue
            if di and dj and not NOCUT and (blocked[L][j, ni] or blocked[L][nj, i]): continue
            if k2 not in dist or dcur + cst * STEP < dist[k2]:
                dist[k2] = dcur + cst * STEP; label[k2] = mylab; parent[k2] = key
                heapq.heappush(heap, (dist[k2], k2))
    if found is None:
        print('MICRO: no path found'); return False
    def path_to(key):
        pts = []
        while key is not None:
            pts.append(key); key = parent.get(key)
        return pts[::-1]
    full = path_to(found[0]) + path_to(found[1])[::-1]
    run = [full[0]]; nadd = 0
    for st in full[1:]:
        if st[0] != run[-1][0]:
            nadd += emit_run(net, w, run)
            add_via(net, X0G + run[-1][2] * STEP, Y0G + run[-1][1] * STEP); nadd += 1
            run = [st]
        else:
            run.append(st)
    nadd += emit_run(net, w, run)
    print(f'MICRO: connected with {nadd} items', flush=True)
    return True

if sys.argv[1:] and sys.argv[1].startswith('MICRO:'):
    _, _net, _pad = sys.argv[1].split(':')
    _ok = micro_escape(_net, _pad)
    if _ok: p.SaveBoard(DST, b); print('MICRO saved')
    sys.exit(0 if _ok else 1)

ok = True
for net in sys.argv[1:]:
    if net.startswith('K:'):
        net = net[2:]; SKIP_DELETE.add(net)
    if route_net(net):
        p.SaveBoard(DST, b)
        print('saved after', net, flush=True)
    else:
        ok = False
        print('NOT saved (failed):', net, flush=True)
        break
print('ALL OK' if ok else 'SOME FAILED')
