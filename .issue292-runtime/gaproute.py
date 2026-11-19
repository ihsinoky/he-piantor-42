"""Gap router: A* on a 0.05mm raster over the CURRENT board.
Obstacles = all copper not in the target net (pads as rotated rects,
tracks, vias, refilled zone fills), inflated by clearance + w/2.
In-field cells (MODULE_FIELD_FINE rect) use the field clearance.
Vias: centre tested against obstacles inflated by via_r + clearance
on F/I2/B, plus via-via centre distance >= 0.85, outside antenna
strip, inside outline. Start/goal = the two components of the target
net identified by hint points.
Usage: gaproute.py <board> <job.json> <out.json>
job: {net, width, region:[x0,y0,x1,y1], layers:["F","I2","B"],
      start:[x,y], goal:[x,y], clearance:0.10, field_clearance:0.05,
      via_cost:3.0}
out: {tracks:[{layer,w,x1,y1,x2,y2}], vias:[{x,y}], length:mm}
"""
import pcbnew as p, sys, json, math, heapq
import numpy as np
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union, polygonize
from PIL import Image, ImageDraw

JOB = json.load(open(sys.argv[2]))
NET = JOB['net']; W = JOB['width']; REG = JOB['region']
LAYERS = JOB.get('layers', ['F', 'I2', 'B'])
CLR = JOB.get('clearance', 0.10); FCLR = JOB.get('field_clearance', 0.05)
FIELD = (69.3, 119.05, 80.9, 128.9)
ANT = (70.3, 128.9, 79.9, 137.9)
STEP = 0.05
LAYID = {p.F_Cu: 'F', p.In1_Cu: 'I1', p.In2_Cu: 'I2', p.B_Cu: 'B'}

b = p.LoadBoard(sys.argv[1])
filler = p.ZONE_FILLER(b)
filler.Fill(list(b.Zones()))

def mm(v): return p.ToMM(v)
def rect_poly(cx, cy, w, h, rot):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return Polygon([(cx + dx * c - dy * s, cy + dx * s + dy * c)
                    for dx, dy in ((-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2))])

# ---------- collect geometry ----------
obs = {L: [] for L in ('F', 'I1', 'I2', 'B')}       # other-net copper
own = {L: [] for L in ('F', 'I1', 'I2', 'B')}       # target-net copper (labelled)
own_elems = []  # (layer, geom, group) for component labelling
via_centres_other = []
for f in b.GetFootprints():
    ref = str(f.GetReference())
    for pad in f.Pads():
        net = pad.GetNetname()
        pos, sz = pad.GetPosition(), pad.GetSize()
        poly = rect_poly(mm(pos.x), mm(pos.y), mm(sz.x), mm(sz.y), pad.GetOrientationDegrees())
        pth = pad.GetAttribute() == p.PAD_ATTRIB_PTH
        lays = ['F', 'I1', 'I2', 'B'] if pth else [LAYID[l] for l in (p.F_Cu, p.In1_Cu, p.In2_Cu, p.B_Cu) if pad.IsOnLayer(l)]
        for L in lays:
            if net == NET:
                own[L].append(poly); own_elems.append((L, poly, f"pad:{ref}.{pad.GetNumber()}"))
            else:
                obs[L].append(poly)
for t in b.GetTracks():
    net = t.GetNetname()
    if isinstance(t, p.PCB_VIA):
        pos = t.GetPosition(); cx, cy = mm(pos.x), mm(pos.y)
        poly = Point(cx, cy).buffer(mm(t.GetWidth(p.F_Cu)) / 2, resolution=12)
        if net == NET:
            for L in ('F', 'I1', 'I2', 'B'):
                own[L].append(poly); own_elems.append((L, poly, f"via:{cx:.3f},{cy:.3f}"))
        else:
            via_centres_other.append((cx, cy))
            for L in ('F', 'I1', 'I2', 'B'):
                obs[L].append(poly)
    else:
        s, e = t.GetStart(), t.GetEnd()
        poly = LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]).buffer(mm(t.GetWidth()) / 2, resolution=4, cap_style=1)
        L = LAYID[t.GetLayer()]
        if net == NET:
            own[L].append(poly); own_elems.append((L, poly, f"trk:{len(own_elems)}"))
        else:
            obs[L].append(poly)
