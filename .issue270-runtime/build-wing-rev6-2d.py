"""Build Wing Rev.6 stage 2d for one variant: Rev.5 board with ONLY
the notch-zone Edge.Cuts replaced by the SIMPLIFIED notch floor from
notch2d.json (3 parallel straights + R0.55 tangent fillets, offsets
0.56, min seam 0.560). The new boundary alternates between the design
chain and surviving old-boundary stretches (where the Rev.5 floor is
already deeper), so the splice is parts-based (Stage 2b method):
parts = new boundary not coincident with the old boundary; each part
is emitted as the exact design sub-chain (lines + true arcs) mapped
from notch2d.json, with a faceted fallback. Zones refilled; fill
delta must stay confined to the removed region + 0.75 mm band.
Usage: build-wing-rev6-2d.py <variant>"""
import json, math, shutil, sys
from collections import defaultdict
from pathlib import Path
import numpy as np
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.ops import unary_union
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
RT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime")
WT = Path("/home/hatch/workspace/projects/he-piantor-mainoutline")
Q263 = WT / "hardware/kicad/qualification/issue-263-implementation"
Q270M = WT / "hardware/kicad/qualification/issue-270-main-rev9/main-rev9"
OUTROOT = WT / "hardware/kicad/qualification/issue-270-wing-rev6"
sys.path.insert(0, str(RT))
from geom2b import polys_of as _polys_of
from notchain import wing_xf_factory

variant = sys.argv[1]
pitch, side = variant.split("-")
ND = json.loads((RT / "notch2d.json").read_text())[variant]

def outline_kicad(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM) for j in range(ch.PointCount())])

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
removed_board = to_board(removed_case)
if not removed_board.is_valid:
    removed_board = removed_board.buffer(0)
print(f"{variant}: removed {removed_case.area:.3f} mm2 (design {ND['removed_area_mm2']})")
main_case = shp_translate(outline_kicad(p.LoadBoard(str(Q270M / "main.kicad_pcb"))), xoff=-100.0, yoff=-70.0)

# ---- design chain elements (case frame) ----
els_case = []
for e in ND["elements_case"]:
    if e[0] == "line":
        els_case.append(("line", tuple(e[1]), tuple(e[2])))
    else:
        els_case.append(("arc", tuple(e[1]), e[2], tuple(e[3]), tuple(e[4]), tuple(e[5])))

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

el_geoms = [el_geom(e) for e in els_case]

def sub_elements(S1, S2):
    """Exact design sub-chain from case point S1 to S2 along the chain.
    Returns element list (case frame) or None if unmapped."""
    def locate(P):
        for i, gm in enumerate(el_geoms):
            if gm.distance(Point(P)) < 0.01:
                return i
        return None
    ia, ib = locate(S1), locate(S2)
    if ia is None or ib is None:
        return None
    # parts may run opposite to the design-chain direction; build the
    # sub-chain in chain order (lo -> hi) and let the caller orient it
    if ia <= ib:
        i1, i2, Plo, Phi = ia, ib, S1, S2
    else:
        i1, i2, Plo, Phi = ib, ia, S2, S1
    out = []
    for i in range(i1, i2 + 1):
        el = els_case[i]
        a = Plo if i == i1 else (el[1] if el[0] == "line" else el[3])
        z = Phi if i == i2 else (el[2] if el[0] == "line" else el[4])
        if el[0] == "line":
            if math.dist(a, z) > 1e-6:
                out.append(("line", a, z))
        else:
            _, O, r, ea, eb, _ = el
            if math.dist(a, z) < 1e-9:
                continue
            a0 = math.atan2(a[1] - O[1], a[0] - O[0]); a1 = math.atan2(z[1] - O[1], z[0] - O[0])
            aA = math.atan2(ea[1] - O[1], ea[0] - O[0]); aB = math.atan2(eb[1] - O[1], eb[0] - O[0])
            while aB - aA > math.pi: aB -= 2 * math.pi
            while aB - aA < -math.pi: aB += 2 * math.pi
            while a0 - aA > math.pi: a0 -= 2 * math.pi
            while a0 - aA < -math.pi: a0 += 2 * math.pi
            while a1 - aA > math.pi: a1 -= 2 * math.pi
            while a1 - aA < -math.pi: a1 += 2 * math.pi
            amid = aA + (a0 + a1) / 2 - aA if False else (a0 + a1) / 2
            mid = (O[0] + r * math.cos(amid), O[1] + r * math.sin(amid))
            out.append(("arc", O, r, a, z, mid))
    return out

def el_to_board(el):
    if el[0] == "line":
        return ("line", inv(el[1]), inv(el[2]))
    return ("arc", inv(el[1]), el[2], inv(el[3]), inv(el[4]), inv(el[5]))

# ---- parts of the new boundary not coincident with the old ----
diff = wing_new_case.boundary.difference(wing_old_case.boundary.buffer(0.002))
parts = []
if diff.geom_type == "LineString":
    parts = [diff]
elif hasattr(diff, "geoms"):
    parts = [gm for gm in diff.geoms if gm.geom_type == "LineString"]
tab_pt = Point((ND["elements_case"][2][1][0] + ND["elements_case"][2][2][0]) / 2,
               (ND["elements_case"][2][1][1] + ND["elements_case"][2][2][1]) / 2)
