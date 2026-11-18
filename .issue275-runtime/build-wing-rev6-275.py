#!/usr/bin/env python3
"""Build Wing Rev.6 stage 2e for one variant by FULL OUTLINE REBUILD:
the Rev.5 board's Edge.Cuts (336 segments, no arcs) are ordered into
a ring in the fitted (case) frame; the notch span between the 2e
design chain's endpoints is replaced by the exact design chain from
notch2e.json (lines + true arcs); every other ring segment is
re-emitted unchanged (same endpoints, fp round-trip ~1e-7mm). All
Edge.Cuts are deleted and re-added in ONE pass (the 2d parts-splice
iteratively mutated the board and corrupted the SWIG drawings list
on the 3rd part - see build-17L.log). Zones refilled; fill delta
must stay confined to the (removed + added) region + 0.75mm band.
Post-checks: non-outline census unchanged, outline symdiff vs the
design polygon < 0.10mm2, seam vs final Rev.9 Main >= 0.55, overlap 0.
Usage: build-wing-rev6-2e.py <variant>"""
import json, math, shutil, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainsym/.issue275-runtime")
WT = Path("/home/hatch/workspace/projects/he-piantor-mainsym")
Q263 = WT / "hardware/kicad/qualification/issue-263-implementation"
Q270M = WT / "hardware/kicad/qualification/issue-275-main-rev10/main-rev10"
OUTROOT = WT / "hardware/kicad/qualification/issue-270-wing-rev6"
sys.path.insert(0, "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
from geom2b import polys_of as _polys_of
from notchain import wing_xf_factory

variant = sys.argv[1]
pitch, side = variant.split("-")
ND = json.loads((RT / "notch275.json").read_text())[variant]


def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM)
                    for j in range(ch.PointCount())])


src = Q263 / f"wing-rev5-{variant}"
b = p.LoadBoard(str(src / "main.kicad_pcb"))
fwd, inv, jw = wing_xf_factory(b, side)
deg = 30.5 if side == "left" else -30.5
env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)


def to_case(poly_board):
    q = shp_translate(poly_board, xoff=-jw[0], yoff=-jw[1])
    q = shp_rotate(q, deg, origin=(0, 0))
    return shp_translate(q, xoff=env[0], yoff=env[1])


def to_board(geom_case):
    q = shp_translate(geom_case, xoff=-env[0], yoff=-env[1])
    q = shp_rotate(q, -deg, origin=(0, 0))
    return shp_translate(q, xoff=jw[0], yoff=jw[1])


wing_old_case = to_case(outline_kicad(b))
wing_new_case = Polygon(ND["wing_new_case"])
removed_case = wing_old_case.difference(wing_new_case)
added_case = wing_new_case.difference(wing_old_case)
delta_board = to_board(removed_case.union(added_case))
print(f"{variant}: removed {removed_case.area:.3f} (design {ND['diag']['removed_area']:.3f}); "
      f"added {added_case.area:.3f} (design {ND['diag']['added_area']:.3f})")
main_case = shp_translate(outline_kicad(p.LoadBoard(str(Q270M / "main.kicad_pcb"))),
                          xoff=-100.0, yoff=-70.0)

# ---- design chain (case frame) ----
els_case = []
for e in ND["elements_case"]:
    if e[0] == "line":
        els_case.append(("line", tuple(e[1]), tuple(e[2])))
    else:
        els_case.append(("arc", tuple(e[1]), e[2], tuple(e[3]), tuple(e[4]), tuple(e[5])))
chain_start = els_case[0][1] if els_case[0][0] == "line" else els_case[0][3]
chain_end = els_case[-1][2] if els_case[-1][0] == "line" else els_case[-1][4]


def el_geom(el):
    if el[0] == "line":
        return LineString([el[1], el[2]])
    _, O, r, a, bb, _ = el
    a0 = math.atan2(a[1] - O[1], a[0] - O[0]); a1 = math.atan2(bb[1] - O[1], bb[0] - O[0])
    while a1 - a0 > math.pi: a1 -= 2 * math.pi
    while a1 - a0 < -math.pi: a1 += 2 * math.pi
    n = max(8, int(abs(a1 - a0) / 0.01))
    return LineString([(O[0] + r * math.cos(a0 + (a1 - a0) * i / n),
                        O[1] + r * math.sin(a0 + (a1 - a0) * i / n)) for i in range(n + 1)])


