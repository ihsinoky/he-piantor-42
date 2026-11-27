#!/usr/bin/env python3
"""Via-stitch repair for B.Cu-sealed GND islands (Issue #299).

Per island: pick a new GND via A whose annulus overlaps the island's
B.Cu copper, a new GND via B whose annulus overlaps return B.Cu
copper, and route an F.Cu GND track A->B.  All new copper is GND net.
Clearances: >=0.100 mm to other-net copper on both layers; via edge to
other-net pads >= the variant's Gate-4 floor; new via centres >=0.55
from existing via centres and >= hole_r+0.40 from NPTH hole centres.
If the island already owns a via, its F.Cu copper is a free start.

Usage: stitch.py <in.kicad_pcb> <out.kicad_pcb> <gate4_floor_mm>
Run route.py first (B.Cu bridges), then this on the result."""
import sys, os, json, math, heapq
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
from shapely.geometry import Point, LineString, box
from shapely.ops import unary_union
from shapely.strtree import STRtree
import gndcheck as gc
import survey2

NM = 1e6
FCU, BCU = pcbnew.F_Cu, pcbnew.B_Cu
CLR = 0.100
EPS = 0.004
VIA_D, VIA_DRILL = 0.60, 0.30

def other_geoms(board, layer):
    out = []
    for t in board.GetTracks():
        if t.GetNetname() == "GND" or not t.IsOnLayer(layer):
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            pos = t.GetPosition()
            out.append((Point(pos.x / NM, pos.y / NM).buffer(t.GetWidth(layer) / NM / 2.0, resolution=24),
                        "via"))
        else:
            s, e = t.GetStart(), t.GetEnd()
            out.append((LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)]).buffer(
                t.GetWidth() / NM / 2.0, cap_style=1, resolution=8), "track"))
    for zone in board.Zones():
        if zone.GetNetname() in ("GND", "") or not zone.IsOnLayer(layer):
            continue
        for p in gc.polys_from_set(zone.GetFilledPolysList(layer)):
            out.append((p, "zonefill"))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() in ("GND", "") or not pad.IsOnLayer(layer):
                continue
            out.append((gc.pad_geom(pad, layer), "pad"))
    return out

class ViaCheck:
    def __init__(self, board, floor):
        self.floor = floor
        self.obs = {}
        self.trees = {}
        for layer in (FCU, BCU):
            o = other_geoms(board, layer)
            self.obs[layer] = o
            self.trees[layer] = STRtree([g for g, k in o]) if o else None
        self.vias = []
        for t in board.GetTracks():
            if t.Type() == pcbnew.PCB_VIA_T:
                pos = t.GetPosition()
                self.vias.append((pos.x / NM, pos.y / NM))
        self.holes = []
        for fp in board.GetFootprints():
            for pad in fp.Pads():
                if pad.GetAttribute() == pcbnew.PAD_ATTRIB_NPTH:
                    ds = pad.GetDrillSize()
                    pos = pad.GetPosition()
                    self.holes.append((pos.x / NM, pos.y / NM, ds.x / NM / 2.0))
    def ok(self, x, y, target_bcu):
        disc = Point(x, y).buffer(VIA_D / 2.0, resolution=24)
        if disc.intersection(target_bcu).area < 0.02:
            return False
        probe = disc.buffer(self.floor)
        for layer in (FCU, BCU):
            tree = self.trees[layer]
            if tree is None:
                continue
            for gi in tree.query(probe, predicate="intersects"):
                g, kind = self.obs[layer][gi]
                req = self.floor if kind == "pad" else CLR
                if disc.distance(g) < req - 1e-9:
                    return False
        for (vx, vy) in self.vias:
            if math.hypot(vx - x, vy - y) < 0.55:
                return False
        for (hx, hy, hr) in self.holes:
            if math.hypot(hx - x, hy - y) < hr + VIA_DRILL / 2.0 + 0.25:
                return False
        return True

def sample_candidates(check, target_geom, window, step=0.05):
    """Grid-sample centres within `window` whose disc could overlap
    target_geom, validity-checked."""
    local = target_geom.intersection(window)
    if local.is_empty:
        return []
    out = []
    minx, miny, maxx, maxy = local.bounds
    y = miny
    while y <= maxy + 1e-9:
        x = minx
        while x <= maxx + 1e-9:
            if local.distance(Point(x, y)) <= VIA_D / 2.0:
                if check.ok(x, y, target_geom):
                    out.append((x, y))
            x += step
        y += step
    return out

