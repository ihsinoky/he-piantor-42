"""Issue #273 verification extract: the notch-region Edge.Cuts element
chain AS SAVED in the current Wing Rev.6 boards (this worktree, HEAD
06efd9a18 = Stage 2d output). Per variant: (1) notch-zone element
count + kinds under the Stage 2d counting rule (midpoint in case frame
within removed-vs-Rev.5 region buffered 1.0 mm); (2) the ordered
element chain through the notch zone (types + endpoints, case frame);
(3) where the saved boundary leaves the Stage 2d design chain
(notch2d.json) - the surviving Rev.5 stretches (the S-wiggle)."""
import json, math, sys
from pathlib import Path
import pcbnew as p
from shapely.geometry import Polygon, LineString, Point
from shapely.affinity import rotate as shp_rotate, translate as shp_translate

MM = 1e6
W = Path("/home/hatch/workspace/projects/he-piantor-wingnotch")
SRT = "/home/hatch/workspace/projects/he-piantor-mainoutline/.issue270-runtime"
sys.path.insert(0, SRT)
from notchain import wing_xf_factory

Q263 = W / "hardware/kicad/qualification/issue-263-implementation"
Q270W = W / "hardware/kicad/qualification/issue-270-wing-rev6"
ND = json.loads(Path(SRT, "notch2d.json").read_text())

def outline(board):
    ps = p.SHAPE_POLY_SET(); board.GetBoardPolygonOutlines(ps)
    ch = ps.Outline(0)
    return Polygon([(ch.CPoint(j).x / MM, ch.CPoint(j).y / MM)
                    for j in range(ch.PointCount())])

def el_pts(d):
    s = (d.GetStart().x / MM, d.GetStart().y / MM)
    e = (d.GetEnd().x / MM, d.GetEnd().y / MM)
    return s, e

out = {}
for variant in ("17mm-left", "17mm-right", "16mm-left", "16mm-right"):
    pitch, side = variant.split("-")
    deg = 30.5 if side == "left" else -30.5
    env = (-27.0, -37.5) if side == "left" else (27.0, -37.5)
    b5 = p.LoadBoard(str(Q263 / f"wing-rev5-{variant}/main.kicad_pcb"))
    b6 = p.LoadBoard(str(Q270W / f"wing-rev6-{variant}/main.kicad_pcb"))
    fwd, inv, jw = wing_xf_factory(b5, side)
    def to_case_pt(pt):
        q = shp_translate(Point(pt), xoff=-jw[0], yoff=-jw[1])
        q = shp_rotate(q, deg, origin=(0, 0))
        q = shp_translate(q, xoff=env[0], yoff=env[1])
        return (q.x, q.y)
    def to_case(poly):
        q = shp_translate(poly, xoff=-jw[0], yoff=-jw[1])
        q = shp_rotate(q, deg, origin=(0, 0))
        return shp_translate(q, xoff=env[0], yoff=env[1])
    zone = to_case(outline(b5)).difference(to_case(outline(b6))).buffer(1.0)
    # collect Edge.Cuts elements, order into a chain by endpoints
    els = []
    for d in b6.GetDrawings():
        if d.GetLayer() != p.Edge_Cuts:
            continue
        s, e = el_pts(d)
        shp = d.GetShape()
        mid = ((s[0] + e[0]) / 2, (s[1] + e[1]) / 2)
        if shp == "ARC":
            mp = d.GetMidPoint()
            mid = (mp.x / MM, mp.y / MM)
        els.append(dict(shape=str(shp), s=s, e=e, mid=mid))
    def key(pt):
        return (round(pt[0], 4), round(pt[1], 4))
    from collections import defaultdict
    by_start = defaultdict(list)
    for i, el in enumerate(els):
        by_start[key(el["s"])].append(i)
        by_start[key(el["e"])].append(i)
    used = [False] * len(els)
    chain = []
    cur = 0; used[0] = True
    chain.append((els[0]["s"], els[0]["e"], els[0]["shape"]))
    curpt = els[0]["e"]
    for _ in range(len(els) - 1):
        nxt = None
        for i in by_start[key(curpt)]:
            if not used[i]:
                nxt = i; break
        if nxt is None:
            break
        used[nxt] = True
        el = els[nxt]
        if key(el["s"]) == key(curpt):
            chain.append((el["s"], el["e"], el["shape"])); curpt = el["e"]
        else:
            chain.append((el["e"], el["s"], el["shape"])); curpt = el["s"]
    # notch-zone elements in chain order (case frame)
    zone_chain = []
    kinds = {}
    n_zone = 0
    for a, b, shp in chain:
        midc = to_case_pt(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2))
        if zone.covers(Point(to_case_pt(a))) or zone.covers(Point(midc)):
            ac, bc = to_case_pt(a), to_case_pt(b)
            zone_chain.append((shp, [round(v, 3) for v in ac],
                               [round(v, 3) for v in bc]))
    for el in els:
        if zone.covers(Point(to_case_pt(el["mid"]))):
            n_zone += 1
            kinds[el["shape"]] = kinds.get(el["shape"], 0) + 1
    # deviation of saved outline from the 2d design chain
    els_c = []
    for e in ND[variant]["elements_case"]:
        if e[0] == "line":
            els_c.append(LineString([e[1], e[2]]))
        else:
            _, O, r, a, bb, _m = e
            a0 = math.atan2(a[1] - O[1], a[0] - O[0])
            a1 = math.atan2(bb[1] - O[1], bb[0] - O[0])
            while a1 - a0 > math.pi: a1 -= 2 * math.pi
            while a1 - a0 < -math.pi: a1 += 2 * math.pi
            n = max(8, int(abs(a1 - a0) / 0.01))
            els_c.append(LineString([(O[0] + r * math.cos(a0 + (a1 - a0) * i / n),
                                      O[1] + r * math.sin(a0 + (a1 - a0) * i / n))
                                     for i in range(n + 1)]))
    from shapely.ops import unary_union
    design = unary_union(els_c)
    oc = to_case(outline(b6))
    coords = list(oc.exterior.coords)
    devs = []
    for i in range(len(coords) - 1):
        seg = LineString([coords[i], coords[i + 1]])
        mid = seg.interpolate(0.5, normalized=True)
        if zone.covers(mid):
            devs.append((design.distance(mid), seg.length,
                         (round(mid.x, 2), round(mid.y, 2))))
    far = [d for d in devs if d[0] > 0.05]
    out[variant] = dict(
        total_edge_items=len(els), chain_len=len(chain),
        zone_count=n_zone, zone_kinds=kinds,
        zone_chain=zone_chain,
        dev_far_n=len(far),
        dev_far=[(round(d[0], 3), round(d[1], 3), d[2]) for d in far],
        dev_max=round(max((d[0] for d in devs), default=0.0), 4))
    print(f"{variant}: total {len(els)} chain {len(chain)} zone {n_zone} "
          f"kinds {kinds} dev>0.05mm segs {len(far)} maxdev "
          f"{out[variant]['dev_max']}")
    for d in far:
        print(f"   far seg dev {d[0]:.3f} len {d[1]:.3f} at case {d[2]}")
json.dump(out, open(W / ".issue273-runtime/extract.json", "w"), indent=1)
print("saved extract.json")
