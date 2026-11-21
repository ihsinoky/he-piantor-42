#!/usr/bin/env python3
"""Pad-level connectivity checker for one net (generalised gndcheck).

Usage: netcheck.py <board> <netname> [root_ref]

Walks the SAVED copper only (zone fills exactly as stored in the file,
tracks, via annuli, pads) and proves which GND pads belong to the
component that contains the J_WING (FH12) GND pins.  No zone refill is
performed at any point.  Cross-layer joins happen at plated vias and
through-hole pads.

Usage: gndcheck.py <board.kicad_pcb> [--dilate-um 0.5]
Exit code 0 iff every GND pad is in the J_WING component.
"""
import sys, os, json, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "pylibs"))
K = "/home/hatch/workspace/projects/he-piantor-42/.issue129-runtime/kicad/usr"
sys.path.insert(0, K + "/lib/python3/dist-packages")
os.environ.setdefault("LD_LIBRARY_PATH", K + "/lib/x86_64-linux-gnu:" + K + "/lib")

import pcbnew
from shapely.geometry import Polygon, LineString, Point, MultiPolygon
from shapely.ops import unary_union

NM = 1e6  # KiCad internal units per mm

def chain_points(chain):
    return [(chain.CPoint(i).x / NM, chain.CPoint(i).y / NM)
            for i in range(chain.PointCount())]

def polys_from_set(ps):
    out = []
    for i in range(ps.OutlineCount()):
        shell = chain_points(ps.Outline(i))
        holes = [chain_points(ps.Hole(i, j)) for j in range(ps.HoleCount(i))]
        try:
            p = Polygon(shell, holes)
            if not p.is_valid:
                p = p.buffer(0)
            if not p.is_empty:
                out.append(p)
        except Exception:
            pass
    return out

def pad_geom(pad, layer):
    """Shapely geometry of a pad's copper on the given layer (mm)."""
    pos = pad.GetPosition()
    cx, cy = pos.x / NM, pos.y / NM
    size = pad.GetSize()
    w, h = size.x / NM, size.y / NM
    ang = pad.GetOrientation().AsDegrees()
    shape = pad.GetShape()
    off = pad.GetOffset()
    ox, oy = off.x / NM, off.y / NM
    # local geometry centred at pad centre (+ offset), then rotate+translate
    if shape == pcbnew.PAD_SHAPE_CIRCLE:
        g = Point(ox, oy).buffer(w / 2.0, resolution=48)
    elif shape == pcbnew.PAD_SHAPE_OVAL:
        if w >= h:
            g = LineString([(ox - (w - h) / 2.0, oy), (ox + (w - h) / 2.0, oy)]).buffer(h / 2.0, resolution=32)
        else:
            g = LineString([(ox, oy - (h - w) / 2.0), (ox, oy + (h - w) / 2.0)]).buffer(w / 2.0, resolution=32)
    else:  # RECT / ROUNDRECT / CHAMFERED_RECT / TRAPEZOID / CUSTOM -> outline polygon
        try:
            ps = pad.GetEffectivePolygon(layer)  # may not exist in this build
            polys = polys_from_set(ps)
            if polys:
                return unary_union(polys)
        except Exception:
            pass
        hw, hh = w / 2.0, h / 2.0
        g = Polygon([(ox - hw, oy - hh), (ox + hw, oy - hh),
                     (ox + hw, oy + hh), (ox - hw, oy + hh)])
    if ang:
        from shapely.affinity import rotate, translate
        g = rotate(g, ang, origin=(0, 0), use_radians=False)
        g = translate(g, xoff=cx, yoff=cy)
    else:
        from shapely.affinity import translate
        g = translate(g, xoff=cx, yoff=cy)
    return g