def grid_astar(starts, goals, obstacles, width, res=0.025, margin=1.5, goal_clip=None):
    if goal_clip is not None:
        goals = goals.intersection(goal_clip)
        if goals.is_empty:
            return None
    dil = CLR + width / 2.0 + EPS
    minx = min(starts.bounds[0], goals.bounds[0]) - margin
    miny = min(starts.bounds[1], goals.bounds[1]) - margin
    maxx = max(starts.bounds[2], goals.bounds[2]) + margin
    maxy = max(starts.bounds[3], goals.bounds[3]) + margin
    nx = int((maxx - minx) / res) + 1
    ny = int((maxy - miny) / res) + 1
    if nx * ny > 2_500_000:
        return None
    blocked = bytearray(nx * ny)
    for ob in obstacles:
        b = ob.bounds
        if b[2] < minx or b[0] > maxx or b[3] < miny or b[1] > maxy:
            continue
        i0 = max(0, int((b[0] - dil - minx) / res) - 1)
        i1 = min(nx - 1, int((b[2] + dil - minx) / res) + 1)
        j0 = max(0, int((b[1] - dil - miny) / res) - 1)
        j1 = min(ny - 1, int((b[3] + dil - miny) / res) + 1)
        for j in range(j0, j1 + 1):
            y = miny + j * res
            for i in range(i0, i1 + 1):
                if ob.distance(Point(minx + i * res, y)) < dil:
                    blocked[j * nx + i] = 1
    start_cells, goal_cells = [], set()
    for j in range(ny):
        for i in range(nx):
            p = Point(minx + i * res, miny + j * res)
            if starts.contains(p):
                start_cells.append((i, j))
            if goals.contains(p):
                goal_cells.add((i, j))
    if not start_cells or not goal_cells:
        return None
    gscore = {s: 0.0 for s in start_cells}
    came = {}
    openh = [(0.0, s) for s in start_cells]
    heapq.heapify(openh)
    found = None
    while openh:
        f, cur = heapq.heappop(openh)
        if cur in goal_cells:
            found = cur
            break
        ci, cj = cur
        for di, dj, cost in ((1, 0, 1), (-1, 0, 1), (0, 1, 1), (0, -1, 1),
                             (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)),
                             (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))):
            ni, nj = ci + di, cj + dj
            if not (0 <= ni < nx and 0 <= nj < ny) or blocked[nj * nx + ni]:
                continue
            if di and dj and (blocked[cj * nx + ni] or blocked[nj * nx + ci]):
                continue
            ng = gscore[cur] + cost * res
            if ng < gscore.get((ni, nj), 1e18):
                gscore[(ni, nj)] = ng
                came[(ni, nj)] = cur
                h = goals.distance(Point(minx + ni * res, miny + nj * res))
                heapq.heappush(openh, (ng + h, (ni, nj)))
    if found is None:
        return None
    path = [found]
    while path[-1] in came:
        path.append(came[path[-1]])
    path.reverse()
    return [(minx + i * res, miny + j * res) for (i, j) in path]

def simplify(pts, obs_union, width):
    if len(pts) <= 2:
        return pts
    out = [pts[0]]
    i = 0
    while i < len(pts) - 1:
        j = len(pts) - 1
        while j > i + 1:
            seg = LineString([pts[i], pts[j]]).buffer(width / 2.0, cap_style=1, resolution=8)
            if obs_union is None or seg.distance(obs_union) >= CLR - 0.001:
                break
            j -= 1
        out.append(pts[j])
        i = j
    return out

def add_via(board, x, y, gnd_code):
    v = pcbnew.PCB_VIA(board)
    v.SetPosition(pcbnew.VECTOR2I(int(round(x * NM)), int(round(y * NM))))
    try:
        v.SetViaType(pcbnew.VIATYPE_THROUGH)
    except Exception:
        pass
    v.SetWidth(int(round(VIA_D * NM)))
    if hasattr(v, "SetDrillValue"):
        v.SetDrillValue(int(round(VIA_DRILL * NM)))
    else:
        v.SetDrill(int(round(VIA_DRILL * NM)))
    v.SetLayerPair(FCU, BCU)
    v.SetNetCode(gnd_code)
    board.Add(v)

def add_track(board, a, b, w, layer, gnd_code):
    t = pcbnew.PCB_TRACK(board)
    t.SetStart(pcbnew.VECTOR2I(int(round(a[0] * NM)), int(round(a[1] * NM))))
    t.SetEnd(pcbnew.VECTOR2I(int(round(b[0] * NM)), int(round(b[1] * NM))))
    t.SetWidth(int(round(w * NM)))
    t.SetLayer(layer)
    t.SetNetCode(gnd_code)
    board.Add(t)

