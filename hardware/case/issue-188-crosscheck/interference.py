"""Geometric interference checks (plan view, KiCad frame X right / Y down, mm).
Imported by extract.py. Stdlib only. Geometry only: no electrical DRC result is used.
Obstacle model: copper (pads, tracks, vias, plated barrels), component envelopes, NPTH holes.
Component bodies are NOT in the board data (no Fab/3D); a component envelope is the bounding box of its pads,
except connectors whose body is a documented value (J1 HRO, J2/J3/J_WING JST BM14B)."""
import math



# ---------- primitives: ('r',x0,y0,x1,y1) ('c',x,y,r) ('s',x1,y1,x2,y2,w)
def seg_pt(p, a, c):
    vx, vy = c[0] - a[0], c[1] - a[1]
    n = vx * vx + vy * vy
    t = 0 if n == 0 else max(0, min(1, ((p[0] - a[0]) * vx + (p[1] - a[1]) * vy) / n))
    return math.hypot(p[0] - a[0] - t * vx, p[1] - a[1] - t * vy)


def d_pt(p, g):
    if g[0] == 'r':
        return math.hypot(max(g[1] - p[0], 0, p[0] - g[3]), max(g[2] - p[1], 0, p[1] - g[4]))
    if g[0] == 'c':
        return math.hypot(p[0] - g[1], p[1] - g[2]) - g[3]
    return seg_pt(p, (g[1], g[2]), (g[3], g[4])) - g[5] / 2


def bbox(g):
    if g[0] == 'r':
        return list(g[1:5])
    if g[0] == 'c':
        return [g[1] - g[3], g[2] - g[3], g[1] + g[3], g[2] + g[3]]
    h = g[5] / 2
    return [min(g[1], g[3]) - h, min(g[2], g[4]) - h, max(g[1], g[3]) + h, max(g[2], g[4]) + h]


def seg_hits_rect(a, c, R):
    t0, t1 = 0.0, 1.0
    dx, dy = c[0] - a[0], c[1] - a[1]
    for p, q in ((-dx, a[0] - R[0]), (dx, R[2] - a[0]), (-dy, a[1] - R[1]), (dy, R[3] - a[1])):
        if p == 0:
            if q < 0:
                return False
        else:
            t = q / p
            if p < 0:
                t0 = max(t0, t)
            else:
                t1 = min(t1, t)
    return t0 <= t1


def d_rect(R, g):
    """Distance between rectangle R=[x0,y0,x1,y1] and geometry g (0 when touching or overlapping)."""
    if g[0] == 'r':
        return math.hypot(max(g[1] - R[2], R[0] - g[3], 0), max(g[2] - R[3], R[1] - g[4], 0))
    if g[0] == 'c':
        return max(0.0, d_pt((g[1], g[2]), ('r',) + tuple(R)) - g[3])
    a, c, h = (g[1], g[2]), (g[3], g[4]), g[5] / 2
    if seg_hits_rect(a, c, R):
        return 0.0
    corners = [(R[0], R[1]), (R[0], R[3]), (R[2], R[1]), (R[2], R[3])]
    return max(0.0, min([d_pt(p, ('r',) + tuple(R)) for p in (a, c)] + [seg_pt(p, a, c) for p in corners]) - h)


def rect_gap(a, b):
    return math.hypot(max(a[0] - b[2], b[0] - a[2], 0), max(a[1] - b[3], b[1] - a[3], 0))


def overlaps(R, g, shrink=1e-6):
    return d_rect([R[0] + shrink, R[1] + shrink, R[2] - shrink, R[3] - shrink], g) <= 0.0