for z in b.Zones():
    net = z.GetNetname()
    for lid, L in LAYID.items():
        if not z.IsOnLayer(lid):
            continue
        try:
            fps = z.GetFilledPolysList(lid)
        except Exception:
            continue
        for oi in range(fps.OutlineCount()):
            chain = fps.Outline(oi)
            pts = [(mm(chain.GetPoint(i).x), mm(chain.GetPoint(i).y)) for i in range(chain.PointCount())]
            if len(pts) < 3: continue
            poly = Polygon(pts)
            if not poly.is_valid: poly = poly.buffer(0)
            if net == NET:
                own[L].append(poly); own_elems.append((L, poly, f"zone:{len(own_elems)}"))
            elif net:
                obs[L].append(poly)

# outline polygon from Edge.Cuts
esegs = []
for d in b.GetDrawings():
    if d.GetLayer() == p.Edge_Cuts:
        s, e = d.GetStart(), d.GetEnd()
        esegs.append(LineString([(mm(s.x), mm(s.y)), (mm(e.x), mm(e.y))]))
outline = max(polygonize(esegs), key=lambda g: g.area)

# ---------- component labelling of own net ----------
class DSU:
    def __init__(self): self.par = {}
    def find(self, x):
        self.par.setdefault(x, x)
        while self.par[x] != x:
            self.par[x] = self.par[self.par[x]]; x = self.par[x]
        return x
    def union(self, a, c):
        ra, rc = self.find(a), self.find(c)
        if ra != rc: self.par[ra] = rc
dsu = DSU()
by_group = {}
for i, (L, g, grp) in enumerate(own_elems):
    by_group.setdefault(grp, []).append(i)
for idxs in by_group.values():
    for i in idxs[1:]: dsu.union(idxs[0], i)
from shapely.strtree import STRtree
by_layer = {}
for i, (L, g, grp) in enumerate(own_elems):
    by_layer.setdefault(L, []).append(i)
for L, idxs in by_layer.items():
    geoms = [own_elems[i][1] for i in idxs]
    tree = STRtree(geoms)
    for j, i in enumerate(idxs):
        for k in tree.query(geoms[j], predicate='intersects'):
            if k != j: dsu.union(i, idxs[k])
def comp_at(x, y):
    pt = Point(x, y)
    for i, (L, g, grp) in enumerate(own_elems):
        if g.contains(pt) or g.distance(pt) < 0.01:
            return dsu.find(i)
    return None
START_COMP = comp_at(*JOB['start']); GOAL_COMP = comp_at(*JOB['goal'])
assert START_COMP is not None and GOAL_COMP is not None and START_COMP != GOAL_COMP, (START_COMP, GOAL_COMP)
start_geoms = {L: [] for L in LAYERS}; goal_geoms = {L: [] for L in LAYERS}
for i, (L, g, grp) in enumerate(own_elems):
    if L not in LAYERS: continue
    r = dsu.find(i)
    if r == START_COMP: start_geoms[L].append(g)
    elif r == GOAL_COMP: goal_geoms[L].append(g)

# ---------- rasterize ----------
x0, y0, x1, y1 = REG
NX = int(round((x1 - x0) / STEP)) + 1; NY = int(round((y1 - y0) / STEP)) + 1
def raster(polys, inflate):
    img = Image.new('1', (NX, NY), 0)
    dr = ImageDraw.Draw(img)
    for g in polys:
        if g.is_empty: continue
        gg = g.buffer(inflate, resolution=4) if inflate else g
        for part in (gg.geoms if gg.geom_type == 'MultiPolygon' else [gg]):
            pts = [((px - x0) / STEP, (py - y0) / STEP) for px, py in part.exterior.coords]
            dr.polygon(pts, fill=1)
    return np.array(img, dtype=bool)