def main():
    inp, outp, floor = sys.argv[1], sys.argv[2], float(sys.argv[3])
    board = pcbnew.LoadBoard(inp)
    gnd_code = None
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == "GND":
                gnd_code = pad.GetNetCode()
    results = []
    for attempt in range(10):
        objs, find, pad_objs = survey2.build(board)
        jw_root = find(objs.index(pad_objs["J_WING.2"][0]))
        groups = {}
        for name, olist in pad_objs.items():
            groups.setdefault(find(objs.index(olist[0])), []).append(name)
        islands = {r: ns for r, ns in groups.items() if r != jw_root}
        if not islands:
            break
        def root_geom(root, layer):
            gs = [o["geom"] for i, o in enumerate(objs) if find(i) == root and o["layer"] == layer]
            return unary_union(gs) if gs else None
        ret_b = root_geom(jw_root, BCU)
        ret_f = root_geom(jw_root, FCU)
        check = ViaCheck(board, floor)
        f_obs = [g for g, k in check.obs[FCU]]
        f_union = unary_union(f_obs) if f_obs else None
        placed_any = False
        for root, names in sorted(islands.items(), key=lambda kv: sorted(kv[1])):
            isl_b = root_geom(root, BCU)
            isl_f = root_geom(root, FCU)
            bb = isl_b.bounds
            candA = sample_candidates(check, isl_b,
                                      box(bb[0] - 0.5, bb[1] - 0.5, bb[2] + 0.5, bb[3] + 0.5))
            candB = sample_candidates(check, ret_b,
                                      box(bb[0] - 7, bb[1] - 7, bb[2] + 7, bb[3] + 7))
            if not candB:
                print(f"island {names}: no valid via-B site", file=sys.stderr)
                continue
            cx, cy = isl_b.representative_point().x, isl_b.representative_point().y
            candA.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
            candB.sort(key=lambda p: math.hypot(p[0] - cx, p[1] - cy))
            starts = []
            if isl_f is not None and not isl_f.is_empty:
                starts.append(isl_f)
            placed = None
            for w in (0.30, 0.20, 0.10):
                starts_w = list(starts)
                for (ax, ay) in candA[:14]:
                    starts_w.append(Point(ax, ay).buffer(VIA_D / 2.0, resolution=16))
                if not starts_w:
                    break
                start_union = unary_union(starts_w)
                # goal type 1: existing return F.Cu copper (clipped near island)
                if ret_f is not None and not ret_f.is_empty:
                    clip = box(bb[0] - 10, bb[1] - 10, bb[2] + 10, bb[3] + 10)
                    path = grid_astar(start_union, ret_f, f_obs, w, goal_clip=clip)
                    if path:
                        placed = (w, path, None)
                # goal type 2: a new via B over return B.Cu copper
                if not placed:
                    for (bx, by) in candB[:14]:
                        goal = Point(bx, by).buffer(VIA_D / 2.0, resolution=16)
                        path = grid_astar(start_union, goal, f_obs, w)
                        if path:
                            placed = (w, path, (bx, by))
                            break
                if placed:
                    break
            if not placed:
                print(f"island {names}: no stitch found", file=sys.stderr)
                continue
            w, path, b_used = placed
            path = simplify(path, f_union, w)
            p0 = Point(path[0])
            a_used = None
            for (ax, ay) in candA[:14]:
                if p0.distance(Point(ax, ay)) <= VIA_D / 2.0 + 0.03:
                    a_used = (ax, ay)
                    break
            if a_used:
                add_via(board, a_used[0], a_used[1], gnd_code)
            if b_used:
                add_via(board, b_used[0], b_used[1], gnd_code)
            for a, b in zip(path, path[1:]):
                add_track(board, a, b, w, FCU, gnd_code)
            results.append({"pads": sorted(names),
                            "via_a": list(a_used) if a_used else "existing-island-copper",
                            "via_b": list(b_used) if b_used else "existing-return-F.Cu",
                            "f_track_width": w,
                            "path": [[round(x, 3), round(y, 3)] for x, y in path]})
            placed_any = True
            break  # rebuild state before the next island
        if not placed_any:
            break
    pcbnew.SaveBoard(outp, board)
    print(json.dumps({"stitches": results}, indent=1))

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    main()