def board_gnd(board_path, dilate_um=0.0, net="GND", root_ref="J_WING"):
    board = pcbnew.LoadBoard(board_path)
    layers = [pcbnew.F_Cu, pcbnew.B_Cu]
    layer_names = {pcbnew.F_Cu: "F.Cu", pcbnew.B_Cu: "B.Cu"}
    gnd_net = board.GetNetInfo().GetNetItem("GND") if hasattr(board, "GetNetInfo") else None
    gnd_code = None
    for code in range(1, board.GetNetInfo().GetNetCount() if hasattr(board.GetNetInfo(), "GetNetCount") else 0):
        pass
    # simpler: find netcode from any GND pad
    pads = []          # (ref, number, layer, geom, centre)
    for fp in board.GetFootprints():
        ref = fp.GetReference()
        for pad in fp.Pads():
            if pad.GetNetname() != net:
                continue
            if gnd_code is None:
                gnd_code = pad.GetNetCode()
            for layer in layers:
                if pad.IsOnLayer(layer):
                    pos = pad.GetPosition()
                    pads.append((ref, pad.GetNumber(), layer,
                                 pad_geom(pad, layer),
                                 (pos.x / NM, pos.y / NM)))
    assert gnd_code is not None, "no pads found for net"

    geoms = {l: [] for l in layers}
    bridges = []       # (centre, radius) vias / TH pads joining layers
    # zone fills, as saved
    for zone in board.Zones():
        if zone.GetNetCode() != gnd_code:
            continue
        for layer in layers:
            if zone.IsOnLayer(layer):
                ps = zone.GetFilledPolysList(layer)
                geoms[layer].extend(polys_from_set(ps))
    # tracks and vias
    for t in board.GetTracks():
        if t.GetNetCode() != gnd_code:
            continue
        if t.Type() == pcbnew.PCB_VIA_T:
            pos = t.GetPosition()
            c = (pos.x / NM, pos.y / NM)
            for layer in layers:
                if t.IsOnLayer(layer):
                    r = t.GetWidth(layer) / NM / 2.0
                    geoms[layer].append(Point(c).buffer(r, resolution=48))
            bridges.append(c)
        else:
            s, e = t.GetStart(), t.GetEnd()
            ls = LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)])
            w = t.GetWidth() / NM
            for layer in layers:
                if t.IsOnLayer(layer):
                    geoms[layer].append(ls.buffer(w / 2.0, cap_style=1, resolution=16))
    # TH pads bridge layers too
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == net and pad.GetAttribute() == pcbnew.PAD_ATTRIB_PTH:
                pos = pad.GetPosition()
                bridges.append((pos.x / NM, pos.y / NM))
    for (ref, num, layer, g, c) in pads:
        geoms[layer].append(g)

    dil = dilate_um / 1000.0
    comps = {}   # layer -> list of polygons (components)
    for layer in layers:
        u = unary_union([g.buffer(dil) if dil else g for g in geoms[layer]])
        if u.is_empty:
            comps[layer] = []
        elif isinstance(u, MultiPolygon):
            comps[layer] = list(u.geoms)
        else:
            comps[layer] = [u]

    # union-find over (layer, idx)
    parent = {}
    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a
    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb
    for layer in layers:
        for i in range(len(comps[layer])):
            parent[(layer, i)] = (layer, i)
    for (bx, by) in bridges:
        hit = []
        for layer in layers:
            for i, poly in enumerate(comps[layer]):
                if poly.contains(Point(bx, by)) or poly.distance(Point(bx, by)) < 1e-9:
                    hit.append((layer, i))
        for h in hit[1:]:
            union(hit[0], h)

    def comp_of(layer, geom):
        for i, poly in enumerate(comps[layer]):
            if poly.intersects(geom):
                return find((layer, i))
        return None

    jw = [comp_of(l, g) for (r, n, l, g, c) in pads if r == root_ref]
    jw = [x for x in jw if x is not None]
    assert jw, "root pads not found in any component"
    root = jw[0]
    assert all(x == root for x in jw), "root pads are split!"

    total, on, off = 0, 0, []
    seen = set()
    for (ref, num, layer, g, c) in pads:
        key = (ref, num)
        r = comp_of(layer, g)
        if key in seen:
            continue
        seen.add(key)
        total += 1
        if r == root:
            on += 1
        else:
            off.append({"pad": f"{ref}.{num}", "centre": [round(c[0], 6), round(c[1], 6)]})
    return {"board": os.path.basename(board_path), "total_pads": total,
            "on_return": on, "off_return": sorted(off, key=lambda d: d["pad"])}

if __name__ == "__main__":
    dil = 0.0
    args = sys.argv[1:]
    if "--dilate-um" in args:
        i = args.index("--dilate-um")
        dil = float(args[i + 1])
        del args[i:i + 2]
    net = args[1] if len(args) > 1 else "GND"
    root_ref = args[2] if len(args) > 2 else "J_WING"
    res = board_gnd(args[0], dil, net, root_ref)
    res["net"] = net
    print(json.dumps(res, indent=1))
    sys.exit(0 if not res["off_return"] else 1)
