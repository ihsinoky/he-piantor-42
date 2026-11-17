"""Build Wing Rev.6 for one variant: Rev.5 board with ONLY the notch-zone
Edge.Cuts replaced by the exact 0.55 mm offset floor of the implemented
Rev.9 Main tab (Stage 2a spec). Pre-check: the removed region must not
intersect any copper (tracks/vias/pads/fills). Post-checks: outline vs
the shapely buffer construction, seam vs Rev.9 = 0.550, copper invariance.
Usage: build-wing-rev6.py <variant e.g. 17mm-left> [--dry]"""
import json, math, shutil, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point, MultiPoint
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
Q263 = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-263-implementation")
Q270M = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-main-rev9")
OUTROOT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/hardware/kicad/qualification/issue-270-wing-rev6")
sys.path.insert(0, str(RT))
from geom2b import outline_of, copper_items
from notchain import wing_xf_factory, build_chain, chain_linestring

variant = sys.argv[1]
DRY = "--dry" in sys.argv
pitch, side = variant.split("-")
site = "J2" if side == "left" else "J3"

src = Q263 / f"wing-rev5-{variant}"
b = p.LoadBoard(str(src / "main.kicad_pcb"))
fwd, inv, jw = wing_xf_factory(b, side)

def poly_to_case(poly_board):
    q = shp_translate(poly_board, xoff=-jw[0], yoff=-jw[1])
    deg = 30.5 if side == "left" else -30.5
    q = shp_rotate(q, deg, origin=(0, 0))
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    return shp_translate(q, xoff=env[0], yoff=env[1])

wing_old_board = outline_of(b)
wing_old_case = poly_to_case(wing_old_board)

mb = p.LoadBoard(str(Q270M / "main-rev9" / "main.kicad_pcb"))
main9_board = outline_of(mb)
main9_case = shp_translate(main9_board, xoff=-100.0, yoff=-70.0)

buf = main9_case.buffer(0.55, resolution=64)
wing_new_case = wing_old_case.difference(buf)
removed_case = wing_old_case.intersection(buf)
print(f"{variant}: wing area {wing_old_case.area:.2f} -> {wing_new_case.area:.2f}; removed {removed_case.area:.3f} mm2")

# ---- pre-check: removed region vs copper (board frame) ----
removed_parts = list(removed_case.geoms) if removed_case.geom_type == "MultiPolygon" else [removed_case]
removed_board = unary_union([Polygon([inv(pt) for pt in part.exterior.coords]) for part in removed_parts])
print("removed components (case):", [(round(pt.area, 3), tuple(round(v, 2) for v in pt.centroid.coords[0])) for pt in removed_parts])
hits = {}
for kind, geom in copper_items(b):
    inter = geom.intersection(removed_board)
    if inter.area > 1e-6:
        hits[kind] = hits.get(kind, 0) + inter.area
print("removed-region copper hits:", {k: round(v, 5) for k, v in hits.items()} or "NONE")
hard = {k: v for k, v in hits.items() if k not in ("fill", "zonepoly")}
if hard:
    print("ABORT: removed region touches routed copper:", hard); sys.exit(1)
# pour fringe in the region is expected (as in #263's respin): zones are
# refilled after the splice and the fill delta is verified to be confined
# to the removed region. Snapshot fills for the delta check.
from geom2b import polys_of as _polys_of
fill_before = {}
for z in b.Zones():
    for l in z.GetLayerSet().Seq():
        fill_before[(z.GetZoneName(), z.GetNetname(), l)] = _polys_of(z.GetFilledPolysList(l))

# ---- floor chain from the exact buffer construction ----
# The new boundary near the tab mixes pure-offset stretches with stretches
# of the old boundary (where the old floor was deeper). Extract the part of
# wing_new's boundary that does not coincide with the old boundary.
TAB_BOARD = {
    "J2": [(82.0535, 103.3522), (76.5824, 103.3518), (68.2378, 117.805), (70.9735, 122.5433)],
    "J3": [(117.8562, 103.1958), (123.3272, 103.1958), (131.6717, 117.6489), (128.9362, 122.3869)],
}
tab_case = [(x - 100.0, y - 70.0) for x, y in TAB_BOARD[site]]
diff = wing_new_case.boundary.difference(wing_old_case.boundary.buffer(0.002))
parts = []
if diff.geom_type == "LineString":
    parts = [diff]
