"""Windowed 2-layer grid A* stub router for the issue-288 PCB build.

Pad obstacles use exact signed distances to the pad shape (rect / circle /
oval, rotation-aware — the same metric as the repo's via-pad audit), so
real corridors between long thin pads stay visible to the search.
Obstacles are bucket-indexed (4 mm cells) for full-board windows.
"""
import heapq
import math

import pcbnew

MM = 1e6
GRID = 0.25
CLEAR = 0.10
CELL = 4.0


def _seg_dist(px, py, ax, ay, bx, by):
    dx, dy = bx - ax, by - ay
    L2 = dx * dx + dy * dy
    if L2 == 0:
        return math.hypot(px - ax, py - ay)
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
    return math.hypot(px - (ax + t * dx), py - (ay + t * dy))


def _pad_signed_dist(pad, px, py):
    """Signed distance from point to pad copper (pad = Obstacles pad tuple)."""
    (cx, cy, w, h, shape, cos_t, sin_t, _nc, _f, _b) = pad
    dx, dy = px - cx, py - cy
    x = dx * cos_t - dy * sin_t
    y = dx * sin_t + dy * cos_t
    if shape == 'rect':
        a, c = abs(x) - w / 2, abs(y) - h / 2
        return math.hypot(max(a, 0), max(c, 0)) + min(max(a, c), 0)
    if shape == 'circle':
        return math.hypot(x, y) - w / 2
    # oval
    return math.hypot(max(abs(x) - max(w - h, 0) / 2, 0),
                      max(abs(y) - max(h - w, 0) / 2, 0)) - min(w, h) / 2