parts = [gm for gm in parts if gm.length > 0.3 and gm.distance(tab_pt) < 14]
parts.sort(key=lambda gm: wing_new_case.boundary.project(Point(gm.coords[0])))
print("new-boundary parts (lengths):", [round(gm.length, 2) for gm in parts])
assert 1 <= len(parts) <= 4, f"unexpected part count {len(parts)}"
for gm in parts:
    samp = [gm.interpolate(t) for t in np.linspace(0, 1, 60)]
    mind = min(pt.distance(main_case) for pt in samp)
    assert mind > 0.54, f"part dips to {mind:.3f} from the final Main outline"
print("all parts keep >0.54 from the final Main outline (design 0.560)")

# ---- snapshot fills + census ----
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
                      t.GetStart().x, t.GetStart().y, t.GetEnd().x, t.GetEnd().y, t.GetNetname(), t.GetLayer()))
    for z in board.Zones():
        items.append(("zone", z.m_Uuid.AsString(), z.GetZoneName(), z.GetNetname()))
    return sorted(str(i) for i in items)
cen_before = census(b)

def V(x, y):
    return p.VECTOR2I(round(x * MM), round(y * MM))
def r4(pt):
    return (round(pt[0], 4), round(pt[1], 4))
def add_seg(a, bb):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_SEGMENT)
    s.SetStart(V(*a)); s.SetEnd(V(*bb)); s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s)
def add_arc(O, r, a, mid, bb):
    s = p.PCB_SHAPE(b); s.SetShape(p.SHAPE_T_ARC)
    s.SetArcGeometry(V(*a), V(*mid), V(*bb))
    s.SetLayer(p.Edge_Cuts); s.SetWidth(int(0.1 * MM))
    b.Add(s)

def splice_part(part_case):
    S1c, S2c = tuple(part_case.coords[0]), tuple(part_case.coords[-1])
    els = sub_elements(S1c, S2c)
    if els is None:
        ls = part_case.simplify(0.002)
        els = [("line", tuple(ls.coords[i]), tuple(ls.coords[i + 1])) for i in range(len(ls.coords) - 1)]
        print("  part: FACETED fallback, %d segments" % len(els))
    else:
        print("  part: exact sub-chain", [e[0] for e in els])
    els_b = [el_to_board(e) for e in els]
    S1b, S2b = inv(S1c), inv(S2c)
    items = []
    for d in b.GetDrawings():
        if d.GetLayer() == p.Edge_Cuts:
            # arcs emitted by earlier parts enter as chord pseudo-items
            # (adjacency only; they are never splice hosts)
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
    assert h1[0].GetShape() == p.SHAPE_T_SEGMENT and h2[0].GetShape() == p.SHAPE_T_SEGMENT, \
        "host is an emitted arc - unexpected"
    # orient elements to run S1b -> S2b
    if els_b and math.dist(els_b[0][1] if els_b[0][0] == "line" else els_b[0][3], S1b) > \
                 math.dist(els_b[0][1] if els_b[0][0] == "line" else els_b[0][3], S2b):
        els_b = [("line", e[2], e[1]) if e[0] == "line" else ("arc", e[1], e[2], e[4], e[3], e[5])
                 for e in reversed(els_b)]
    if h1 is h2:
        d, s, e = h1
        near_s = S1b if math.dist(S1b, s) < math.dist(S2b, s) else S2b
        far_s = S2b if near_s is S1b else S1b
        b.Remove(d)
        if math.dist(s, near_s) > 1e-6:
            add_seg(s, near_s)
        if math.dist(far_s, e) > 1e-6:
            add_seg(far_s, e)
        print("  same-item splice")
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
    # snap element ends to the splice points and emit
    if els_b:
        e0 = els_b[0]
        els_b[0] = ("line", S1b, e0[2]) if e0[0] == "line" else ("arc", e0[1], e0[2], S1b, e0[4], e0[5])
        e1 = els_b[-1]
        els_b[-1] = ("line", e1[1], S2b) if e1[0] == "line" else ("arc", e1[1], e1[2], e1[3], S2b, e1[5])
    for el in els_b:
        if el[0] == "line":
            if math.dist(el[1], el[2]) > 1e-6:
                add_seg(el[1], el[2])
        else:
            add_arc(el[1], el[2], el[3], el[5], el[4])
    print("  emitted %d elements" % len(els_b))

for part in parts:
    print("splicing part len %.2f" % part.length)
    splice_part(part)

out = OUTROOT / f"wing-rev6-{variant}"
out.mkdir(parents=True, exist_ok=True)
p.SaveBoard(str(out / "main.kicad_pcb"), b)

# ---- refill + confinement (2b rule) ----
filler = p.ZONE_FILLER(b)
filler.Fill(b.Zones())
ok = True
for z in b.Zones():
    for l in z.GetLayerSet().Seq():
        key = (z.GetZoneName(), z.GetNetname(), l)
        new = _polys_of(z.GetFilledPolysList(l))
        old = fill_before[key]
        delta = new.symmetric_difference(old)
        outside = delta.difference(removed_board.buffer(0.75))
        ncomp = lambda gg: len(list(gg.geoms)) if gg.geom_type == "MultiPolygon" else (1 if gg.area else 0)
        esc = list(outside.geoms) if outside.geom_type == "MultiPolygon" else [outside]
        esc_max = max((e.area for e in esc), default=0.0)
        print(f"fill delta {key}: total {delta.area:.4f}, outside band {outside.area:.5f}, "
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
assert sd.area < 0.10 and seam >= 0.55 - 1e-9 and ovl == 0.0  # symdiff: um-wide transform slivers + endpoint snaps (see 2d REPORT)
for f in src.iterdir():
    if f.is_file() and f.name not in ("main.kicad_pcb",) and not f.name.endswith((".log", ".json")):
        shutil.copyfile(f, out / f.name)
print("saved", out / "main.kicad_pcb")