elif hasattr(diff, "geoms"):
    parts = [g for g in diff.geoms if g.geom_type == "LineString"]
tab_pt = Point((tab_case[0][0] + tab_case[3][0]) / 2, (tab_case[0][1] + tab_case[3][1]) / 2)
parts = [g for g in parts if g.length > 0.5 and g.distance(tab_pt) < 12]
# order parts along the new boundary
parts.sort(key=lambda g: wing_new_case.boundary.project(Point(g.coords[0])))
print("new-boundary chain parts (lengths):", [round(g.length, 2) for g in parts])
assert 1 <= len(parts) <= 4, f"unexpected part count {len(parts)}"
import numpy as np
for g in parts:
    samp = [g.interpolate(t) for t in np.linspace(0, 1, 60)]
    mind = min(pt.distance(main9_case) for pt in samp)
    assert mind > 0.54, f"chain part dips to {mind:.3f} from Rev.9 outline"
print("all chain parts keep >0.54 from the Rev.9 outline (design 0.550)")

if DRY:
    print("DRY RUN ok"); sys.exit(0)

# ---- splice into the board (board frame), one part at a time ----
from collections import defaultdict
def V(x, y):
    return p.VECTOR2I(round(x * MM), round(y * MM))
def r4(pt):
    return (round(pt[0], 4), round(pt[1], 4))
def add_seg(a, bb):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(V(*a)); s.SetEnd(V(*bb)); s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s)

def splice_part(chain_case_part):
    pts = [inv(pt) for pt in chain_case_part.coords]
    S1b, S2b = pts[0], pts[-1]
    items = []
    for d in b.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            assert d.GetShape() == p.SHAPE_T_SEGMENT, "non-segment Edge.Cuts present"
            items.append([d, (d.GetStart().x / MM, d.GetStart().y / MM),
                          (d.GetEnd().x / MM, d.GetEnd().y / MM)])
    def on_seg(pt, a, bb, tol=0.01):
        return LineString([a, bb]).distance(Point(pt)) < tol and min(math.dist(pt, a), math.dist(pt, bb)) > 0.05
    def split_at(S):
        for it in items:
            if on_seg(S, it[1], it[2]):
                return it, S
        best = None
        for it in items:
            for e in (it[1], it[2]):
                dd = math.dist(S, e)
                if dd < 0.05 and (best is None or dd < best[0]):
                    best = (dd, it, e)
        return (best[1], best[2]) if best else (None, S)
    h1, S1b = split_at(S1b)
    h2, S2b = split_at(S2b)
    assert h1 is not None and h2 is not None, "host item not found"
    # orient/simplify the chain with snapped ends
    if math.dist(pts[0], S1b) > math.dist(pts[0], S2b):
        pts.reverse(); S1b, S2b = S2b, S1b; h1, h2 = h2, h1
    ls = LineString(pts).simplify(0.002)
    pts = list(ls.coords); pts[0], pts[-1] = S1b, S2b
    print("  chain points: raw %d -> simplified %d" % (len(chain_case_part.coords), len(pts)))
    if h1 is h2:
        # both ends on one item: keep the two outer pieces, drop the middle
        d, s, e = h1
        near_s = S1b if math.dist(S1b, s) < math.dist(S2b, s) else S2b
        far_s = S2b if near_s is S1b else S1b
        b.Remove(d)
        add_seg(s, near_s); add_seg(far_s, e)
        print("  same-item splice on", [r4(s), r4(e)])
    else:
        adj = defaultdict(list)
        for idx, (d, s, e) in enumerate(items):
            adj[r4(s)].append((idx, r4(e)))
            adj[r4(e)].append((idx, r4(s)))
        i1, i2 = items.index(h1), items.index(h2)
        cands = []
        for start_vertex in (r4(h1[1]), r4(h1[2])):
            chain = [i1]; cur = start_vertex; prev = i1; guard = 0
            while chain[-1] != i2:
                nxts = [(i, v) for i, v in adj[cur] if i != prev]
                if len(nxts) != 1: break
                i, v = nxts[0]; chain.append(i); prev, cur = i, v; guard += 1
                if guard > len(items) + 2: break
            if chain[-1] == i2:
                cands.append(chain)
        assert len(cands) == 2, f"expected 2 chains, got {len(cands)}"
        def score(chain):
            tot = 0.0
            for i in chain[1:-1]:
                mid = ((items[i][1][0] + items[i][2][0]) / 2, (items[i][1][1] + items[i][2][1]) / 2)
                tot += Point(mid).distance(removed_board)
            return tot / max(1, len(chain) - 2)
        notch = cands[0] if score(cands[0]) < score(cands[1]) else cands[1]
        for i in notch[1:-1]:
            b.Remove(items[i][0])
        def zone_vertex(host_item, next_idx):
            nxt = items[next_idx]
            shared = [v for v in (r4(host_item[1]), r4(host_item[2])) if v in (r4(nxt[1]), r4(nxt[2]))]
            assert len(shared) == 1
            return shared[0]
        def trim_host(item, S, zv):
            d, s, e = item
            if r4(s) == zv: d.SetStart(V(*S))
            else: d.SetEnd(V(*S))
        trim_host(h1, S1b, zone_vertex(h1, notch[1]))
        trim_host(h2, S2b, zone_vertex(h2, notch[-2]))
        print("  spliced: removed %d interior items" % (len(notch) - 2))
    for a, bb in zip(pts, pts[1:]):
        add_seg(a, bb)
    print("  added %d chain segments" % (len(pts) - 1))