class Obstacles:
    """Board-wide obstacles with 4mm bucket indexes per category."""

    def __init__(self, board):
        self.pads = []
        self.segs = []
        self.vias = []
        self.bbox = None
        self.pad_b = {}
        self.seg_b = {}
        self.via_b = {}
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                p = pad.GetPosition()
                sz = pad.GetSize()
                shape_id = pad.GetShape()
                shape = {pcbnew.PAD_SHAPE_RECT: 'rect', pcbnew.PAD_SHAPE_CIRCLE: 'circle',
                         pcbnew.PAD_SHAPE_OVAL: 'oval'}.get(shape_id, 'rect')
                # PAD::GetOrientationDegrees() is already absolute (verified)
                th = math.radians(pad.GetOrientationDegrees())
                layers = pad.GetLayerSet()
                thru = pad.GetDrillSize().x > 0
                entry = (p.x / MM, p.y / MM, sz.x / MM, sz.y / MM, shape,
                         math.cos(th), math.sin(th), pad.GetNetCode(),
                         thru or layers.Contains(pcbnew.F_Cu),
                         thru or layers.Contains(pcbnew.B_Cu))
                self.pads.append(entry)
                self._put(self.pad_b, entry[0], entry[1], len(self.pads) - 1)
        for t in board.GetTracks():
            nc = t.GetNetCode()
            if isinstance(t, pcbnew.PCB_VIA):
                p = t.GetPosition()
                e = (p.x / MM, p.y / MM, t.GetWidth(pcbnew.F_Cu) / 2 / MM, nc)
                self.vias.append(e)
                self._put(self.via_b, e[0], e[1], len(self.vias) - 1)
            else:
                a, bb = t.GetStart(), t.GetEnd()
                layer = 0 if t.GetLayer() == pcbnew.F_Cu else 1
                e = (a.x / MM, a.y / MM, bb.x / MM, bb.y / MM,
                     t.GetWidth() / 2 / MM, nc, layer)
                self.segs.append(e)
                n = max(1, int(math.hypot(e[2] - e[0], e[3] - e[1]) / 3.0))
                for k in range(n + 1):
                    self._put(self.seg_b, e[0] + (e[2] - e[0]) * k / n,
                              e[1] + (e[3] - e[1]) * k / n, len(self.segs) - 1)
        self.holes = []
        self.hole_b = {}
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                dr = pad.GetDrillSize().x / MM
                if dr > 0:
                    p = pad.GetPosition()
                    e = (p.x / MM, p.y / MM, dr / 2, pad.GetNetCode())
                    self.holes.append(e)
                    self._put(self.hole_b, e[0], e[1], len(self.holes) - 1)
        edges = [d for d in board.GetDrawings() if d.GetLayer() == pcbnew.Edge_Cuts]
        xs, ys = [], []
        for d in edges:
            bb2 = d.GetBoundingBox()
            xs += [bb2.GetLeft() / MM, bb2.GetRight() / MM]
            ys += [bb2.GetTop() / MM, bb2.GetBottom() / MM]
        if xs:
            self.bbox = (min(xs), min(ys), max(xs), max(ys))

    @staticmethod
    def _put(index, x, y, i):
        index.setdefault((int(x // CELL), int(y // CELL)), []).append(i)

    @staticmethod
    def _near(index, x, y):
        out = set()
        ci, cj = int(x // CELL), int(y // CELL)
        for di in (-1, 0, 1):
            for dj in (-1, 0, 1):
                out.update(index.get((ci + di, cj + dj), ()))
        return out

    def blocked(self, x, y, layer, netcode, my_half, via=False):
        need = CLEAR + (0.30 if via else my_half)
        for i in self._near(self.pad_b, x, y):
            pad = self.pads[i]
            if pad[7] == netcode:
                continue
            if layer == 0 and not pad[8]:
                continue
            if layer == 1 and not pad[9]:
                continue
            if _pad_signed_dist(pad, x, y) < need:
                return True
        for i in self._near(self.seg_b, x, y):
            (ax, ay, bx, by, hw, nc, lay) = self.segs[i]
            if nc == netcode or lay != layer:
                continue
            if _seg_dist(x, y, ax, ay, bx, by) < hw + need:
                return True
        if via:
            # hole clearance: via copper radius 0.30 + hole radius + 0.20 rule
            for i in self._near(self.hole_b, x, y):
                (hx, hy, hr, hnc) = self.holes[i]
                if hnc == netcode:
                    continue
                if math.hypot(x - hx, y - hy) < 0.30 + hr + 0.20 + 0.03:
                    return True
        vr = 0.30 if via else my_half
        for i in self._near(self.via_b, x, y):
            (vx, vy, r, nc) = self.vias[i]
            if nc == netcode:
                continue
            if math.hypot(x - vx, y - vy) < r + CLEAR + vr:
                return True
        if self.bbox:
            m = CLEAR + my_half + 0.02
            if x < self.bbox[0] + m or x > self.bbox[2] - m or y < self.bbox[1] + m or y > self.bbox[3] - m:
                return True
        return False

    def add_seg(self, ax, ay, bx, by, halfwidth, netcode, layer):
        e = (ax, ay, bx, by, halfwidth, netcode, layer)
        self.segs.append(e)
        n = max(1, int(math.hypot(bx - ax, by - ay) / 3.0))
        for k in range(n + 1):
            self._put(self.seg_b, ax + (bx - ax) * k / n, ay + (by - ay) * k / n,
                      len(self.segs) - 1)

    def add_via(self, x, y, r, netcode):
        self.vias.append((x, y, r, netcode))
        self._put(self.via_b, x, y, len(self.vias) - 1)


def _seg_clear(obs, ax, ay, bx, by, layer, netcode, my_half):
    steps = max(2, int(math.hypot(bx - ax, by - ay) / 0.1))
    for k in range(steps + 1):
        t = k / steps
        if obs.blocked(ax + (bx - ax) * t, ay + (by - ay) * t, layer, netcode, my_half):
            return False
    return True


def _astar(obs, start, end, netcode, width, x0, x1, y0, y1):
    my_half = width / 2
    sx, sy, sl = start
    ex, ey, el = end
    nx = int((x1 - x0) / GRID) + 1
    ny = int((y1 - y0) / GRID) + 1
    if nx * ny > 420_000:
        return None

    def cell_of(x, y):
        return (int(round((x - x0) / GRID)), int(round((y - y0) / GRID)))

    def xy_of(i, j):
        return (x0 + i * GRID, y0 + j * GRID)

    si, sj = cell_of(sx, sy)
    ei, ej = cell_of(ex, ey)
    start_state = (si, sj, sl)
    goal_cells = {(ei, ej, el)}

    def heuristic(i, j, l):
        return math.hypot(i - ei, j - ej) + (0 if l == el else 3)

    open_heap = [(heuristic(si, sj, sl), 0.0, start_state)]
    came = {start_state: None}
    gscore = {start_state: 0.0}
    DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
            (1, 1, 1.414), (1, -1, 1.414), (-1, 1, 1.414), (-1, -1, 1.414)]
    found = None
    while open_heap:
        _, g, state = heapq.heappop(open_heap)
        if g > gscore.get(state, 1e18) + 1e-9:
            continue
        if state in goal_cells:
            found = state
            break
        i, j, l = state
        x, y = xy_of(i, j)
        for di, dj, cost in DIRS:
            ni, nj = i + di, j + dj
            if not (0 <= ni < nx and 0 <= nj < ny):
                continue
            nstate = (ni, nj, l)
            if nstate in came and gscore.get(nstate, 1e18) <= g + cost:
                continue
            px, py = xy_of(ni, nj)
            if nstate not in goal_cells and obs.blocked(px, py, l, netcode, my_half):
                continue
            came[nstate] = state
            gscore[nstate] = g + cost
            heapq.heappush(open_heap, (g + cost + heuristic(ni, nj, l), g + cost, nstate))
        nstate = (i, j, 1 - l)
        if not (nstate in came and gscore.get(nstate, 1e18) <= g + 4):
            if not obs.blocked(x, y, 0, netcode, 0.30, via=True) and \
               not obs.blocked(x, y, 1, netcode, 0.30, via=True):
                came[nstate] = state
                gscore[nstate] = g + 4
                heapq.heappush(open_heap, (g + 4 + heuristic(i, j, 1 - l), g + 4, nstate))
    if found is None:
        return None
    path = []
    st = found
    while st is not None:
        i, j, l = st
        x, y = xy_of(i, j)
        path.append((x, y, l))
        st = came[st]
    path.reverse()
    path[0] = (sx, sy, sl)
    path[-1] = (ex, ey, el)
    out = [path[0]]
    via_pts = []
    k = 0
    while k < len(path) - 1:
        cur = path[k]
        nxt = path[k + 1]
        if nxt[2] != cur[2]:
            via_pts.append((cur[0], cur[1]))
            out.append(nxt)
            k += 1
            continue
        best = k + 1
        for m in range(k + 2, len(path)):
            if path[m][2] != cur[2]:
                break
            if _seg_clear(obs, cur[0], cur[1], path[m][0], path[m][1], cur[2], netcode, my_half):
                best = m
            else:
                break
        out.append(path[best])
        k = best
    return out, via_pts


def route(obs, start, end, netcode, width, layers=(0, 1)):
    """A* between start/end (x, y, layer); distance-scaled window, then a
    full-board retry. Returns (points, via_points) or None."""
    sx, sy, _ = start
    ex, ey, _ = end
    dist = math.hypot(ex - sx, ey - sy)
    margin = max(5.0, 0.75 * dist)
    x0 = min(sx, ex) - margin
    x1 = max(sx, ex) + margin
    y0 = min(sy, ey) - margin
    y1 = max(sy, ey) + margin
    if obs.bbox:
        x0 = max(x0, obs.bbox[0] + 0.2)
        y0 = max(y0, obs.bbox[1] + 0.2)
        x1 = min(x1, obs.bbox[2] - 0.2)
        y1 = min(y1, obs.bbox[3] - 0.2)
    res = _astar(obs, start, end, netcode, width, x0, x1, y0, y1)
    if res is None and obs.bbox:
        res = _astar(obs, start, end, netcode, width,
                     obs.bbox[0] + 0.2, obs.bbox[2] - 0.2,
                     obs.bbox[1] + 0.2, obs.bbox[3] - 0.2)
    return res


def add_route(board, net, width, points, via_pts):
    netcode = net.GetNetCode() if hasattr(net, 'GetNetCode') else net
    layer_ids = [pcbnew.F_Cu, pcbnew.B_Cu]
    for (ax, ay, al), (bx, by, bl) in zip(points, points[1:]):
        if al != bl:
            continue
        if math.hypot(bx - ax, by - ay) < 1e-6:
            continue
        t = pcbnew.PCB_TRACK(board)
        t.SetStart(pcbnew.VECTOR2I(int(ax * MM), int(ay * MM)))
        t.SetEnd(pcbnew.VECTOR2I(int(bx * MM), int(by * MM)))
        t.SetWidth(int(width * MM))
        t.SetLayer(layer_ids[al])
        t.SetNetCode(netcode)
        board.Add(t)
    for (x, y) in via_pts:
        v = pcbnew.PCB_VIA(board)
        v.SetPosition(pcbnew.VECTOR2I(int(x * MM), int(y * MM)))
        v.SetWidth(int(0.60 * MM))
        v.SetDrill(int(0.30 * MM))
        v.SetLayerPair(pcbnew.F_Cu, pcbnew.B_Cu)
        v.SetNetCode(netcode)
        board.Add(v)
