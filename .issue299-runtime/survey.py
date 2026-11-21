#!/usr/bin/env python3
"""Survey each off-return GND island: seal geometry, gaps, F.Cu occupancy."""
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

def other_net_geoms(board, layer, keep_nets=None):
    """(netname, kind, geom, desc) for non-GND copper on layer."""
    out = []
    for t in board.GetTracks():
        if t.GetNetname() == "GND":
            continue
        if not t.IsOnLayer(layer):
            continue
        if t.Type() == pcbnet_via():
            pos = t.GetPosition()
            g = Point(pos.x / NM, pos.y / NM).buffer(t.GetWidth(layer) / NM / 2.0, resolution=32)
            out.append((t.GetNetname(), "via", g, f"via @({pos.x/NM:.3f},{pos.y/NM:.3f})"))
        else:
            s, e = t.GetStart(), t.GetEnd()
            g = LineString([(s.x / NM, s.y / NM), (e.x / NM, e.y / NM)]).buffer(t.GetWidth() / NM / 2.0, cap_style=1, resolution=8)
            out.append((t.GetNetname(), "track", g,
                        f"track ({s.x/NM:.2f},{s.y/NM:.2f})->({e.x/NM:.2f},{e.y/NM:.2f}) w={t.GetWidth()/NM:.2f}"))
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() in ("GND", ""):
                continue
            if not pad.IsOnLayer(layer):
                continue
            g = gc.pad_geom(pad, layer)
            pos = pad.GetPosition()
            out.append((pad.GetNetname(), "pad", g,
                        f"pad {fp.GetReference()}.{pad.GetNumber()} @({pos.x/NM:.3f},{pos.y/NM:.3f})"))
    return out

def pcbnet_via():
    return pcbnew.PCB_VIA_T

def survey(path):
    board = pcbnew.LoadBoard(path)
    res = gc.board_gnd(path)
    off = {o["pad"]: tuple(o["centre"]) for o in res["off_return"]}
    print(f"### {os.path.basename(path)}  on-return {res['on_return']}/{res['total_gnd_pads']}")
    if not off:
        return
    # rebuild components the same way gndcheck does, but keep them accessible:
    # simpler: recompute per-layer GND unions and identify island polys by pad membership
    layers = [pcbnew.F_Cu, pcbnew.B_Cu]
    lname = {pcbnew.F_Cu: "F.Cu", pcbnew.B_Cu: "B.Cu"}
    gnd_code = None
    padmap = {}
    for fp in board.GetFootprints():
        for pad in fp.Pads():
            if pad.GetNetname() == "GND":
                gnd_code = pad.GetNetCode()
                padmap[f"{fp.GetReference()}.{pad.GetNumber()}"] = pad
    geoms = {l: [] for l in layers}
    for zone in board.Zones():
        if zone.GetNetCode() != gnd_code:
            continue
        for l in layers:
            if zone.IsOnLayer(l):
                geoms[l].extend(gc.polys_from_set(zone.GetFilledPolysList(l)))
    unions = {}
    for l in layers:
        unions[l] = unary_union(geoms[l]) if geoms[l] else None
    # main return component on B.Cu = the union member containing a J_WING pad
    jw = padmap["J_WING.2"] if "J_WING.2" in padmap else None
    jw_pt = None
    for fp in board.GetFootprints():
        if fp.GetReference() == "J_WING":
            for pad in fp.Pads():
                if pad.GetNetname() == "GND":
                    pos = pad.GetPosition()
                    jw_pt = Point(pos.x / NM, pos.y / NM)
                    break
            break
    main_b = None
    u = unions[pcbnew.B_Cu]
    polys_b = list(u.geoms) if u and u.geom_type == "MultiPolygon" else ([u] if u else [])
    for p in polys_b:
        if p.contains(jw_pt) or p.intersects(jw_pt):
            main_b = p
    print(f"B.Cu GND union members: {len(polys_b)}; main pour area={main_b.area:.1f} mm2" if main_b else "no main")
    others_b = other_net_geoms(board, pcbnew.B_Cu)
    others_f = other_net_geoms(board, pcbnew.F_Cu)
    gnd_vias = []
    for t in board.GetTracks():
        if t.GetNetname() == "GND" and t.Type() == pcbnew.PCB_VIA_T:
            pos = t.GetPosition()
            gnd_vias.append((pos.x / NM, pos.y / NM))
    done = set()
    for name, centre in sorted(off.items()):
        pt = Point(centre)
        isl = None
        for p in polys_b:
            if p.intersects(pt):
                isl = p
        if isl is None or id(isl) in done:
            continue
        done.add(id(isl))
        members = [n for n, c in off.items() if isl.intersects(Point(c))]
        d_main = isl.distance(main_b)
        a, b = nearest_points(isl, main_b)
        print(f"\n-- island {members} area={isl.area:.3f} mm2 bbox={tuple(round(v,2) for v in isl.bounds)}")
        print(f"   dist to main pour: {d_main:.3f} mm; closest {a} -> {b}")
        near = []
        for net, kind, g, desc in others_b:
            d = isl.distance(g)
            if d < 1.2:
                near.append((round(d, 3), net, desc))
        for d, net, desc in sorted(near)[:10]:
            print(f"   B.Cu near {d:6.3f}  [{net}] {desc}")
        # corridor: segment between closest points, widened 0.35 each side
        seg = LineString([a, b]).buffer(0.35, cap_style=2)
        blockers = []
        for net, kind, g, desc in others_f:
            if seg.intersects(g):
                blockers.append((net, desc))
        print(f"   F.Cu blockers over B.Cu bridge corridor (+/-0.35mm): {blockers if blockers else 'NONE'}")
        gv = [(round(x, 2), round(y, 2)) for (x, y) in gnd_vias if isl.distance(Point(x, y)) < 1.0]
        print(f"   GND vias within 1mm of island: {gv if gv else 'none'}")

if __name__ == "__main__":
    survey(sys.argv[1])