chain_union = unary_union([el_geom(e) for e in els_case])
mind = chain_union.distance(main_case)
print(f"design chain min distance to final Main outline: {mind:.4f}")
assert mind > 0.54

# ---- snapshot fills + census (before any edit) ----
fill_before = {}
for z in b.Zones():
    for l in z.GetLayerSet().Seq():
        fill_before[(z.GetZoneName(), z.GetNetname(), l)] = _polys_of(z.GetFilledPolysList(l))


def census(board):
    items = []
    for f in board.GetFootprints():
        items.append(("fp", f.GetReference(), f.GetPosition().x, f.GetPosition().y, f.GetValue()))
        for a in f.Pads():
            items.append(("pad", f.GetReference(), a.GetNumber(), a.GetPosition().x, a.GetPosition().y))
    for t in board.GetTracks():
        items.append(("via" if isinstance(t, p.PCB_VIA) else "trk", t.m_Uuid.AsString(),
                      t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y,
                      t.GetNetname(), t.GetLayer()))
    for z in board.Zones():
        items.append(("zone", z.m_Uuid.AsString(), z.GetZoneName(), z.GetNetname()))
    return sorted(str(i) for i in items)


cen_before = census(b)

# ---- order the Rev.5 Edge.Cuts segments into a ring (case frame) ----
segs = []
for d in b.GetDrawings():
    if d.GetLayer() != p.Edge_Cuts:
        continue
    assert str(d.GetShape()) in ("0", "SEGMENT"), f"unexpected outline shape {d.GetShape()}"
    s = fwd((d.GetStart().x / MM, d.GetStart().y / MM))
    e = fwd((d.GetEnd().x / MM, d.GetEnd().y / MM))
    segs.append((s, e))
print(f"outline segments: {len(segs)}")


def key(pt):
    return (round(pt[0], 4), round(pt[1], 4))


adj = defaultdict(list)
for i, (s, e) in enumerate(segs):
    adj[key(s)].append(i)
    adj[key(e)].append(i)
assert all(len(v) == 2 for v in adj.values()), "outline is not a single closed ring"
ring_idx = [0]
ring_pts = [segs[0][0], segs[0][1]]
used = {0}
cur = key(segs[0][1])
while len(ring_idx) < len(segs):
    nxt = [i for i in adj[cur] if i not in used]
    assert len(nxt) == 1, "ring walk stuck"
    i = nxt[0]
    used.add(i)
    ring_idx.append(i)
    s, e = segs[i]
    nxt_pt = e if key(s) == cur else s
    ring_pts.append(nxt_pt)
    cur = key(nxt_pt)
assert key(ring_pts[-1]) == key(ring_pts[0])
ring_pts = ring_pts[:-1]  # open ring, vertices in order
n = len(ring_pts)
print(f"ring vertices: {n}")


def seg_proj(pt):
    pt = np.array(pt)
    best = (1e9, -1, 0.0)
    for i in range(n):
        a, bb = np.array(ring_pts[i]), np.array(ring_pts[(i + 1) % n])
        ab = bb - a
        t = float(np.clip(np.dot(pt - a, ab) / np.dot(ab, ab), 0, 1))
        d = float(np.linalg.norm(pt - (a + ab * t)))
        if d < best[0]:
            best = (d, i, t)
    return best


dS = seg_proj(chain_start)
dE = seg_proj(chain_end)
assert dS[0] < 1e-3 and dE[0] < 1e-3, f"chain endpoints off ring: {dS[0]:.4f} {dE[0]:.4f}"
fe = els_case[ND["front_index"]]
tab_pt = Point(((fe[1][0] + fe[2][0]) / 2, (fe[1][1] + fe[2][1]) / 2))


def ring_walk(i_from, i_to):
    """Vertices from ring index i_from forward to i_to (inclusive)."""
    pts = []
    i = i_from
    while True:
        pts.append(ring_pts[i % n])
        if i % n == i_to:
            return pts
        i += 1