# ---------- board items
def board_items(bd, ctx):
    """Returns items (dict: face, geom, ref, kind). kind: pad/tp/th/track/via/hole/body."""
    children, child, all_pads = ctx['children'], ctx['child'], ctx['all_pads']
    items = []
    for q in all_pads(bd):
        r = q['rect']
        w, h = r[2] - r[0], r[3] - r[1]
        if q['kind'] == 'np_thru_hole':
            geom, kind, faces = ('c', (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, w / 2), 'hole', 'FB'
        else:
            geom = ('c', (r[0] + r[2]) / 2, (r[1] + r[3]) / 2, w / 2) if q['shape'] == 'circle' else ('r',) + tuple(r)
            kind = 'th' if q['kind'] == 'thru_hole' else ('tp' if q['ref'].startswith('TP') else 'pad')
            lay = q['layers']
            faces = ('F' if ('F.Cu' in lay or '*.Cu' in lay) else '') + ('B' if ('B.Cu' in lay or '*.Cu' in lay) else '')
        for f in faces:
            items.append(dict(face=f, geom=geom, ref=q['ref'], kind=kind, layer=f + '.Cu'))
    for s in children(bd, 'segment'):
        st, en = list(map(float, child(s, 'start')[1:3])), list(map(float, child(s, 'end')[1:3]))
        lay = child(s, 'layer')[1]
        face = {'F.Cu': 'F', 'B.Cu': 'B'}.get(lay, 'I')
        items.append(dict(face=face, geom=('s', st[0], st[1], en[0], en[1], float(child(s, 'width')[1])), ref='track', kind='track', layer=lay))
    for v in children(bd, 'via'):
        x, y = map(float, child(v, 'at')[1:3])
        for f in 'FB':
            items.append(dict(face=f, geom=('c', x, y, float(child(v, 'size')[1]) / 2), ref='via', kind='via', layer=f + '.Cu'))
    return items


def envelopes(bd, ctx, overrides=None):
    """Component envelope = bbox of its pads (body unknown); overrides[ref] replaces it with a documented body."""
    children, child, all_pads = ctx['children'], ctx['child'], ctx['all_pads']
    env = {}
    for q in all_pads(bd):
        if q['kind'] == 'np_thru_hole':
            continue
        e = env.setdefault(q['ref'], list(q['rect']))
        e[:] = [min(e[0], q['rect'][0]), min(e[1], q['rect'][1]), max(e[2], q['rect'][2]), max(e[3], q['rect'][3])]
    faces = {}
    for f in children(bd, 'footprint'):
        ref = next(p[2] for p in children(f, 'property') if p[1] == 'Reference')
        faces[ref] = 'F' if child(f, 'layer')[1] == 'F.Cu' else 'B'
    out = {r: dict(rect=e, face=faces[r], source='pad-bbox') for r, e in env.items()}
    for r, (rect, src) in (overrides or {}).items():
        out[r] = dict(rect=rect, face=faces[r], source=src)
    return out


# ---------- grid
class Grid:
    def __init__(self, x0, y0, x1, y1, res=0.05):
        self.x0, self.y0, self.res = x0, y0, res
        self.half_diag = res * 0.7072
        self.nx, self.ny = int(round((x1 - x0) / res)), int(round((y1 - y0) / res))
        self.b = bytearray(self.nx * self.ny)

    def block(self, g, margin=0.0):
        bb = bbox(g)
        m = margin + self.res
        i0 = max(0, int((bb[0] - m - self.x0) / self.res)); i1 = min(self.nx - 1, int((bb[2] + m - self.x0) / self.res))
        j0 = max(0, int((bb[1] - m - self.y0) / self.res)); j1 = min(self.ny - 1, int((bb[3] + m - self.y0) / self.res))
        for j in range(j0, j1 + 1):
            cy = self.y0 + (j + .5) * self.res
            row = j * self.nx
            for i in range(i0, i1 + 1):
                if d_pt((self.x0 + (i + .5) * self.res, cy), g) < margin + self.half_diag:
                    self.b[row + i] = 1

    def free(self, i, j):
        return not self.b[j * self.nx + i]

    def ij(self, x, y):
        return int(round((x - self.x0) / self.res)), int(round((y - self.y0) / self.res))

    def mm(self, i0, j0, i1, j1):  # cell range [i0,i1) x [j0,j1) -> mm rect
        return [round(self.x0 + i0 * self.res, 3), round(self.y0 + j0 * self.res, 3), round(self.x0 + i1 * self.res, 3), round(self.y0 + j1 * self.res, 3)]

    def _hist(self, heights, base_axis):
        """largest rectangle in a histogram -> (area_cells, start, end(excl), height)"""
        best = (0, 0, 0, 0)
        st = []
        for k, h in enumerate(heights + [0]):
            s = k
            while st and st[-1][1] >= h:
                s, hh = st.pop()
                a = hh * (k - s)
                if a > best[0]:
                    best = (a, s, k, hh)
            st.append((s, h))
        return best

    def largest(self, region, anchor=None):
        """Largest free axis-aligned rectangle inside region [x0,y0,x1,y1]. anchor in N/S/E/W: rectangle must touch that region side."""
        i0, j0 = self.ij(region[0], region[1]); i1, j1 = self.ij(region[2], region[3])
        i0, j0, i1, j1 = max(i0, 0), max(j0, 0), min(i1, self.nx), min(j1, self.ny)
        best = (0, None)
        if anchor is None:
            h = [0] * (i1 - i0)
            for j in range(j0, j1):
                h = [(h[k] + 1) if self.free(i0 + k, j) else 0 for k in range(i1 - i0)]
                a, s, e, hh = self._hist(h, 0)
                if a > best[0]:
                    best = (a, (i0 + s, j - hh + 1, i0 + e, j + 1))
        elif anchor in 'NS':
            rows = range(j0, j1) if anchor == 'N' else range(j1 - 1, j0 - 1, -1)
            depth = [0] * (i1 - i0); alive = [True] * (i1 - i0)
            for n, j in enumerate(rows):
                for k in range(i1 - i0):
                    alive[k] = alive[k] and self.free(i0 + k, j)
                    if alive[k]:
                        depth[k] = n + 1
            a, s, e, hh = self._hist(depth, 0)
            best = (a, (i0 + s, j0, i0 + e, j0 + hh) if anchor == 'N' else (i0 + s, j1 - hh, i0 + e, j1))
        else:
            cols = range(i0, i1) if anchor == 'W' else range(i1 - 1, i0 - 1, -1)
            depth = [0] * (j1 - j0); alive = [True] * (j1 - j0)
            for n, i in enumerate(cols):
                for k in range(j1 - j0):
                    alive[k] = alive[k] and self.free(i, j0 + k)
                    if alive[k]:
                        depth[k] = n + 1
            a, s, e, hh = self._hist(depth, 0)
            best = (a, (i0, j0 + s, i0 + hh, j0 + e) if anchor == 'W' else (i1 - hh, j0 + s, i1, j0 + e))
        if not best[1]:
            return dict(rect_xy=None, w=0.0, h=0.0, area=0.0)
        r = self.mm(*best[1])
        return dict(rect_xy=r, w=round(r[2] - r[0], 3), h=round(r[3] - r[1], 3), area=round((r[2] - r[0]) * (r[3] - r[1]), 3))

    def free_depth_profile(self, region, anchor, step=1.0):
        """For each column (N/S anchor) or row (E/W) every `step` mm: free depth from the anchored side."""
        i0, j0 = self.ij(region[0], region[1]); i1, j1 = self.ij(region[2], region[3])
        out = []
        n = int(round(step / self.res))
        if anchor in 'NS':
            for i in range(i0, i1, n):
                d = 0
                rng = range(j0, j1) if anchor == 'N' else range(j1 - 1, j0 - 1, -1)
                # worst case over the cells of this step column
                depth = min(self._col_depth(i + k, rng) for k in range(n) if i + k < i1)
                out.append([round(self.x0 + i * self.res, 2), round(depth * self.res, 2)])
        else:
            for j in range(j0, j1, n):
                rng = range(i0, i1) if anchor == 'W' else range(i1 - 1, i0 - 1, -1)
                depth = min(self._row_depth(j + k, rng) for k in range(n) if j + k < j1)
                out.append([round(self.y0 + j * self.res, 2), round(depth * self.res, 2)])
        return out

    def _col_depth(self, i, rng):
        d = 0
        for j in rng:
            if not self.free(i, j):
                break
            d += 1
        return d

    def _row_depth(self, j, rng):
        d = 0
        for i in rng:
            if not self.free(i, j):
                break
            d += 1
        return d


def make_grid(board_rect, items, face, kinds, margin, res=0.05, extra=()):
    g = Grid(*board_rect, res=res)
    for e in extra:
        g.block(e, margin)
    for it in items:
        if it['face'] == face and it['kind'] in kinds:
            g.block(it['geom'], margin)
    return g


def rnd(v, n=3):
    return round(v, n)


def ascii_map(board_rect, items, env, face, region, cell=1.0):
    """1mm cells: # component envelope, T test pad, o hole, v via, c other copper (pad/track/barrel), . free"""
    x0, y0, x1, y1 = region
    lines = []
    for j in range(int(round((y1 - y0) / cell))):
        row = ''
        for i in range(int(round((x1 - x0) / cell))):
            R = [x0 + i * cell, y0 + j * cell, x0 + (i + 1) * cell, y0 + (j + 1) * cell]
            ch = '.'
            kinds = set()
            for it in items:
                if it['face'] == face and overlaps(R, it['geom']):
                    kinds.add(it['kind'])
            body = any(e['face'] == face and overlaps(R, ('r',) + tuple(e['rect'])) for e in env.values())
            ch = 'o' if 'hole' in kinds else '#' if body else 'T' if 'tp' in kinds else 'v' if 'via' in kinds else 'c' if kinds else '.'
            row += ch
        lines.append(f'Y{y0 + j * cell:6.1f} ' + row)
    hdr = '        ' + ''.join(str(int((x0 + i * cell) // 10 % 10)) if (x0 + i * cell) % 10 == 0 else ' ' for i in range(int(round((x1 - x0) / cell))))
    return [f'face={face} X{x0}-{x1} Y{y0}-{y1} cell={cell}mm  (#=component envelope T=testpad o=hole v=via c=pad/track/barrel .=free)', hdr] + lines


# ======================================================================
def union(a, b):
    return [min(a[0], b[0]), min(a[1], b[1]), max(a[2], b[2]), max(a[3], b[3])]


def fill_polygons(bd, ctx, layer):
    children, child = ctx['children'], ctx['child']
    out = []
    for z in children(bd, 'zone'):
        if children(z, 'keepout'):
            continue
        for fp in children(z, 'filled_polygon'):
            if child(fp, 'layer')[1] == layer:
                out.append([list(map(float, p[1:3])) for p in children(child(fp, 'pts'), 'xy')])
    return out


def pip(p, poly):
    c = False
    for k in range(len(poly)):
        a, b = poly[k], poly[(k + 1) % len(poly)]
        if (a[1] > p[1]) != (b[1] > p[1]) and p[0] < (b[0] - a[0]) * (p[1] - a[1]) / (b[1] - a[1]) + a[0]:
            c = not c
    return c


def boss_checks(name, bd, inv, ctx, items, env, fills):
    """Pair 1: phi4.5 boss envelope (and the phi4 washer of #163) vs keepout, copper on every layer, edges, bodies."""
    children, child = ctx['children'], ctx['child']
    x0, y0, x1, y1 = inv['bounds_xy_mm']
    assert len(inv['edges']) == 4
    holes = [h for h in inv['holes'] if h['ref'].startswith('H')]
    zones = []
    for z in children(bd, 'zone'):
        if children(z, 'keepout'):
            pts = [list(map(float, p[1:3])) for p in children(child(child(z, 'polygon'), 'pts'), 'xy')]
            zones.append((pts, child(z, 'layers')[1:], child(z, 'keepout')))
    res = []
    for h in holes:
        c = (h['x'], h['y'])
        edge = {'W': c[0] - x0, 'E': x1 - c[0], 'N': c[1] - y0, 'S': y1 - c[1]}
        near = min(edge, key=edge.get)
        ko = None
        for pts, layers, k in zones:
            rad = [math.hypot(p[0] - c[0], p[1] - c[1]) for p in pts]
            if max(abs(r - 2.5) for r in rad) < 0.001:
                apothem = min(seg_pt(c, pts[i], pts[(i + 1) % len(pts)]) for i in range(len(pts)))
                ko = dict(layers=layers, n_vertices=len(pts), vertex_radius_max=rnd(max(rad), 4), inscribed_radius=rnd(apothem, 4),
                          forbids=[x[0] for x in k if x[1] == 'not_allowed'])
        per_layer = {}
        for it in items:
            if it['ref'] == h['ref'] or it['kind'] == 'hole' and it['ref'] == h['ref']:
                continue
            d = d_pt(c, it['geom'])
            lay = it['layer']
            if lay not in per_layer or d < per_layer[lay][0]:
                per_layer[lay] = (d, it['kind'] + (':' + it['ref'] if it['ref'] != 'track' else ''))
        for lay, polys in fills.items():
            best = None
            for poly in polys:
                ins = pip(c, poly)
                dd = min(seg_pt(c, poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly)))
                dd = -dd if ins else dd
                if best is None or dd < best:
                    best = dd
            if best is not None:
                per_layer[lay] = (best, 'GND fill boundary')
        anyd = min(v[0] for v in per_layer.values())
        body = min(((rect_dist_pt(c, e['rect']), r) for r, e in env.items()), key=lambda t: t[0])
        res.append(dict(hole=h['ref'], xy=c, edge_distance_mm={k: rnd(v) for k, v in edge.items()}, nearest_edge=near,
                        boss_4_5_edge_clearance_mm=rnd(edge[near] - 2.25), washer_4_0_edge_clearance_mm=rnd(edge[near] - 2.0),
                        keepout=ko,
                        nearest_copper_per_layer_center_distance_mm={k: [rnd(v[0]), v[1]] for k, v in sorted(per_layer.items())},
                        nearest_copper_center_distance_mm=rnd(anyd),
                        boss_4_5_copper_clearance_mm=rnd(anyd - 2.25), reservation_5_0_copper_clearance_mm=rnd(anyd - 2.5),
                        nearest_component_envelope=[body[1], rnd(body[0]), rnd(body[0] - 2.25)]))
    return dict(board=name, holes=res)


def rect_dist_pt(p, r):
    return math.hypot(max(r[0] - p[0], 0, p[0] - r[2]), max(r[1] - p[1], 0, p[1] - r[3]))


def circle_rect_gap(c, r, R):
    return rect_dist_pt(c, R) - r


def zone_report(g, region, anchor=None):
    return g.largest(region, anchor)


def run(ctx):
    children, child = ctx['children'], ctx['child']
    out = {}
    MB, minv = ctx['main_b'], ctx['main']
    bx0, by0, bx1, by1 = minv['bounds_xy_mm']
    items = board_items(MB, ctx)
    j = {r: ctx['connectors'][r]['at'][:2] for r in ('J1', 'J2', 'J3')}
    def ghbody(o):
        return [o[0] - 10.375, o[1] + 0.2, o[0] + 10.375, o[1] + 4.45]
    def ghhousing(o):
        yc = o[1] + 2.325
        return [o[0] - 9.375, yc - 2.075, o[0] + 9.375, yc + 2.075]
    locator = next(it['geom'][2] for it in items if it['ref'] == 'J1' and it['kind'] == 'hole')
    j1_front = locator - 4.15  # HRO recommended layout: board edge 4.15 from the locator-hole line, on the shell-stake side
    j1_body = [j['J1'][0] - 4.47, j1_front, j['J1'][0] + 4.47, j1_front + 7.35]
    pad_env = envelopes(MB, ctx)
    over = {'J3': (union(pad_env['J3']['rect'], ghbody(j['J3'])), 'pad-bbox ∪ BM14B body 20.75x4.25'),
            'J2': (union(pad_env['J2']['rect'], ghbody(j['J2'])), 'pad-bbox ∪ BM14B body 20.75x4.25'),
            'J1': (union(pad_env['J1']['rect'], j1_body), 'pad-bbox ∪ HRO body 8.94x7.35 from recommended-layout edge datum')}
    env = envelopes(MB, ctx, over)
    board_rect = (bx0, by0, bx1, by1)
    mb_fills = {'In1.Cu': fill_polygons(MB, ctx, 'In1.Cu')}

    # ---- Pair 1
    out['pair1_boss'] = dict(
        boss_radius=2.25, reservation_radius=2.5, washer_radius=2.0,
        source='boss max phi4.5: docs/issue-150 §2 (proposal); phi4 POM washer/boss: docs/issue-163 (prototype size proposal); reservation: board keepouts',
        main=boss_checks('Main Rev.3', MB, minv, ctx, items, env, mb_fills))
    wing_out = {}
    for pitch, (inv, wb) in ctx['wings'].items():
        wi = board_items(wb, ctx)
        wj = ctx['wing_j'][pitch]
        wenv = envelopes(wb, ctx, {'J_WING': (union(envelopes(wb, ctx)['J_WING']['rect'], ghbody(wj)), 'pad-bbox ∪ BM14B body')})
        wing_out[str(pitch)] = boss_checks(f'Wing Rev.1 {pitch}mm', wb, inv, ctx, wi, wenv, {})
    out['pair1_boss']['wings'] = wing_out

    # ---- Pair 2: J3 support zones on both faces
    maps = {}
    zones = {}
    J3 = env['J3']['rect']
    regions = {
        'north_strip_full_width_Y70-79': ([bx0, by0, bx1, 79.0], 'N'),
        'north_strip_under_J3_span_X94.5-115.5_Y70-79': ([94.5, by0, 115.5, 79.0], 'N'),
        'east_zone_X115.5-124_Y70-92': ([115.5, by0, bx1, 92.0], 'E'),
        'east_edge_anchored_strip_X100-124_Y70-78.7': ([100.0, by0, bx1, 78.7], 'E'),
        'under_J3_body_X94.625-115.375_Y73.2-77.45': ([94.625, 73.2, 115.375, 77.45], None),
        'near_J3_any_X90-124_Y70-90': ([90.0, by0, bx1, 90.0], None),
        'near_J3_any_touching_north_or_east_edge_X90-124_Y70-90': None,
    }
    for margin in (0.0, 0.3):
        for face in 'FB':
            extra = [('r',) + tuple(e['rect']) for e in env.values() if e['face'] == face]
            extra += [('c', h['x'], h['y'], 2.25) for h in minv['holes'] if h['ref'].startswith('H')]  # case bosses are not contact zone
            gs = make_grid(board_rect, items, face, ('pad', 'tp', 'th', 'track', 'via', 'hole'), margin, 0.05, extra)
            gc = make_grid(board_rect, items, face, ('tp', 'th', 'via', 'hole'), margin, 0.05, extra)
            for nm, spec in regions.items():
                if spec is None:
                    continue
                zones.setdefault(f'margin{margin}', {}).setdefault(face, {})[nm] = dict(
                    all_obstacles=gs.largest(spec[0], spec[1]), components_testpads_vias_holes_only=gc.largest(spec[0], spec[1]))
            prof = gs.free_depth_profile([76, by0, 124, 80], 'N', 2.0)
            zones[f'margin{margin}'][face]['north_edge_free_depth_profile_per_2mm_column(x,depth)'] = prof
            e_prof = gs.free_depth_profile([100, by0, 124, 92], 'E', 2.0)
            zones[f'margin{margin}'][face]['east_edge_free_depth_profile_per_2mm_row(y,depth)'] = e_prof
    out['pair2_j3_zones'] = dict(grid_res_mm=0.05, phi4_5_case_bosses_excluded=True, margins_mm=[0.0, 0.3], J3_envelope_xy=J3, zones=zones)
    near = {}
    for face in 'FB':
        R = [90, by0, bx1, 90]
        cnt = {}
        for it in items:
            if it['face'] == face and overlaps(R, it['geom']):
                k = it['kind'] + (':' + it['ref'] if it['kind'] in ('pad', 'th', 'tp', 'hole') else '')
                cnt[k] = cnt.get(k, 0) + 1
        near[face] = dict(items_in_X90_124_Y70_90=dict(sorted(cnt.items())),
                          component_envelopes=sorted(r for r, e in env.items() if e['face'] == face and overlaps(R, ('r',) + tuple(e['rect']))))
    out['pair2_j3_zones']['obstacles_in_region'] = near
    for face in 'FB':
        maps[face] = ascii_map(board_rect, items, env, face, [88, 70, 124, 90], 1.0)

    # ---- Pair 3: GH housing envelopes (published GHR-14V-S 18.75x4.15x5.7, assembly ref 7.3) for J2/J3
    def housing_report(label, o, env_, items_, holes_, bounds):
        H = ghhousing(o)
        obst = {r: e['rect'] for r, e in env_.items() if e['face'] == 'F' and not r.startswith(('TP', 'H')) and r not in (label,)}
        ring = {}
        for m in (0.0, 0.5, 1.0, 2.0):
            ring[str(m)] = sorted(r for r, rc in obst.items() if rect_gap(rc, H) <= m)
        def gap(side):
            best = (None, None)
            bd_gap = {'N': H[1] - bounds[1], 'S': bounds[3] - H[3], 'W': H[0] - bounds[0], 'E': bounds[2] - H[2]}[side]
            best = (bd_gap, 'board edge')
            for r, rc in obst.items():
                if side in 'NS' and rc[0] < H[2] and rc[2] > H[0]:
                    g = H[1] - rc[3] if side == 'N' else rc[1] - H[3]
                elif side in 'EW' and rc[1] < H[3] and rc[3] > H[1]:
                    g = H[0] - rc[2] if side == 'W' else rc[0] - H[2]
                else:
                    continue
                if g >= 0 and g < best[0]:
                    best = (g, r)
            for h in holes_:
                hb = [h['x'] - 2.25, h['y'] - 2.25, h['x'] + 2.25, h['y'] + 2.25]
                if side in 'NS' and hb[0] < H[2] and hb[2] > H[0]:
                    g = H[1] - hb[3] if side == 'N' else hb[1] - H[3]
                elif side in 'EW' and hb[1] < H[3] and hb[3] > H[1]:
                    g = H[0] - hb[2] if side == 'W' else hb[0] - H[2]
                else:
                    continue
                if g >= 0 and g < best[0]:
                    best = (g, h['ref'] + ' boss phi4.5')
            return [rnd(best[0]), best[1]]
        tpg = sorted((rnd(rect_gap(e['rect'], H)), r) for r, e in env_.items() if r.startswith('TP') and e['face'] == 'F')[:2]
        boss = {h['ref']: rnd(circle_rect_gap((h['x'], h['y']), 2.25, H)) for h in holes_}
        bends = {}
        cx, cy = (H[0] + H[2]) / 2, (H[1] + H[3]) / 2
        for R in (3, 5, 8):
            reach = R + 0.5
            ends = {'N': cy - reach, 'S': cy + reach, 'W': cx - reach, 'E': cx + reach}
            bends[f'R{R}'] = dict(horizontal_reach_from_housing_center=reach,
                                  bend_end_to_board_edge_mm={'N': rnd(ends['N'] - bounds[1]), 'S': rnd(bounds[3] - ends['S']),
                                                             'W': rnd(ends['W'] - bounds[0]), 'E': rnd(bounds[2] - ends['E'])})
        return dict(housing_xy=H, board_edge_gap_mm={'N': rnd(H[1] - bounds[1]), 'S': rnd(bounds[3] - H[3]), 'W': rnd(H[0] - bounds[0]), 'E': rnd(bounds[2] - H[2])},
                    free_lateral_room_to_first_obstacle_mm=dict((s, gap(s)) for s in 'NSEW'),
                    components_within_gap_mm=ring, nearest_test_pads=tpg, harness_bend_end_vs_board_edge=bends, boss_4_5_to_housing_gap_mm=boss)
    mh = [h for h in minv['holes'] if h['ref'].startswith('H')]
    out['pair3_gh_housing'] = dict(
        published=dict(GHR_14V_S=dict(width=18.75, depth=4.15, height=5.7, assembled_height_ref=7.3, wire_od=[0.76, 1.0]),
                       BM14B=dict(width=20.75, depth=4.25, height=4.05, mated_height=5.7), source='JST GH catalog via docs/issue-160 §2 and docs/issue-150 §7'),
        assumption='housing centred on header body (#163); actual latch datum unknown',
        J3=housing_report('J3', j['J3'], env, items, mh, minv['bounds_xy_mm']),
        J2=housing_report('J2', j['J2'], env, items, mh, minv['bounds_xy_mm']),
        service_rectangle_26x7_5={'rect': [92, 71.5, 118, 79], 'pads_overlapping': ctx['mech']['pads_overlapping_service_rect']})

    # ---- Pair 4: J1 USB-C
    ov_w, ov_h, shell_len = 12.35, 6.5, 6.65
    pad = 0.5
    tunnel = [j['J1'][0] - ov_w / 2 - pad, by0, j['J1'][0] + ov_w / 2 + pad, j1_front]
    hits = {}
    for face in 'FB':
        hits[face] = sorted({it['kind'] + ':' + it['ref'] for it in items if it['face'] == face and overlaps(tunnel, it['geom'])})
    benv = sorted(r for r, e in env.items() if r != 'J1' and e['face'] == 'F' and overlaps(tunnel, ('r',) + tuple(e['rect'])))
    by_width = {}
    for w in (8.25, 8.94, 12.35):
        T = [j['J1'][0] - w / 2, by0, j['J1'][0] + w / 2, j1_front]
        by_width[str(w)] = sorted(r for r, e in env.items() if r != 'J1' and e['face'] == 'F' and overlaps(T, ('r',) + tuple(e['rect'])))
    out['pair4_usbc'] = dict(
        component_envelopes_in_strip_by_width_without_clearance=by_width,
        envelope_xy_of_those_components={r: [rnd(v) for v in env[r]['rect']] for r in sorted({x for v in by_width.values() for x in v})},
        J1_xy=j['J1'], locator_y=rnd(locator), receptacle_front_face_y=rnd(j1_front), receptacle_body_xy=j1_body,
        front_face_source='HRO TYPE-C-31-M-12 recommended layout: board edge 4.15 from locator line (hardware/jitx/geometry/EDA-002C3.md:121-140; view mapping flagged SOURCE_AMBIGUITY there)',
        shell_stake_north_end_y=rnd(min(it['geom'][1] - 0 for it in items if it['ref'] == 'J1' and it['kind'] == 'th') if False else min(bbox(it['geom'])[1] for it in items if it['ref'] == 'J1' and it['kind'] == 'th' and it['face'] == 'F')),
        depth_from_north_edge_to_front_face=rnd(j1_front - by0),
        published_usbc=dict(overmold_max_w=ov_w, overmold_max_h=ov_h, shell_w=8.25, shell_h=2.4, shell_len_min=shell_len, receptacle_opening=[8.34, 2.56],
                            source='USB-IF Type-C recommended values as cited by Amphenol Socapex FAQ / accesscomms; primary spec not re-fetched'),
        overmold_tunnel_xy=tunnel, tunnel_width_with_0_5_each_side=rnd(tunnel[2] - tunnel[0]),
        tunnel_to_west_edge=rnd(tunnel[0] - bx0), tunnel_to_east_edge=rnd(bx1 - tunnel[2]),
        items_in_tunnel_over_board=hits, component_envelopes_in_tunnel=benv,
        nose_tip_if_overmold_stops_at_board_edge_y=rnd(by0 + shell_len), nose_shortfall_to_front_face=rnd(j1_front - (by0 + shell_len)),
        overmold_front_must_reach_y_for_full_insertion_approx=rnd(j1_front),
        axis_height_required_for_overmold_clearing_pcb_top=ov_h / 2,
        case_tunnel_depth_from_outer_wall=rnd(j1_front - by0 + 2.0 + 0.5),
        wall_and_gap_basis='initial values wall 2.0 + clearance 0.5 from docs/issue-150 §6 (proposal, not a design)')

    # ---- Pair 5: Wing top side
    keyrows = ctx['rows']
    p5 = {}
    for pitch, (inv, wb) in ctx['wings'].items():
        wi = board_items(wb, ctx)
        wj = ctx['wing_j'][pitch]
        base = envelopes(wb, ctx)
        wenv = envelopes(wb, ctx, {'J_WING': (union(base['J_WING']['rect'], ghbody(wj)), 'pad-bbox ∪ BM14B body')})
        wr = inv['bounds_xy_mm']
        Hh = ghhousing(wj)
        rows = [r for r in keyrows if r['pitch_mm'] == pitch]
        holes = [h for h in inv['holes'] if h['ref'].startswith('H')]
        res = {}
        # free zones on both faces
        zres = {}
        for face in 'FB':
            extra = [('r',) + tuple(e['rect']) for e in wenv.values() if e['face'] == face]
            gs = make_grid(tuple(wr), wi, face, ('pad', 'tp', 'th', 'track', 'via', 'hole'), 0.0, 0.1, extra)
            gc = make_grid(tuple(wr), wi, face, ('tp', 'th', 'via', 'hole'), 0.0, 0.1, extra)
            d = {}
            for nm, g in (('all_obstacles', gs), ('components_testpads_vias_holes_only', gc)):
                d[nm] = dict(largest_free_rect=g.largest(list(wr)),
                             edge_anchored={a: g.largest(list(wr), a) for a in 'NSEW'},
                             uniform_free_strip_width_mm={
                                 a: min(v[1] for v in g.free_depth_profile(
                                     [wr[0], wr[1], wr[2], wr[3]], a, 1.0)) for a in 'NSEW'})
            zres[face] = d
        res['free_zones_grid_0_1mm'] = zres
        # key envelopes
        sq = lambda r, w: [r['x_mm'] - w / 2, r['y_mm'] - w / 2, r['x_mm'] + w / 2, r['y_mm'] + w / 2]
        env158 = [sq(r, 15.8) for r in rows]
        all_keys = [r['sensor'] for r in rows]
        under = {}
        for r, E in zip(rows, env158):
            for ref, e in wenv.items():
                if ref == r['sensor'] or e['face'] != 'F':
                    continue
                if overlaps(E, ('r',) + tuple(e['rect'])):
                    under.setdefault(ref.split('_')[0] + '_' + (ref.split('_')[1][:2] if '_' in ref else ''), set()).add(ref)
        under_cnt = {k: sorted(v) for k, v in under.items()}
        kb = [min(E[0] for E in env158), min(E[1] for E in env158), max(E[2] for E in env158), max(E[3] for E in env158)]
        in_bbox = sorted(r for r, e in wenv.items() if e['face'] == 'F' and overlaps(kb, ('r',) + tuple(e['rect'])) and not r.startswith(('U_H', 'C_H', 'TP')))
        tp_in_bbox = sorted(r for r, e in wenv.items() if r.startswith('TP') and overlaps(kb, ('r',) + tuple(e['rect'])))
        def tp_class(e):
            cx, cy = (e[0] + e[2]) / 2, (e[1] + e[3]) / 2
            inside = [E for E in env158 if E[0] <= cx <= E[2] and E[1] <= cy <= E[3]]
            body = [r_ for r_ in rows if abs(r_['x_mm'] - cx) <= 7.0 and abs(r_['y_mm'] - cy) <= 7.0]
            return 'center_under_switch_15.8' if inside else ('partial_overlap_15.8' if any(overlaps(E, ('r',) + tuple(e)) for E in env158) else 'outside')
        tp_cls = {}
        for r_, e in wenv.items():
            if r_.startswith('TP'):
                tp_cls.setdefault(tp_class(e['rect']), []).append(r_)
        edge_gap = min(min(E[0] - wr[0], E[1] - wr[1], wr[2] - E[2], wr[3] - E[3]) for E in env158)
        boss_gap = {h['ref']: rnd(min(circle_rect_gap((h['x'], h['y']), 2.25, E) for E in env158)) for h in holes}
        svc = {'16': [50, 139, 76, 147], '17': [46.75, 141.375, 72.75, 149.375]}[str(pitch)]
        res['keys'] = dict(
            test_pads_by_switch_overlap={k: sorted(v) for k, v in tp_cls.items()},
            n=len(rows), envelope_15_8_bbox_xy=[rnd(v) for v in kb], min_env15_8_to_board_edge=rnd(edge_gap),
            min_env15_8_edge_to_boss_4_5=boss_gap,
            min_env15_8_to_J_WING_housing=rnd(min(rect_gap(E, Hh) for E in env158)),
            min_env15_8_to_service_rect_26x8=rnd(min(rect_gap(E, svc) for E in env158)),
            service_rect_xy=svc, J_WING_housing_xy=[rnd(v) for v in Hh],
            J_WING_housing_overlaps_key_bbox=overlaps(kb, ('r',) + tuple(Hh)),
            components_under_15_8_squares_other_than_own_sensor=under_cnt,
            non_sensor_non_cap_non_TP_components_overlapping_key_bbox=in_bbox, test_pads_overlapping_key_bbox=tp_in_bbox,
            key_bbox_gap_to_J_WING_body=rnd(rect_gap(kb, wenv['J_WING']['rect'])),
            key_bbox_gap_to_mux_envelopes=rnd(min(rect_gap(kb, e['rect']) for r, e in wenv.items() if r.startswith('U_MUX'))))
        # keep-away of key bounding box from the 4 boss circles in plan
        p5[str(pitch)] = res
    zdt = dict(plate_support_surface_H=10.0, plate_thickness=1.5, plate_underside=8.5,
               switch_support_to_bottom=5.0, switch_below_seat_protrusion_max=2.8, switch_seat_depth_conservative=5.05,
               sensor_top=1.12, sensor_float_budget=0.10, H_tolerance=0.15, travel_nominal=3.5, travel_tol=0.2,
               source='docs/issue-150 §3, §5, §6 (design proposal values)')
    zdt['switch_lowest_z_nominal'] = rnd(zdt['plate_support_surface_H'] - 5.05 - 2.8)
    zdt['switch_lowest_z_at_H_min'] = rnd(zdt['plate_support_surface_H'] - 0.15 - 5.05 - 2.8)
    zdt['sensor_top_z_with_float'] = rnd(1.12 + 0.10)
    zdt['switch_lowest_to_sensor_top_gap_min_unpressed'] = rnd(zdt['switch_lowest_z_at_H_min'] - zdt['sensor_top_z_with_float'])
    zdt['plate_underside_to_sensor_top'] = rnd(8.5 - 1.22)
    zdt['plate_underside_to_mated_GH_ref_7_3'] = rnd(8.5 - 7.3)
    zdt['switch_top_above_support_published'] = rnd(11.10 - 5.00)
    zdt['switch_top_z_nominal'] = rnd(10.0 + 11.10 - 5.00)
    zdt['max_press_travel'] = 3.7
    out['pair5_wing_top'] = dict(vertical=zdt, wings=p5)
    return out, maps