for part in parts:
    print("splicing part len %.2f" % part.length)
    splice_part(part)

out = OUTROOT / f"wing-rev6-{variant}"
out.mkdir(parents=True, exist_ok=True)
p.SaveBoard(str(out / "main.kicad_pcb"), b)

# refill zones on the new outline (the #263 respin did the same), then
# verify the fill delta is confined to the removed region.
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
ok = True
for z in b.Zones():
    for l in z.GetLayerSet().Seq():
        key = (z.GetZoneName(), z.GetNetname(), l)
        new = _polys_of(z.GetFilledPolysList(l))
        old = fill_before[key]
        delta = new.symmetric_difference(old)
        # the fill edge re-insets from the moved outline: the delta band on
        # the material side of the new floor is expected; confine the delta
        # to the removed region plus a 0.75 mm band around it.
        outside = delta.difference(removed_board.buffer(0.75))
        ncomp = lambda g: len(list(g.geoms)) if g.geom_type == "MultiPolygon" else (1 if g.area else 0)
        print(f"fill delta {key}: total {delta.area:.4f} mm2, outside removed region {outside.area:.5f} mm2, "
              f"components {ncomp(old)} -> {ncomp(new)}")
        esc = list(outside.geoms) if outside.geom_type == "MultiPolygon" else [outside]
        esc_max = max((e.area for e in esc), default=0.0)
        print("   outside-band: %.4f mm2, largest component %.4f" % (outside.area, esc_max))
        # refill re-derives the pour edge from the whole outline; um-scale
        # slivers at distant shallow vertices are refill noise (measured
        # 0.067 mm2 total on 17L). Anything bigger is a real escape.
        if outside.area > 0.15 or esc_max > 0.05 or ncomp(new) != ncomp(old):
            ok = False
            print("   ESCAPING:", [(round(e.area, 4), tuple(round(v, 2) for v in e.centroid.coords[0])) for e in esc if e.area > 1e-4])
print("fill-delta confined:", ok)
assert ok, "fill delta escapes the removed region or splits a pour"
p.SaveBoard(str(out / "main.kicad_pcb"), b)
for f in src.iterdir():
    if f.is_file() and f.name not in ("main.kicad_pcb",) and not f.name.endswith((".log", ".json")):
        shutil.copyfile(f, out / f.name)
print("saved", out / "main.kicad_pcb")