def in_field(cx, cy):
    return FIELD[0] <= cx <= FIELD[2] and FIELD[1] <= cy <= FIELD[3]
field_mask = np.zeros((NY, NX), dtype=bool)
fx0 = max(0, int((FIELD[0] - x0) / STEP)); fx1 = min(NX - 1, int((FIELD[2] - x0) / STEP))
fy0 = max(0, int((FIELD[1] - y0) / STEP)); fy1 = min(NY - 1, int((FIELD[3] - y0) / STEP))
field_mask[fy0:fy1 + 1, fx0:fx1 + 1] = True

blocked = {}; via_blocked = None
ant_poly = Polygon([(ANT[0], ANT[1]), (ANT[2], ANT[1]), (ANT[2], ANT[3]), (ANT[0], ANT[3])])
for L in LAYERS:
    o = [g for g in obs[L] if g.bounds[2] >= x0 - 1 and g.bounds[0] <= x1 + 1 and g.bounds[3] >= y0 - 1 and g.bounds[1] <= y1 + 1]
    bn = raster(o + [ant_poly], CLR + W / 2)
    bf = raster(o + [ant_poly], FCLR + W / 2)
    blk = np.where(field_mask, bf, bn)
    # outside outline (shrunk by w/2+0.15) is blocked
    out_img = Image.new('1', (NX, NY), 1)
    dr = ImageDraw.Draw(out_img)
    shr = outline.buffer(-(W / 2 + 0.15))
    for part in (shr.geoms if shr.geom_type == 'MultiPolygon' else [shr]):
        dr.polygon([((px - x0) / STEP, (py - y0) / STEP) for px, py in part.exterior.coords], fill=0)
    blk |= np.array(out_img, dtype=bool)
    blocked[L] = blk
# via raster: obstacles on F/I2/B inflated by 0.30+CLR; other vias as 0.85 discs; antenna; outline shrink 0.55
vall = []
for L in ('F', 'I2', 'B'):
    vall += obs[L]
via_obs = vall + [Point(cx, cy).buffer(0.85, resolution=8) for cx, cy in via_centres_other] + [ant_poly]
via_blocked = raster(via_obs, 0.30 + CLR)
out_img = Image.new('1', (NX, NY), 1)
dr = ImageDraw.Draw(out_img)
shr = outline.buffer(-0.55)
for part in (shr.geoms if shr.geom_type == 'MultiPolygon' else [shr]):
    dr.polygon([((px - x0) / STEP, (py - y0) / STEP) for px, py in part.exterior.coords], fill=0)
via_blocked |= np.array(out_img, dtype=bool)

start_cells = {}; goal_cells = {}
for L in LAYERS:
    if start_geoms[L]:
        start_cells[L] = raster(start_geoms[L], 0.0)
    if goal_geoms[L]:
        goal_cells[L] = raster(goal_geoms[L], 0.0)

# ---------- A* ----------
def cell_xy(ix, iy): return (x0 + ix * STEP, y0 + iy * STEP)
starts = []
for L in LAYERS:
    if L in start_cells:
        ys, xs = np.nonzero(start_cells[L])
        for ix, iy in zip(xs, ys):
            starts.append((LAYERS.index(L), int(ix), int(iy)))
goals = set()
for L in LAYERS:
    if L in goal_cells:
        ys, xs = np.nonzero(goal_cells[L])
        for ix, iy in zip(xs, ys):
            goals.add((LAYERS.index(L), int(ix), int(iy)))
assert starts and goals, 'no start/goal cells in region'
gx, gy = JOB['goal']
def heur(s):
    cx, cy = cell_xy(s[1], s[2])
    return math.hypot(cx - gx, cy - gy)