# span A: start -> end forward; span B: end -> start forward
spanA = [chain_start] + ring_walk(dS[1] + 1, dE[1]) + [chain_end]
spanB = [chain_end] + ring_walk(dE[1] + 1, dS[1]) + [chain_start]
scoreA = LineString(spanA).distance(tab_pt)
scoreB = LineString(spanB).distance(tab_pt)
notch_span, long_span = (spanA, spanB) if scoreA < scoreB else (spanB, spanA)
print(f"span scores: notch {min(scoreA, scoreB):.2f} (verts {len(notch_span)}), "
      f"long {max(scoreA, scoreB):.2f} (verts {len(long_span)})")
assert min(scoreA, scoreB) < 5.0 < max(scoreA, scoreB)
if long_span[0] == chain_start:
    long_span = long_span[::-1]
assert long_span[0] == chain_end and long_span[-1] == chain_start
# long_span runs chain_end -> ... -> chain_start; emit it as segments,
# then the design chain (chain_start -> ... -> chain_end)
new_els_case = []
for i in range(len(long_span) - 1):
    new_els_case.append(("line", long_span[i], long_span[i + 1]))
new_els_case += els_case
print(f"new outline elements: {len(new_els_case)} "
      f"({sum(1 for e in new_els_case if e[0] == 'line')} lines, "
      f"{sum(1 for e in new_els_case if e[0] == 'arc')} arcs)")

# ---- rebuild Edge.Cuts in one pass ----
old_drawings = [d for d in b.GetDrawings() if d.GetLayer() == p.Edge_Cuts]
for d in old_drawings:
    b.Remove(d)


def V(x, y):
    return p.VECTOR2I(round(x * MM), round(y * MM))


_keep = []


def add_seg(a, bb):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(V(*a)); s.SetEnd(V(*bb)); s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s); _keep.append(s)


def add_arc(O, r, a, mid, bb):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_ARC)
    s.SetArcGeometry(V(*a), V(*mid), V(*bb))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s); _keep.append(s)


for el in new_els_case:
    if el[0] == "line":
        a, bb = inv(el[1]), inv(el[2])
        if math.dist(a, bb) > 1e-6:
            add_seg(a, bb)
    else:
        add_arc(inv(el[1]), el[2], inv(el[3]), inv(el[5]), inv(el[4]))

out = OUTROOT / f"wing-rev6-{variant}"
out.mkdir(parents=True, exist_ok=True)
p.SaveBoard(str(out / "main.kicad_pcb"), b)

# ---- refill + confinement ----
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
ok = True
for z in b.Zones():
    for l in z.GetLayerSet().Seq():
        k = (z.GetZoneName(), z.GetNetname(), l)
        new = _polys_of(z.GetFilledPolysList(l))
        old = fill_before[k]
        delta = new.symmetric_difference(old)
        outside = delta.difference(delta_board.buffer(0.75))
        ncomp = lambda gg: len(list(gg.geoms)) if gg.geom_type == "MultiPolygon" else (1 if gg.area else 0)
        esc = list(outside.geoms) if outside.geom_type == "MultiPolygon" else [outside]
        esc_max = max((e.area for e in esc), default=0.0)
        print(f"fill delta {k}: total {delta.area:.4f}, outside band {outside.area:.5f}, "
              f"largest {esc_max:.4f}, components {ncomp(old)} -> {ncomp(new)}")
        if outside.area > 0.15 or esc_max > 0.05 or ncomp(new) != ncomp(old):
            ok = False
print("fill-delta confined:", ok)
assert ok, "fill delta escapes"
p.SaveBoard(str(out / "main.kicad_pcb"), b)

# ---- post-checks ----
b2 = p.LoadBoard(str(out / "main.kicad_pcb"))
assert census(b2) == cen_before, "non-outline census changed"
new_case = to_case(outline_kicad(b2))
sd = new_case.symmetric_difference(wing_new_case)
seam = main_case.distance(new_case)
ovl = main_case.intersection(new_case).area
print(f"post: outline symdiff vs design {sd.area:.5f} mm2; seam vs final Main {seam:.4f}; overlap {ovl:.5f}")
assert sd.area < 0.10 and seam >= 0.55 - 1e-9 and ovl == 0.0
for f in src.iterdir():
    if f.is_file() and f.name not in ("main.kicad_pcb",) and not f.name.endswith((".log", ".json")):
        shutil.copyfile(f, out / f.name)
print("saved", out / "main.kicad_pcb")
