#!/usr/bin/env python3
"""Component-accurate island survey: nearest approach of each off-return
GND component to the J_WING component, per layer, with blockers."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
import pcbnew
from shapely.geometry import Point, LineString
from shapely.ops import unary_union, nearest_points
import gndcheck as gc

NM = 1e6
LAYERS = [pcbnew.F_Cu, pcbnew.B_Cu]
LNAME = {pcbnew.F_Cu: "F.Cu", pcbnew.B_Cu: "B.Cu"}

def build(board):
    gnd_code = None
    objs = []  # dicts: layer, geom, kind, desc, pad (ref.num or None)
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == "GND":
                gnd_code = pad.GetNetCode()
    for zone in board.Zones():
        if zone.GetNetCode() != gnd_code:
            continue
        for l in LAYERS:
            if zone.IsOnLayer(l):
                for i, p in enumerate(gc.polys_from_set(zone.GetFilledPolysList(l))):
                    objs.append(dict(layer=l, geom=p, kind="fill", desc=f"fill#{i} a={p.area:.2f}", pad=None))
    for t in board.GetTracks():
        if t.GetNetCode() != gnd_code:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            pos = t.GetPosition()
            c = (pos.x / NM, pos.y / NM)
            for l in LAYERS:
                if t.IsOnLayer(l):
                    objs.append(dict(layer=l, geom=Point(c).buffer(t.GetWidth(l) / NM / 2.0, resolution=32),
                                     kind="via", desc=f"via @({c[0]:.2f},{c[1]:.2f})", pad=None, centre=c))
        else:
            s, e = t.GetStart(), t.GetEnd()
            ls = LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)])
            for l in LAYERS:
                if t.IsOnLayer(l):
                    objs.append(dict(layer=l, geom=ls.buffer(t.GetWidth() / NM / 2.0, cap_style=1, resolution=8),
                                     kind="track", desc=f"track ({s.x/NM:.2f},{s.y/NM:.2f})->({e.x/NM:.2f},{e.y/NM:.2f}) w={t.GetWidth()/NM:.2f}", pad=None))
    pad_objs = {}
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            if pad.GetNetname() != "GND":
                continue
            for l in LAYERS:
                if pad.IsOnLayer(l):
                    o = dict(layer=l, geom=gc.pad_geom(pad, l), kind="pad",
                             desc=f"pad {ref}.{pad.GetNumber()}", pad=f"{ref}.{pad.GetNumber()}")
                    objs.append(o)
                    pad_objs.setdefault(f"{ref}.{pad.GetNumber()}", []).append(o)
    # union-find
    parent = list(range(len(objs)))
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]; a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb: parent[ra] = rb
    from shapely.strtree import STRtree
    for l in LAYERS:
        idx = [i for i, o in enumerate(objs) if o["layer"] == l]
        geoms = [objs[i]["geom"] for i in idx]
        tree = STRtree(geoms)
        for k, i in enumerate(idx):
            for j in tree.query(geoms[k], predicate="intersects"):
                if idx[j] != i:
                    union(i, idx[j])
    # cross-layer at vias
    via_centres = [o["centre"] for o in objs if o["kind"] == "via" and "centre" in o]
    seen = set()
    for c in via_centres:
        if c in seen: continue
        seen.add(c)
        hits = [i for i, o in enumerate(objs) if o["geom"].distance(Point(c)) < 1e-9]
        for h in hits[1:]:
            union(hits[0], h)
    return objs, find, pad_objs

def survey(path):
    board = pcbnew.LoadBoard(path)
    objs, find, pad_objs = build(board)
    jw_root = find(objs.index(pad_objs["J_WING.2"][0]))
    groups = {}
    for name, olist in pad_objs.items():
        r = find(objs.index(olist[0]))
        groups.setdefault(r, []).append(name)
    print(f"### {os.path.basename(path)}  components with pads: {len(groups)}")
    jw_objs = [o for i, o in enumerate(objs) if find(i) == jw_root]
    for root, names in sorted(groups.items(), key=lambda kv: -len(kv[1])):
        tag = "J_WING" if root == jw_root else "ISLAND"
        print(f"[{tag}] {len(names)} pads: {sorted(names)}")
        if root == jw_root:
            continue
        iobjs = [o for i, o in enumerate(objs) if find(i) == root]
        for l in LAYERS:
            ig = [o["geom"] for o in iobjs if o["layer"] == l]
            jg = [o["geom"] for o in jw_objs if o["layer"] == l]
            if not ig or not jg:
                continue
            iu, ju = unary_union(ig), unary_union(jg)
            d = iu.distance(ju)
            a, b = nearest_points(iu, ju)
            print(f"  {LNAME[l]}: dist island->return {d:.3f} mm, nearest ({a.x:.3f},{a.y:.3f}) -> ({b.x:.3f},{b.y:.3f}); island area {iu.area:.2f}")
            # blockers: other-net copper intersecting the corridor box
            seg = LineString([a, b]).buffer(0.45, cap_style=2)
            blockers = []
            for net, kind, g, desc in gc_other(board, l):
                if seg.intersects(g):
                    blockers.append(f"[{net}] {desc} d_island={iu.distance(g):.3f}")
            for bl in blockers[:12]:
                print(f"    corridor blocker: {bl}")
            if not blockers:
                print("    corridor blockers: NONE")

_cache = {}
def gc_other(board, layer):
    key = (id(board), layer)
    if key in _cache: return _cache[key]
    out = []
    for t in board.GetTracks():
        if t.GetNetname() == "GND" or not t.IsOnLayer(layer):
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            pos = t.GetPosition()
            g = Point(pos.x / NM, pos.y / NM).buffer(t.GetWidth(layer) / NM / 2.0, resolution=32)
            out.append((t.GetNetname(), "via", g, f"via @({pos.x/NM:.2f},{pos.y/NM:.2f})"))
        else:
            s, e = t.GetStart(), t.GetEnd()
            g = LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)]).buffer(t.GetWidth() / NM / 2.0, cap_style=1, resolution=8)
            out.append((t.GetNetname(), "track", g, f"track ({s.x/NM:.2f},{s.y/NM:.2f})->({e.x/NM:.2f},{e.y/NM:.2f}) w={t.GetWidth()/NM:.2f}"))
    for zone in board.Zones():
        if zone.GetNetname() in ("GND", ""):
            continue
        if zone.IsOnLayer(layer):
            for p in gc.polys_from_set(zone.GetFilledPolysList(layer)):
                out.append((zone.GetNetname(), "zonefill", p, f"zone fill a={p.area:.1f}"))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() in ("GND", "") or not pad.IsOnLayer(layer):
                continue
            pos = pad.GetPosition()
            out.append((pad.GetNetname(), "pad", gc.pad_geom(pad, layer),
                        f"pad {fp.GetReference()}.{pad.GetNumber()} @({pos.x/NM:.2f},{pos.y/NM:.2f})"))
    _cache[key] = out
    return out

if __name__ == "__main__":
    import warnings; warnings.filterwarnings("ignore")
    survey(sys.argv[1])