VIA_COST = JOB.get('via_cost', 3.0)
open_h = []
cost = {}
came = {}
for s in starts:
    cost[s] = 0.0; heapq.heappush(open_h, (heur(s), 0.0, s))
DIRS = [(1, 0, 1.0), (-1, 0, 1.0), (0, 1, 1.0), (0, -1, 1.0),
        (1, 1, math.sqrt(2)), (1, -1, math.sqrt(2)), (-1, 1, math.sqrt(2)), (-1, -1, math.sqrt(2))]
found = None
while open_h:
    f, g, cur = heapq.heappop(open_h)
    if g > cost.get(cur, 1e18): continue
    if cur in goals:
        found = cur; break
    li, ix, iy = cur
    L = LAYERS[li]
    for dx, dy, dc in DIRS:
        jx, jy = ix + dx, iy + dy
        if not (0 <= jx < NX and 0 <= jy < NY): continue
        nk = (li, jx, jy)
        if blocked[L][jy, jx] and nk not in goals and nk not in starts: continue
        if dx and dy and (blocked[L][iy, jx] or blocked[L][jy, ix]): continue
        ng = g + dc * STEP
        if ng < cost.get(nk, 1e18):
            cost[nk] = ng; came[nk] = cur
            heapq.heappush(open_h, (ng + heur(nk), ng, nk))
    if not via_blocked[iy, ix]:
        for lj in range(len(LAYERS)):
            if lj == li: continue
            nk = (lj, ix, iy)
            ng = g + VIA_COST
            if ng < cost.get(nk, 1e18):
                cost[nk] = ng; came[nk] = cur
                heapq.heappush(open_h, (ng + heur(nk), ng, nk))
if not found:
    print('NO PATH'); sys.exit(2)
path = [found]
while path[-1] in came:
    path.append(came[path[-1]])
path.reverse()
# ---------- simplify per layer ----------
runs = []
cur_layer = path[0][0]; cur_pts = [cell_xy(path[0][1], path[0][2])]
vias = []
for s in path[1:]:
    if s[0] != cur_layer:
        vias.append(cell_xy(s[1], s[2]))
        runs.append((LAYERS[cur_layer], cur_pts))
        cur_layer = s[0]; cur_pts = [cell_xy(s[1], s[2])]
    else:
        cur_pts.append(cell_xy(s[1], s[2]))
runs.append((LAYERS[cur_layer], cur_pts))
def simplify(pts):
    if len(pts) <= 2: return pts
    out = [pts[0]]
    for i in range(1, len(pts) - 1):
        a, bq, c = out[-1], pts[i], pts[i + 1]
        cross = abs((bq[0] - a[0]) * (c[1] - a[1]) - (bq[1] - a[1]) * (c[0] - a[0]))
        if cross > 1e-9:
            out.append(bq)
    out.append(pts[-1])
    return out
tracks = []
total = 0.0
for L, pts in runs:
    sp = simplify(pts)
    for a, bq in zip(sp, sp[1:]):
        if math.hypot(bq[0] - a[0], bq[1] - a[1]) < 0.01: continue
        tracks.append({'layer': L, 'w': W, 'x1': round(a[0], 3), 'y1': round(a[1], 3), 'x2': round(bq[0], 3), 'y2': round(bq[1], 3)})
        total += math.hypot(bq[0] - a[0], bq[1] - a[1])
json.dump({'tracks': tracks, 'vias': [{'x': round(v[0], 3), 'y': round(v[1], 3)} for v in vias],
           'length': round(total, 2), 'cost': round(cost[found], 2)}, open(sys.argv[3], 'w'), indent=1)
print(f"PATH len={total:.2f}mm tracks={len(tracks)} vias={len(vias)} cost={cost[found]:.2f}")
for v in vias: print('  via', v)
